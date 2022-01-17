import json
import asyncio
from channels.db import database_sync_to_async


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer
from users.models import CustomUser
from registration.models import Volunteer_Registration, Volunteer_Registration_IP_Info
from registration.models import Volunteer_Registration_Note
from registration.models import Parent_Registration, Parent_Registration_IP_Info
from registration.models import Parent_Registration_Note
from registration.models import Staff_Registration, Staff_Registration_IP_Info
from registration.models import Staff_Registration_Note

from registration.models import Registration_Error


class RegistrationConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\nRegistrationConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'registration'
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
		print("\n*******************RegistrationConsumer: disconnect", timezone.now())

		try:
			print("\n\nDisconnecting RegistrationConsumer", str(self.scope["user"]))

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
		print("\n***** RegistrationConsumer: receive_json: " + str(self.scope["user"]))
		# print("This is the command", command)

		if command =="test":
			await adjust_registration_ip(content)
			await self.test_connection(content)


	async def test_connection(self, content):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'connect_success',
				"username": str(self.scope["user"]),
				"reg_type": str(content['reg_type']),
				"reg_id": str(content['reg_id']),
			}
		)

	async def connect_success(self, event):		
		await self.send_json(
			{
				"msg_type": "websocket_good",	
				"username": event["username"],
				"reg_type": event["reg_type"],
				"reg_id": event["reg_id"],
			},
		)


@database_sync_to_async
def adjust_registration_ip(content):
	try:
		print("\n\n\n\n\nadjust_registration_ip", content)
		reg_type = content['reg_type']
		reg_id = content['reg_id']

		if reg_type == "Volunteer":
			registration = Volunteer_Registration.objects.get(id=reg_id)
			ip_info = Volunteer_Registration_IP_Info.objects.get(registration=registration)
			ip_info.ws_connected = True
			ip_info.save()

			ip_note = Volunteer_Registration_Note.objects.create(registration = registration,
																name="Websocket Connects",
																)

		elif reg_type == "Parent":
			registration = Parent_Registration.objects.get(id=reg_id)
			ip_info = Parent_Registration_IP_Info.objects.get(registration=registration)
			ip_info.ws_connected = True
			ip_info.save()

			ip_note = Parent_Registration_Note.objects.create(registration = registration,
																name="Websocket Connects",
																)

		elif reg_type == "Staff":
			registration = Staff_Registration.objects.get(id=reg_id)
			ip_info = Staff_Registration_IP_Info.objects.get(registration=registration)
			ip_info.ws_connected = True
			ip_info.save()

			ip_note = Staff_Registration_Note.objects.create(registration = registration,
																name="Websocket Connects",
																)


	except Exception as e:
		print("BROKEN adjust_registration_ip", e)
		Registration_Error.objects.create(file="registration_consumer.py",
						function_name="adjust_registration_ip",
						location_in_function="try block for adjust_registration_ip",
						occurred_for_user=str(content['reg_type'] + " - " + content['reg_id']),
						error_text=str(e))
	return True	

