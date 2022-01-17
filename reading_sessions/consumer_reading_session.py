from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import StopConsumer
import json
from django.utils import timezone
import asyncio
from django.db.models import Q

from users.models import CustomUser, Role, User_View
from buddy_program_data.models import Room, Program_Semester, Daily_Session
from matches.models import Temporary_Match, Match_Type, Match_Note
from matches.models import Scheduled_Match
from reading_sessions.models import Redirect
from reading_sessions.models import Help_Request
from reading_sessions.models import Reading_Session_Error
from reading_sessions.models import User_Session_Status
from reading_sessions.models import Match_Session_Status
from reading_sessions.models import Room_Participants
from reading_sessions.serializers import LazyUserSessionStatusEncoder
from reading_sessions.serializers import LazyRoomParticipantsEncoder
from reading_sessions.serializers import LazyRedirectEncoder, LazyHelpEncoder
from reading_sessions.serializers import RedirectSerializer, TemporaryMatchSerializer
from reading_sessions.serializers import LazyMatchStatusEncoder
from private_chat.consumer_private_chat import get_private_room_or_error
from private_chat.consumer_private_chat import private_connect_user
from private_chat.consumer_private_chat import private_get_connected_users
from private_chat.consumer_private_chat import create_private_chat_room_message
from private_chat.consumer_private_chat import append_unread_msg_if_not_connected
from private_chat.consumer_private_chat import to_user_unread_count
from private_chat.consumer_private_chat import unread_private_msg_by_user
from private_chat.consumer_private_chat import private_disconnect_user
from private_chat.consumer_private_chat import get_private_rooms_for_user

class ReadingSessionConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\nReadingSessionConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'status'
		await self.channel_layer.group_add(
			self.socket_group_name,
			self.channel_name,		
		)
		await self.accept()



	async def websocket_disconnect(self, message):
		"""
		Called when a WebSocket connection is closed. Base level so you don't
		need to call super() all the time.
		"""
		print("\n*******************ReadingSessionConsumer: disconnect", timezone.now())

		try:
			print("\n\nDisconnecting ReadingSessionConsumer", str(self.scope["user"]))
			user, room, status, count = await set_user_offline(self.scope["user"], self.user, self.room)
			await self.leave_meeting_room(status, room, count)
			await self.get_and_send_redirects(user)
			await self.send_session_status(user)


		
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_reading_session.py"
			socket_info['function_name']="websocket_disconnect"
			socket_info['location_in_function']="try block websocket_disconnect"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)

		try:
			for group in self.groups:
				await self.channel_layer.group_discard(group, self.channel_name)
		except AttributeError:
			raise InvalidChannelLayerError(
				"BACKEND is unconfigured or doesn't support groups"
				)

		await self.disconnect(message["code"])
		raise StopConsumer()

	async def disconnect(self, code):
		"""
		Called when a WebSocket connection is closed.
		"""
		pass


	async def receive_json(self, content):
		command = content.get("command", None)
		print("\n***** ReadingSessionConsumer: receive_json: " + str(self.scope["user"]))

		if command =="join":
			user, room, status, count, redirect= await set_user_online(self.scope["user"], content)
			self.user = user
			self.room = room
			await self.join_meeting_room(status, room, count)
			if redirect:
				await self.get_and_send_redirects(user)
			else:
				print("No Redirects")

			await self.send_session_status(user)


		elif command == "create_redirects":
			manual_redirects, manual_redirect_count, not_auto_send_count = await create_redirects(content)
			await self.send_redirects(manual_redirects, manual_redirect_count, not_auto_send_count)

		elif command == "create_temp_match":				
			temp_match, redirect = await create_temp_match(self.user, content)
			await self.send_new_match_redirect(temp_match, redirect)

		elif command =="delete_redirect":
			await delete_redirect(content)
			await self.get_and_send_redirects(self.user)

		elif command =="redirect_autosend":
			await change_to_autosend_redirect(content)
			await self.get_and_send_redirects(self.user)

		elif command == "notify_all":
			print("notify_all", content)
			if len(content["message"].lstrip()) != 0:
				await self.send_to_all_rooms(content)

		elif command == "create_send_private_message":
			print("******ReadingSession create_send_private_message", content)
			private_chat_room = await get_private_room_or_error(content['room_id'], self.scope["user"])
			# print(private_chat_room)
			await private_connect_user(private_chat_room, self.scope["user"])
			private_room_id = private_chat_room.id
			if len(content["pvt_message"].lstrip()) == 0:
				raise ClientError(422,"You can't send an empty message.")
			await self.send_room_join_send_leave(private_chat_room, self.scope["user"], content)
			await private_disconnect_user(private_chat_room, self.scope["user"])

		elif command == "get_private_rooms":
			print("\n\n****ReadingSession GETTING private_room_list", content)
			pvt_rooms, pvt_room_count = await get_private_rooms_for_user(content['user_id'])
			unread_count_for_user = await to_user_unread_count(content['user_id'])
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "private_room_list",
					"for_user": content['user_id'],
					"pvt_rooms": pvt_rooms,
					"pvt_room_count": pvt_room_count,
					"unread_count_for_user": unread_count_for_user,
				}
			)

		elif command == "get_private_messages":
			print("\n\n****Reading Session GETTING Private Messages", content)
			user_private_unread = await to_user_unread_count(content['user_id'])
			unread_by_user = await unread_private_msg_by_user(content['user_id'])
			pvt_rooms, pvt_room_count = await get_private_rooms_for_user(content['user_id'])
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "unread_private_messages",
					"for_user": content['user_id'],
					"pvt_unread_count": user_private_unread,
					"unread_by_room_total": unread_by_user,
					"pvt_rooms": pvt_rooms,
					"pvt_room_count": pvt_room_count,
				}
			)

	async def private_room_list(self, event):
		await self.send_json(
			{
				"msg_type": "private_room_list",
				"for_user": event["for_user"],
				"pvt_rooms": event["pvt_rooms"],
				"pvt_room_count": event["pvt_room_count"],
				"unread_count_for_user": event["unread_count_for_user"],
			},
		)

	async def unread_private_messages(self, event):
		await self.send_json(
			{
				"msg_type": "unread_private_messages",
				"for_user": event["for_user"],
				"pvt_unread_count": event["pvt_unread_count"],
				"unread_by_room_total": event["unread_by_room_total"],
				"pvt_rooms": event["pvt_rooms"],
				"pvt_room_count": event["pvt_room_count"],
			},
		)

	async def send_to_all_rooms(self, content):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'notify_all',
				"from": content['user_id'],
				'message': content['message'],
				"to_group": content['to_group']
			}
		)

	async def notify_all(self, event):
		await self.send_json(
			{
				"msg_type": "notify_all",
				"from": event['from'],
				'message': event['message'],
				"to_group": event['to_group'],
			},
		)


	async def send_session_status(self, user):
		data = await session_stats(user)
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'staff_session_stats',
				"stats": data,
			}
		)

	async def staff_session_stats(self, event):		
		await self.send_json(
			{
				"msg_type": "session_stats",
				"stats": event["stats"],
			},
		)


	async def send_new_match_redirect(self, temp_match, redirect):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'new_temp_match',
				"temp_match": temp_match,
				"redirect": redirect,
			}
		)

	async def new_temp_match(self, event):		
		await self.send_json(
			{
				"msg_type": "temp_match_redirect",
				"temp_match": event["temp_match"],
				"redirect": event["redirect"],

			},
		)


	async def help_requests(self, event):
		print("here help_requests")
		all_help_requests, help_count = await get_all_help_requests(event["username"])
		await self.send_json(
			{
				"msg_type": "help_requests",
				"all_help_requests": all_help_requests,
				"help_count": help_count
			},
		)

	async def get_and_send_redirects(self, user):
		manual_redirects, manual_redirect_count, not_auto_send_count = await get_redirects(user)
		await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "redirect_users",
					"manual_redirects": manual_redirects,
					"manual_redirect_count": manual_redirect_count,
					"not_auto_send_count": not_auto_send_count,
				}
			)


	async def send_redirects(self, manual_redirects, manual_redirect_count, not_auto_send_count):
		await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "redirect_users",
					"manual_redirects": manual_redirects,
					"manual_redirect_count": manual_redirect_count,
					"not_auto_send_count": not_auto_send_count,
				}
			)

	async def redirect_users(self, event):
		await self.send_json(
			{
				"msg_type": "manual_redirects",
				"manual_redirects": event["manual_redirects"],
				"manual_redirect_count": event["manual_redirect_count"],
				"not_auto_send_count": event["not_auto_send_count"],
			},
		)

	async def join_meeting_room(self, status, room, count):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_joining',
				"username": self.scope["user"].username,
				"status": status,
				"room_name": room.name,
				"room_id": room.id,
				"ws_count": count,
			}
		)

	async def member_joining(self, event):		
		await self.send_json(
			{
				"msg_type": "member_joining",
				"username": event["username"],
				"status": event["status"],
				"room_name": event["room_name"],
				"room_id": event["room_id"],
				"ws_count": event["ws_count"],
			},
		)


	async def leave_meeting_room(self, status, room, count):
		print("Disconnecting Status leave_meeting_room", str(self.scope["user"]))
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_left',
				"username": self.scope["user"].username,
				"status": status,
				"room_name": room.name,
				"room_id": room.id,
				"ws_count": count,
			}
		)

	async def member_left(self, event):		
		await self.send_json(
			{
				"msg_type": "member_left",			
				"username": event["username"],
				"status": event["status"],
				"room_name": event["room_name"],
				"room_id": event["room_id"],
				"ws_count": event["ws_count"],
			},
		)

	async def send_room_join_send_leave(self, room, user, content):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# print("Match: Private Message send_room_join_send_leave")

		# get list of connected_users
		connected_users, user1, user2 = await private_get_connected_users(room)

		message = await create_private_chat_room_message(room, self.scope["user"], content)

		# Execute these functions asychronously
		await asyncio.gather(*[
			append_unread_msg_if_not_connected(self.scope["user"], room, user1, connected_users, message), 
			append_unread_msg_if_not_connected(self.scope["user"], room, user2, connected_users, message),

		])

		to_user_private_unread = await to_user_unread_count(content['to_user'])
		unread_by_user = await unread_private_msg_by_user(content['to_user'])
		print("***********to_user_private_unread", to_user_private_unread)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				"type": "private_message",
				"private_room_id": room.id,
				"to_user": message.to_user.id,
				"total_unread": to_user_private_unread,
				"unread_by_room_total": unread_by_user,
			}
		)

	async def private_message(self, event):
		await self.send_json(
			{
				"msg_type": "new_private_message",
				"in_private_room_id": event["private_room_id"],
				"to_user": event["to_user"],
				"total_unread": event["total_unread"],
				"unread_by_room_total": event["unread_by_room_total"],
			},
		)

