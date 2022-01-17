from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.utils import timezone
from django.core.paginator import Paginator

import json
import asyncio

from private_chat.models import PrivateChatMessage, PrivateChatRoom, UnreadPrivateChatMessages
from private_chat.models import Private_Chat_Error, User_Private_Room_List
from private_chat.private_chat_constants import *
from private_chat.exceptions import ClientError
from private_chat.utils import calculate_timestamp
from users.models import CustomUser
from private_chat.serializers import LazyCustomUserEncoder
from private_chat.serializers import LazyMeetingParticipantsEncoder
from private_chat.serializers import LazyPrivateRoomChatMessageEncoder
from private_chat.serializers import LazyPrivateRoomEncoder



class PrivateChatConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		# print("PRIVATE ChatConsumer: connect: " + str(self.scope["user"]))

		# let everyone connect. But limit read/write to authenticated users
		await self.accept()

		# the room_id will define what it means to be "connected". If it is not None, then the user is connected.
		self.room_id = None


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		# print("PRIVATEChatConsumer: receive_json", content)
		command = content.get("command", None)
		try:
			if command == "join":
				# print("joining room: " + str(content['room']))
				await self.join_room(content["room"])
			elif command == "leave":
				# print("Leaving", content)
				await self.leave_room(content["room"])
			elif command == "send":
				# print('CONTENT in send', content)
				if len(content["message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room(content)


			elif command == "join_send_leave":
				# print("JOIN SEND LEAVE", content)
				self.room = await get_room_or_error(content['room_id'], self.scope["user"])
				# print(self.room)
				await connect_user(self.room, self.scope["user"])
				self.room_id = self.room.id
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_join_send_leave(self.room, self.scope["user"], content)
				await disconnect_user(self.room, self.scope["user"])

					

			elif command == "create_message":
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_not_connected(content)

			elif command == "get_room_chat_messages":
				print("\n\n\n\n\n*************Lets get the new messages")
				await self.display_progress_bar(True)
				print("** content['room_id']", content['room_id'])
				print("** self.scope[user]", self.scope["user"])
				print("** content['page_number'])", content['page_number'])
				room = await get_room_or_error(content['room_id'], self.scope["user"])
				print("** Room", room)
				try:
					payload = await get_room_chat_messages(room, content['page_number'])
					print("** payload", payload)

					if payload != None:
						payload = json.loads(payload)
						await self.send_messages_payload(payload['messages'], payload['new_page_number'])
					else:
						raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
					await self.display_progress_bar(False)
				except Exception as e:
					print("Exception get_room_chat_messages", e)

				


			elif command == "get_user_info":
				await self.display_progress_bar(True)
				room = await get_room_or_error(content['room_id'], self.scope["user"])
				payload = await get_user_info(room, self.scope["user"])
				if payload != None:
					payload = json.loads(payload)
					await self.send_user_info_payload(payload['user_info'])
				else:
					raise ClientError(204, "Something went wrong retrieving the other users account details.")
				await self.display_progress_bar(False)




			elif command == "create_send_private_message":
				print("******Private create_send_private_message", content)

				private_chat_room = await get_private_room_or_error(content['room_id'], self.scope["user"])
				# print(private_chat_room)
				await private_connect_user(private_chat_room, self.scope["user"])
				private_room_id = private_chat_room.id
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_join_send_leave(private_chat_room, self.scope["user"], content)
				await private_disconnect_user(private_chat_room, self.scope["user"])

			elif command == "get_private_rooms":
				print("\n\n**** IN PRIVATE CHAT GETTING private_room_list", content)
				pvt_rooms, pvt_room_count, total_unread_private = await get_private_rooms_for_user(content['user_id'])
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
				# print("\n\n**** GETTING Private Messages", content)
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
		except ClientError as e:
			await self.handle_client_error(e)


	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# Leave the room
		# print("ChatConsumer: disconnect")
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception as e:
			print("EXCEPTION: disconnect" + str(e))
			pass


	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
		# print("ChatConsumer: join_room: " + str(room_id))
		try:
			room = await get_room_or_error(room_id, self.scope["user"])
			# print("\n\n\n Private Room", room)
		except ClientError as e:
			return await self.handle_client_error(e)

		# Add user to "users" list for room
		await connect_user(room, self.scope["user"])

		# Store that we're in the room
		self.room_id = room.id
		# print("Self.room_id", self.room_id)

		await on_user_connected(room, self.scope["user"])

		# Add them to the group so they get room messages
		await self.channel_layer.group_add(
			room.group_name,
			self.channel_name,
		)

		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(room.id),
		})

		if self.scope["user"].is_authenticated:
			# Notify the group that someone joined
			await self.channel_layer.group_send(
				room.group_name,
				{
					"type": "chat.join",
					"room_id": room_id,
					"username": self.scope["user"].username,
					"user_id": self.scope["user"].id,
					"user_full_name": self.scope["user"].full_name(),
					# "jitsi_room_name": self.scope["user"].user_location.room.name,
					# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
				}
			)

	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware
		# print("ChatConsumer: leave_room", room_id)

		room = await get_room_or_error(room_id, self.scope["user"])

		# Remove user from "connected_users" list
		await disconnect_user(room, self.scope["user"])

		# Notify the group that someone left
		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "chat.leave",
				"room_id": room_id,
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"user_full_name": self.scope["user"].full_name(),
				# "jitsi_room_name": self.scope["user"].user_location.room.name,
				# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
			}
		)

		# Remove that we're in the room
		self.room_id = None

		# Remove them from the group so they no longer get room messages
		await self.channel_layer.group_discard(
			room.group_name,
			self.channel_name,
		)
		# Instruct their client to finish closing the room
		await self.send_json({
			"leave": str(room.id),
		})



	async def send_room(self, content):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# print("ChatConsumer: send_room", content)
		# Check they are in this room
		if self.room_id != None:
			if str(content['room_id']) != str(self.room_id):
				print("CLIENT ERRROR 1")
				raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
		else:
			print("CLIENT ERRROR 2")
			raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

		# Get the room and send to the group about it
		room = await get_room_or_error(content['room_id'], self.scope["user"])

		# print("******room", room)

		connected_users, user1, user2 = await private_get_connected_users(room)

		message = await create_private_chat_room_message(room, self.scope["user"], content)

		# Execute these functions asychronously
		await asyncio.gather(*[
			append_unread_msg_if_not_connected(self.scope["user"], room, user1, connected_users, message), 
			append_unread_msg_if_not_connected(self.scope["user"], room, user2, connected_users, message),

		])

		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "chat.message",
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"user_full_name": self.scope["user"].full_name(),
				# "jitsi_room_name": self.scope["user"].user_location.room.name,
				# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
				"message": message.content,
				"room_id": content['room_id'],
				"to_user": content['to_user']
			}
		)


	# These helper methods are named by the types we send - so chat.join becomes chat_join
	async def chat_join(self, event):
		"""
		Called when someone has joined our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_join: " + str(self.scope["user"].id))
		if event["username"]:
			await self.send_json(
				{
					"msg_type": PRIVATE_MSG_TYPE_ENTER,
					"room": event["room_id"],
					"username": event["username"],
					"user_id": event["user_id"],
					"user_full_name": event["user_full_name"],
					# "jitsi_room_name": event["jitsi_room_name"],
					# "jitsi_room_slug": event["jitsi_room_slug"],
					"message": event["username"] + " connected.",
				},
			)

	async def chat_leave(self, event):
		"""
		Called when someone has left our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_leave")
		if event["username"]:
			await self.send_json(
			{
				"msg_type": PRIVATE_MSG_TYPE_LEAVE,
				"room": event["room_id"],
				"username": event["username"],
				"user_id": event["user_id"],
				"user_full_name": event["user_full_name"],
				# "jitsi_room_name": event["jitsi_room_name"],
				# "jitsi_room_slug": event["jitsi_room_slug"],
				"message": event["username"] + " disconnected.",
			},
		)


	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_message")

		timestamp = calculate_timestamp(timezone.now())

		await self.send_json(
			{
				"msg_type": PRIVATE_MSG_TYPE_MESSAGE,
				"username": event["username"],
				"user_id": event["user_id"],
				"user_full_name": event["user_full_name"],
				# "jitsi_room_name": event["jitsi_room_name"],
				# "jitsi_room_slug": event["jitsi_room_slug"],
				"message": event["message"],
				"natural_timestamp": timestamp,
				"to_user": event['to_user'],
			},
		)

	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		# print("ChatConsumer: send_messages_payload. ")

		await self.send_json(
			{
				"messages_payload": "messages_payload",
				"messages": messages,
				"new_page_number": new_page_number,
			},
		)

	async def send_user_info_payload(self, user_info):
		"""
		Send a payload of user information to the ui
		"""
		# print("ChatConsumer: send_user_info_payload. ")
		await self.send_json(
			{
				"user_info": user_info,
			},
		)

	async def display_progress_bar(self, is_displayed):
		"""
		1. is_displayed = True
		- Display the progress bar on UI
		2. is_displayed = False
		- Hide the progress bar on UI
		"""
		# print("DISPLAY PROGRESS BAR: " + str(is_displayed))
		await self.send_json(
			{
				"display_progress_bar": is_displayed
			}
		)


	async def handle_client_error(self, e):
		"""
		Called when a ClientError is raised.
		Sends error data to UI.
		"""
		errorData = {}
		errorData['error'] = e.code
		if e.message:
			errorData['message'] = e.message
			await self.send_json(errorData)
		return

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

