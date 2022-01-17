import json
import asyncio
from channels.db import database_sync_to_async


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer
from users.models import CustomUser
from jitsi_data.models import Jitsi_Data_Websocket_Error
from buddy_program_data.models import Room
from reading_sessions.models import Room_Participants


class JitsiDataConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		# print("\n\n\nJitsiDataConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'jitsi_data'
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
		print("\n*******************JitsiDataConsumer: disconnect", timezone.now())

		try:
			print("\n\nDisconnecting JitsiDataConsumer", str(self.scope["user"]))
			room, count = await set_user_offline(self.username)

		except Exception as e:
			print(e)

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
		# print("\n***** RegistrationConsumer: receive_json: " + str(self.scope["user"]))
		# print("This is the command", command)

		if command =="test":
			print("\n\n\n\nTESTING THE CONNECTION")
			# await adjust_registration_ip(content)
			# await self.test_connection(content)
		elif command =="staff_connect":
			print("\n\n\n\nstaff_connect THE CONNECTION")
			self.username = content['username']
			room, count = await set_user_online(content)
			await self.test_connection(content)

		elif command =="other_connect":
			print("\n\n\n\nother_connect THE CONNECTION")
			self.username = content['username']
			room, count = await set_user_online(content)
			await self.test_connection(content)


	async def test_connection(self, content):

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'connect_success',
				"scope_username": str(self.scope["user"]),
				"username": str(content['username']),
			}
		)

	async def connect_success(self, event):		
		await self.send_json(
			{
				"msg_type": "websocket_good",
				"scope_username": event["scope_username"],	
				"username": event["username"],
			},
		)

	async def jitsi_event(self, event):		
		await self.send_json(
			{
				"msg_type": "jitsi_event",	
				"status_event": event["status_event"],
				"name": event["name"],
			},
		)

	async def room_created(self, event):		
		await self.send_json(
			{
				"msg_type": "room_created",
				"room_created_in_db" : event["room_created"],	
				"event_name": event["event_name"],
				"room_name": event["room_name"],
			},
		)

	async def room_destroyed(self, event):		
		await self.send_json(
			{
				"msg_type": "room_destroyed",
				"room_created_in_db" : event["room_created"],		
				"event_name": event["event_name"],
				"room_name": event["room_name"],
			},
		)

	async def jitsi_joined(self, event):		
		await self.send_json(
			{
				"msg_type": "jitsi_joined",	
				"username": event["username"],
				"room_name": event["room_name"],
				"online": event["online"],
				"created": event["created"],
			},
		)

	async def jitsi_left(self, event):		
		await self.send_json(
			{
				"msg_type": "jitsi_left",	
				"username": event["username"],
				"room_name": event["room_name"],
				"online": event["online"],
				"created": event["created"],
			},
		)

	async def room_update(self, event):		
		await self.send_json(
			{
				"msg_type": "room_update",	
				"data": event["data"],
			},
		)
 

@database_sync_to_async
def adjust_registration_ip(content):
	try:
		print("\n\n\n\n\nadjust_registration_ip", content)
		reg_type = content['reg_type']
		reg_id = content['reg_id']
		print("reg_type", reg_type)
		print("reg_type", reg_type)

		if reg_type == "Volunteer":
			registration = Volunteer_Registration.objects.get(id=reg_id)
			ip_info = Volunteer_Registration_IP_Info.objects.get(registration=registration)
			ip_info.ws_connected = True
			ip_info.save()


	except Exception as e:
		print("BROKEN adjust_registration_ip", e)
		Jitsi_Data_Websocket_Error.objects.create(file="registration_consumer.py",
						function_name="adjust_registration_ip",
						location_in_function="try block for adjust_registration_ip",
						occurred_for_user=str(content['reg_type'] + " - " + content['reg_id']),
						error_text=e)
	return True	


@database_sync_to_async
def set_user_online(content):
	try:
		print("\n\n\n\n\nJITSI set_user_online", content)
		# user_id = content['user_id']
		# room_id = content['room_id']
		
		# room = Room.objects.get(id=room_id)		
			
		# participants, created = Room_Participants.objects.get_or_create(room=room)

		payload = {}
		data = json.dumps(payload)
		count = 0


	except Exception as e:
		print("BROKEN set_user_online", e)
		Jitsi_Data_Websocket_Error.objects.create(file="consumer_jitsi_data.py",
						function_name="set_user_online",
						location_in_function="try block for set_user_online",
						occurred_for_user=str(content['username']),
						error_text=e)

	return data, count


@database_sync_to_async
def set_user_offline(username):
	try:
		print("\n\n\n\n\n JITSI set_user_offline", username)
		# user_id = content['user_id']
		# room_id = content['room_id']
		
		# room = Room.objects.get(id=room_id)		
			
		# participants, created = Room_Participants.objects.get_or_create(room=room)
		payload = {}
		data = json.dumps(payload)
		count = 0

	except Exception as e:
		print("BROKEN set_user_online", e)
		Jitsi_Data_Websocket_Error.objects.create(file="consumer_jitsi_data.py",
						function_name="set_user_offline",
						location_in_function="try block for set_user_offline",
						occurred_for_user=str(username),
						error_text=e)

	return data, count