def db_create_log_of_error(socket_info):
	try:
		Reading_Session_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN db_create_log_of_error")


def localtime_now_date():
	date_now = timezone.localtime(timezone.now()).date()
	return date_now

def user_match_status(user):
	try:
		student_role = Role.objects.get(name="Student")
		reader_role = Role.objects.get(name="Reader")
		if reader_role in user.roles.all():
			match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|
											Q(sch_match__reader=user)|
											Q(temp_match__student=user)|
											Q(temp_match__reader=user)
											)


		elif student_role in user.roles.all():
			if user.session_status.active_scheduled_match:
				sch_match = user.session_status.active_scheduled_match
			else:
				sch_match = None

			if user.session_status.temp_match:
				temp_match = user.session_status.temp_match
			else:
				temp_match = None

			if sch_match and temp_match:
				print("Sch and Temp")
				reader_temp = temp_match.reader
				reader_sch = sch_match.reader
				student = user
				print("Student", student)
				print("reader_temp", reader_temp)
				print("reader_sch", reader_sch)
				match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|											
											Q(temp_match__student=user)|
											Q(sch_match__reader=reader_sch)|
											Q(sch_match__reader=reader_temp)|
											Q(temp_match__reader=reader_sch)|
											Q(temp_match__reader=reader_temp)							
											
											)
			elif sch_match and not temp_match:
				print("Sch and No Temp")
				reader_sch = sch_match.reader
				match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|											
											Q(temp_match__student=user)|
											Q(sch_match__reader=reader_sch)|
											Q(temp_match__reader=reader_sch)
											)

			elif not sch_match and temp_match:
				print("No Sch and Temp")
				reader_temp = temp_match.reader
				match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|											
											Q(temp_match__student=user)|
											Q(sch_match__reader=reader_temp)|
											Q(temp_match__reader=reader_temp)
											)

			else:
				print("No Sch and No Temp")
				match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|											
											Q(temp_match__student=user)
											)



		else:
			match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__student=user)|
											Q(sch_match__reader=user)|
											Q(temp_match__student=user)|
											Q(temp_match__reader=user)
											)

		print("MATCH STATUS FOR USER", user, match_statuses)
		for status in match_statuses:
			print("status id", status.id)
	except Exception as e:
		print("BROKEN user_match_status", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="user_match_status"
		socket_info['location_in_function']="try block user_match_status"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)	

	return match_statuses