@database_sync_to_async
def private_connect_user(room, user):
	# add user to connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.connect_user(user)


@database_sync_to_async
def private_disconnect_user(room, user):
	# remove from connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id, user):
	"""
	Tries to fetch a room for the user, checking permissions along the way.
	"""
	try:
		room = PrivateChatRoom.objects.get(pk=room_id)
		user1 = room.user1
		user2 = room.user2
		if user != user1 and user != user2:
			raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")
		# else:
		# 	print("Allowed")

	except Exception as e:
		print('Broken get_room_or_error', e)

	return room


# I don't think this requires @database_sync_to_async since we are just accessing a model field
# https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
@database_sync_to_async
def get_user_info(room, user):
	"""
	Retrieve the user info for the user you are chatting with
	"""
	try:
		# Determine who is who
		other_user = room.user1
		if other_user == user:
			other_user = room.user2

		payload = {}
		s = LazyCustomUserEncoder()
		# convert to list for serializer and select first entry (there will be only 1)
		payload['user_info'] = s.serialize([other_user])[0] 
		return json.dumps(payload)
	except ClientError as e:
		raise ClientError("DATA_ERROR", "Unable to get that users information.")
	return None


@database_sync_to_async
def create_room_chat_message(room, user, content):
	message = ""
	# print("create_room_chat_message")
	# print('room', room)
	# print('user', user)
	# print('content', content)
	to_user = CustomUser.objects.get(id=content['to_user'])

	message = PrivateChatMessage.objects.create(from_user= user,
											to_user=to_user,
											user=user,
											room=room,
											content=content['pvt_message'])
	return message