@database_sync_to_async
def session_stats(user):
	data = ""
	payload = {}
	try:
		student_role = Role.objects.get(name="Student")
		unmatched_students = CustomUser.objects.filter(roles__in=[student_role,],
										 session_status__needs_session_match=True)
		payload['unmatched_students'] = unmatched_students.count()

		reader_role = Role.objects.get(name="Reader")
		unmatched_readers = CustomUser.objects.filter(roles__in=[reader_role,],
										 session_status__needs_session_match=True)
		payload['unmatched_readers'] = unmatched_readers.count()

		try:
			match_statuses = user_match_status(user)
			s=LazyMatchStatusEncoder()
			payload['match_statuses'] = s.serialize(match_statuses) 
		except Exception as e:
			print("\n\n\n\n*** Match STATUS Exception HERE", e)
			socket_info={}
			socket_info['file']="consumer_reading_session.py"
			socket_info['function_name']="match_statuses"
			socket_info['location_in_function']="try block match_statuses"
			socket_info['occurred_for_user']=str(user)
			socket_info['error_text']=str(e)
			db_create_log_of_error(socket_info)



		data = json.dumps(payload)
	except Exception as e:
		print("BROKEN session_stats", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="session_stats"
		socket_info['location_in_function']="try block session_stats"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

	return data


@database_sync_to_async
def change_to_autosend_redirect(content):
	try:
		user = CustomUser.objects.get(id=content['user_id'])
		redirect = Redirect.objects.get(id=content['redirect_id'])
		redirect.auto_send = True
		redirect.save()		

	except Exception as e:
		print("BROKEN change_to_autosend_redirect", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="change_to_autosend_redirect"
		socket_info['location_in_function']="try block change_to_autosend_redirect"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

@database_sync_to_async
def delete_redirect(content):
	try:
		user = CustomUser.objects.get(id=content['user_id'])
		redirect = Redirect.objects.get(id=content['redirect_id'])
		redirect.delete()
		

	except Exception as e:
		print("BROKEN delete_redirect", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="delete_redirect"
		socket_info['location_in_function']="try block delete_redirect"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

@database_sync_to_async
def create_temp_match(user, content):
	temp_match_data = {}
	redirect_data = {}
	try:

		temp_match, redirect = Temporary_Match.create_temporary_match(content)
		redirect_data = RedirectSerializer(instance=redirect).data
		temp_match_data = TemporaryMatchSerializer(instance=temp_match).data

		# semester = Program_Semester.objects.get(active_semester = True)
		# match_type = Match_Type.objects.get(name="Temporary - In Session")
		# student = CustomUser.objects.get(id=content['student_id'])
		# reader = CustomUser.objects.get(id=content['reader_id'])
		# session = Daily_Session.objects.get(id=content['session_id'])
		# sent_by = CustomUser.objects.get(id=content['sent_by'])
		# student_previous_temps =Temporary_Match.objects.filter(session=session, student=student)
		# for item in student_previous_temps:
		# 	item.active = False
		# 	item.save()
		# 	old_temp_note_stu = Match_Note.objects.create(
		# 											match_type=match_type,
		# 											name="Temporary Match Inactive",
		# 											content="Student Has New Temp Match",
		# 											created_user = sent_by)
		# 	item.notes.add(old_temp_note_stu)
		# reader_previous_temps = Temporary_Match.objects.filter(session=session, reader=reader)
		# for item in reader_previous_temps:
		# 	item.active = False
		# 	item.save()
		# 	old_temp_note_reader = Match_Note.objects.create(
		# 											match_type=match_type,
		# 											name="Temporary Match Inactive",
		# 											content="Reader Has New Temp Match",
		# 											created_user = sent_by)
		# 	item.notes.add(old_temp_note_reader)

		# temp_match = Temporary_Match.objects.create(
		# 				semester = semester,
		# 				match_type = match_type,
		# 				student = student,
		# 				reader=reader,
		# 				session=session,
		# 				active=True,
		# 			)
		# temp_note_note = Match_Note.objects.create(
		# 								match_type=match_type,
		# 								name="Temporary Match Created",
		# 								created_user = sent_by)

		# temp_match.notes.add(temp_note_note)

		# if Scheduled_Match.objects.filter(student=student, active=True).exists():
		# 	student_scheduled_match = Scheduled_Match.objects.get(student=student, active=True)
		# 	student_scheduled_match.add_note_temporary_match_created(sent_by, temp_match)

		# if Scheduled_Match.objects.filter(reader=reader, active=True).exists():
		# 	reader_matches = Scheduled_Match.objects.filter(reader=reader, active=True)
		# 	for match in reader_matches:
		# 		if session in match.sessions_scheduled.all():
		# 			match.add_note_temporary_match_created(sent_by, temp_match)
		
		# redirect, created = Redirect.objects.get_or_create(
		# 							user_to_redirect = student,
		# 							)
		# redirect.to_user = reader
		# redirect.auto_send= True
		# redirect.to_room=reader.session_status.room
		# redirect.save()



		# temp_match.set_student_info()
		# temp_match.set_reader_info()
		

	except Exception as e:
		print("BROKEN create_temp_match", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="create_temp_match"
		socket_info['location_in_function']="try block create_temp_match"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

	return temp_match_data, redirect_data

@database_sync_to_async
def get_all_help_requests(user):
	try:
		all_helps = Help_Request.objects.filter(done=False)
		count= all_helps.count()
		
		payload = {}
		s = LazyHelpEncoder()
		payload['help_requests'] = s.serialize(all_helps)
		data = json.dumps(payload)
		

	except Exception as e:
		print("BROKEN CREATE Help Request", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="get_all_help_requests"
		socket_info['location_in_function']="try block get_all_help_requests"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

	return data, count

@database_sync_to_async
def set_user_online(ini_user, content):
	redirect = None
	try:
		print("\n\n\n\n\nset_user_online", ini_user.id, type(ini_user), content)
		user_id = content['user_id']
		room_id = content['room_id']
		user = CustomUser.objects.get(id=user_id)
		room = Room.objects.get(id=room_id)
		redirect = room.participants.join_room(user)
		print("\n\n\n\n After JOIN ROOM")
		session_status = User_Session_Status.objects.get(user=user)
		participants, created = Room_Participants.objects.get_or_create(room=room)
		try:
			statuses=[]
			statuses.append(session_status)
			initial_data={}
			payload = {}
			s = LazyUserSessionStatusEncoder()
			initial_data['session_status'] = s.serialize(statuses)
			payload['session_status'] = initial_data['session_status'][0]
			payload['room_ws_count'] = participants.ws_count
			payload['jitsi_ws_count'] = participants.jitsi_count
		except Exception as e:
			print("Exception serialize", e)


		
		
		data = json.dumps(payload)

		online_count = CustomUser.objects.filter(session_status__online_ws=True).count()

	except Exception as e:
		print("BROKEN set_user_online", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="set_user_online"
		socket_info['location_in_function']="try block set_user_online"
		socket_info['occurred_for_user']=str(ini_user)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)

	return user, room, data, online_count, redirect


@database_sync_to_async
def set_user_offline(lazy_user, user_ini, room_ini):
	try:
		print("\n\n\n\n\nset_user_offline", lazy_user, user_ini, room_ini)
		user = CustomUser.objects.get(id=user_ini.id)
		room = Room.objects.get(id=room_ini.id)
		room.participants.leave_room(user)
		session_status = User_Session_Status.objects.get(user=user)
		participants, created = Room_Participants.objects.get_or_create(room=room)

		



		statuses=[]
		statuses.append(session_status)

		initial_data={}
		payload = {}
		s = LazyUserSessionStatusEncoder()
		initial_data['session_status'] = s.serialize(statuses)
		payload['session_status'] = initial_data['session_status'][0]
		payload['room_ws_count'] = participants.ws_count
		payload['jitsi_ws_count'] = participants.jitsi_count
		data = json.dumps(payload)
		online_count = CustomUser.objects.filter(session_status__online_ws=True).count()
		print("online_count", online_count)
	except Exception as e:
		print("BROKEN set_user_offline", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="set_user_offline"
		socket_info['location_in_function']="try block set_user_offline"
		socket_info['occurred_for_user']=str(user_ini)
		socket_info['error_text']=str(e)
		db_create_log_of_error(socket_info)
	
	return user, room, data, online_count	

@database_sync_to_async
def get_redirects(user):
	try:
		# all_redirects_to_send = Redirect.objects.filter(auto_send=True)
		all_redirects_to_send = Redirect.objects.all()
		print('all_redirects_to_send', all_redirects_to_send)
		count = len(all_redirects_to_send)
		not_auto_send_count = Redirect.objects.filter(auto_send=False).count()
		payload = {}
		s = LazyRedirectEncoder()
		payload['manual_redirects'] = s.serialize(all_redirects_to_send)

		data = json.dumps(payload)	


	except Exception as e:
		print("BROKEN get_redirects", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="get_redirects"
		socket_info['location_in_function']="try block get_redirects"
		socket_info['occurred_for_user']=str(user)
		socket_info['error_text']=str(e)

		db_create_log_of_error(socket_info)
	return data, count, not_auto_send_count


@database_sync_to_async
def create_redirects(content):
	try:
		print(content)
		room = Room.objects.get(id=content['to_room']);
		created_by = CustomUser.objects.get(id=content['created_by']);
		all_redirects_to_send = []
		for item in content['users_to_send']:
			user_to_send = CustomUser.objects.get(id=item)
			redirect, created = Redirect.objects.get_or_create(
								user_to_redirect=user_to_send,
								)
			redirect.auto_send= True
			redirect.created_by=created_by
			redirect.to_room=room
			redirect.save()
			all_redirects_to_send.append(redirect)	

		count = len(all_redirects_to_send)
		not_auto_send_count = Redirect.objects.filter(auto_send=False).count()
		payload = {}
		s = LazyRedirectEncoder()
		payload['manual_redirects'] = s.serialize(all_redirects_to_send)

		data = json.dumps(payload)	


	except Exception as e:
		print("BROKEN create_redirects", e)
		socket_info={}
		socket_info['file']="consumer_reading_session.py"
		socket_info['function_name']="create_redirects"
		socket_info['location_in_function']="try block create_redirects"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)

		db_create_log_of_error(socket_info)
	return data, count, not_auto_send_count


@database_sync_to_async
def create_log_of_error(socket_info):
	try:
		Reading_Session_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN create_log_of_error")