@database_sync_to_async
def get_room_chat_messages(room, page_number):
	# print("room, page_number", room, page_number)
	try:
		qs = PrivateChatMessage.objects.by_room(room)
		p = Paginator(qs, PRIVATE_DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)  
		if new_page_number <= p.num_pages:
			new_page_number = new_page_number + 1
			s = LazyPrivateRoomChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = "None"
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION get_room_chat_messages: " + str(e))
	return None


@database_sync_to_async
def connect_user(room, user):
	# add user to connected_users list
	user = CustomUser.objects.get(pk=user.id)
	# print("User", user)
	return room.connect_user(user)


@database_sync_to_async
def disconnect_user(room, user):
	# remove from connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.disconnect_user(user)


# When a user connects, reset their unread message count
@database_sync_to_async
def on_user_connected(room, user):
	print("On user connected", room, user)
	# confirm they are in the connected users list
	connected_users = room.connected_users.all()
	# print("connected_user", connected_users)
	if user in connected_users:
		# print("yes in connected users")
		try:
			# reset count
			unread_msgs = UnreadPrivateChatMessages.objects.get(room=room, user=user)
			old_unread_count = unread_msgs.count
			print("old_unread_count", old_unread_count)
			unread_msgs.count = 0
			unread_msgs.save()
			if User_Private_Room_List.objects.filter(user=user).exists():
				room_list = User_Private_Room_List.objects.get(user=user)
				print("ROOM LIST", room_list.total_unread_private)
				total_unread_private = room_list.total_unread_private 
				print("total_unread_private",total_unread_private)
				total_unread_private = total_unread_private - old_unread_count
				print("new total_unread_private",total_unread_private)
				room_list.total_unread_private = total_unread_private
				room_list.save()
				print("After ROOM LIST", room_list.total_unread_private)
			else:
				print("NO USER PRIVATE ROOM LIST")


			# print("unread_msgs count after", unread_msgs.count)
		except UnreadPrivateChatMessages.DoesNotExist:
			UnreadPrivateChatMessages(room=room, user=user).save()
			pass

	else:
		print("No not in connected users")
	return



@database_sync_to_async
def private_get_connected_users(room):
	try:
		connected_users = room.connected_users.all()
		user1 = room.user1
		user2 = room.user2		
		# print("count", count)	
	except:
		print("\n\n\nBROKEN get_connected_users")
		Private_Chat_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="private_get_connected_users",
						location_in_function="try block private_get_connected_users",
						occurred_for_user=room.name,
						error_text=str(e))
	return connected_users, user1, user2

@database_sync_to_async
def create_private_chat_room_message(room, user, content):
	try:
		message = ""
		# print("create_room_chat_message")
		# print('room', room)
		# print('user', user)
		# print('content', content)
		to_user = CustomUser.objects.get(id=content['to_user'])

		message = PrivateChatMessage.objects.create(from_user= user,
												to_user=to_user,
												user=user,
												room=room,
												content=content['pvt_message'])
	except Exception as e:
		Private_Chat_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_private_chat_room_message",
						location_in_function="try block create_private_chat_room_message",
						occurred_for_user=user.username,
						error_text=str(e))
	
	return message



@database_sync_to_async
def append_unread_msg_if_not_connected(sender, room, user, connected_users, message):
	try:
		if not user in connected_users: 
			try:
				print("Sender", sender, type(sender))
				full_name = sender.full_name()
				print("Full name", full_name)
				unread_msgs = UnreadPrivateChatMessages.objects.get(room=room, user=user)
				unread_msgs.most_recent_message = "New Message from " + full_name
				unread_msgs.last_message = message
				unread_msgs.count += 1
				unread_msgs.save()
				unread_msgs.unread_msgs.add(message)
				
			except UnreadPrivateChatMessages.DoesNotExist:
				print("UnreadPrivateChatMessages.DoesNotExist")
				UnreadPrivateChatMessages(room=room, user=user,
										count=1, most_recent_message=message.content,
										last_message=message).save()
				

			user.private_room_list.total_all_unread()
	except Exception as e:
		print("BROKEN append_unread_msg_if_not_connected", e)
		Private_Chat_Error.objects.create(file="consumer_private_chat.py",
						function_name="append_unread_msg_if_not_connected",
						location_in_function="try block append_unread_msg_if_not_connected",
						occurred_for_user=user.username,
						error_text=str(e))
	
	return

@database_sync_to_async
def get_private_room_or_error(room_id, user):
	try:
		room = PrivateChatRoom.objects.get(pk=room_id)
		user1 = room.user1
		user2 = room.user2
		if user != user1 and user != user2:
			raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")
		# else:
		# 	print("Allowed")

	except Exception as e:
		print("BROKEN get_private_room_or_error", e)
		Private_Chat_Error.objects.create(file="consumer_private_chat.py",
						function_name="get_private_room_or_error",
						location_in_function="try block for get_private_room_or_error",
						occurred_for_user=user.username,
						error_text=str(e))

	return room



@database_sync_to_async
def get_private_rooms_for_user(user_id):

	print("GETTING PRIVATE ROOMS FOR USER PRIVATE CHAT")
	data = ""
	count = ""
	try:
		user = CustomUser.objects.get(id=user_id)
		# print("***********get_private_rooms_for_user")
		if not User_Private_Room_List.objects.filter(user=user).exists():
			pvt_list = User_Private_Room_List.objects.create(user=user)
	

		list_rooms = user.private_room_list.private_rooms.all().order_by('-last_use')
		count = list_rooms.count()
		# print("list_rooms", list_rooms)
		# print("count", count)

		payload = {}
		s = LazyPrivateRoomEncoder()
		payload['private_rooms'] = s.serialize(list_rooms)
		data = json.dumps(payload)


	except Exception as e:
		print("BROKEN get_private_rooms_for_user", e)
		Private_Chat_Error.objects.create(file="consumer_private_chat.py",
						function_name="get_private_rooms_for_user",
						location_in_function="try block for get_private_rooms_for_user",
						occurred_for_user=user.username,
						error_text=str(e))
	# return unique_senders_data, message_data, count
	return data, count

@database_sync_to_async
def to_user_unread_count(user_id):
	user = CustomUser.objects.get(id=user_id)
	try:
		user = CustomUser.objects.get(id=user_id)
		if not User_Private_Room_List.objects.filter(user=user).exists():
			pvt_list = User_Private_Room_List.objects.create(user=user)

		private_unread_count = user.private_room_list.total_unread_private
		# print(private_unread_count)
	except Exception as e:
		print("Broken to_user_unread_count", e)
		Private_Chat_Error.objects.create(file="consumer_private_chat.py",
						function_name="to_user_unread_count",
						location_in_function="try block for to_user_unread_count",
						occurred_for_user=user.username,
						error_text=str(e))	
	
	return private_unread_count


@database_sync_to_async
def unread_private_msg_by_user(user_id):
	count = 0
	try:
		user = CustomUser.objects.get(id=user_id)


		if UnreadPrivateChatMessages.objects.filter(user=user).exists():
			pvt_list = UnreadPrivateChatMessages.objects.filter(user=user)

			for room in pvt_list:
				count = count + room.count
		# print(private_unread_count)
	except Exception as e:
		print("Broken unread_private_msg_by_user", e)
		Private_Chat_Error.objects.create(file="consumer_private_chat.py",
						function_name="unread_private_msg_by_user",
						location_in_function="try block for unread_private_msg_by_user",
						occurred_for_user=str(user_id),
						error_text=str(e))
	
	return count