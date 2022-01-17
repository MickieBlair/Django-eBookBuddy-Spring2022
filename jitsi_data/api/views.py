from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.views import APIView
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from users.models import CustomUser
from jitsi_data.models import Jitsi_User_Event
from jitsi_data.models import Jitsi_User_Status
from jitsi_data.models import Jitsi_Data_Websocket_Error

from jitsi_data.api.serializers import Jitsi_User_Event_Serializer
from jitsi_data.api.serializers import Jitsi_User_Event_Create_Serializer
from jitsi_data.api.serializers import Jitsi_User_Event_Update_Serializer
from jitsi_data.api.serializers import Jitsi_User_Status_Serializer
from jitsi_data.api.serializers import Jitsi_Room_Create_Serializer
from jitsi_data.api.serializers import Jitsi_Room_Update_Serializer

import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from datetime import datetime

from django.utils.timezone import make_aware

SUCCESS = 'success'
ERROR = 'error'
DELETE_SUCCESS = 'deleted'
UPDATE_SUCCESS = 'updated'
CREATE_SUCCESS = 'created'

def format_local_time_api(api_time):
	return make_aware(datetime.fromtimestamp(api_time))

@api_view(['POST', ])
@permission_classes((HasAPIKey,))
def api_occupant_joined_view(request):
	if request.method == 'POST':
		data = request.data
		print("***********************JOINED", data)
		try:
			occupant_info = data['occupant']
			print("occupant_info", occupant_info)
			user_info = {}
			user_info['event_name'] = data['event_name']
			user_info['room_name'] = data['room_name']
			user_info['room_jid'] = data['room_jid']
			user_info['occupant_name'] = occupant_info['name']
			user_info['occupant_email'] = occupant_info['email']			
			user_info['occupant_jid'] = occupant_info['occupant_jid']
			user_info['occupant_joined_at'] = format_local_time_api(occupant_info['joined_at'])
			user_info['occupant_left_at'] = None
			serializer = Jitsi_User_Event_Create_Serializer(data=user_info)

			data = {}

			if serializer.is_valid():
				user_status, created = serializer.save()
				print("User Status", user_status.id)
				print("User Status created", created)
				data['response'] = CREATE_SUCCESS
				data['id'] = user_status.id
				data['created'] = created
				if user_status.user:
					user_status.user.jitsi_status.get_online_status()
					online = user_status.user.jitsi_status.online
				else:
					online = "User Does Not Exist"

				data['online'] = online
				layer = get_channel_layer()
				async_to_sync(layer.group_send)(
					'jitsi_data',
					{
						"type": "jitsi_joined",
						"username" : user_status.occupant_name,
						"room_name" : user_status.room_name,
						"online": online,
						"created": created                         
					}
				)
				return Response(data=data)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			print("Exception top", e)
			Jitsi_Data_Websocket_Error.objects.create(file="views.py",
					function_name="api_occupant_joined_view",
					location_in_function="try block for incoming data",
					occurred_for_user=str(request.user),
					error_text=data)

		
		

@api_view(['POST', ])
@permission_classes((HasAPIKey,))
def api_occupant_left_view(request):
	if request.method == 'POST':
		data = request.data
		print("Left", data)
		try:
			occupant_info = data['occupant']
			print("occupant_info", occupant_info)
			user_info = {}
			user_info['event_name'] = data['event_name']
			user_info['room_name'] = data['room_name']
			user_info['room_jid'] = data['room_jid']
			user_info['occupant_name'] = occupant_info['name']
			user_info['occupant_email'] = occupant_info['email']			
			user_info['occupant_jid'] = occupant_info['occupant_jid']
			user_info['occupant_joined_at'] = format_local_time_api(occupant_info['joined_at'])
			user_info['occupant_left_at'] = format_local_time_api(occupant_info['left_at'])
			serializer = Jitsi_User_Event_Update_Serializer(data=user_info)

			data = {}
			if serializer.is_valid():
				user_status, created = serializer.save()
				print('Back', user_status)
				data['response'] = UPDATE_SUCCESS
				data['id'] = user_status.id
				data['created'] = created
				print('created', created)
				if user_status.user:
					user_status.user.jitsi_status.get_online_status()
					online = user_status.user.jitsi_status.online
				else:
					online = "User Does Not Exist"

				data['online'] = online
				layer = get_channel_layer()
				async_to_sync(layer.group_send)(
					'jitsi_data',
					{
						"type": "jitsi_left",
						"username" : user_status.occupant_name,
						"room_name" : user_status.room_name,
						"online": online,
						"created": created                         
					}
				)
				return Response(data=data)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			print("Exception top", e)
			Jitsi_Data_Websocket_Error.objects.create(file="views.py",
					function_name="api_occupant_left_view",
					location_in_function="try block for incoming data",
					occurred_for_user=str(request.user),
					error_text=data)

		
		

@api_view(['POST', ])
@permission_classes((HasAPIKey,))
def api_room_created_view(request):
	if request.method == 'POST':
		data = request.data
		try:
			data['created_at'] = format_local_time_api(data['created_at'])
			serializer = Jitsi_Room_Create_Serializer(data=data)
			data = {}
			if serializer.is_valid():
				room, created = serializer.save()
				data['response'] = CREATE_SUCCESS
				data['created'] = created
				data['id'] = room.id
				layer = get_channel_layer()
				async_to_sync(layer.group_send)(
					'jitsi_data',
					{
						"type": "room_created",
						"room_created" : created,
						"event_name" : room.event_name,
						"room_name" : room.room_name,                      
					}
				)
				return Response(data=data, status=status.HTTP_200_OK)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			Jitsi_Data_Websocket_Error.objects.create(file="views.py",
					function_name="api_room_created_view",
					location_in_function="try block for incoming data",
					occurred_for_user=str(request.user),
					error_text=str(e) + " - " + json.dumps(data))
			return_data ={}
			return_data['Error'] = str(e)
			return_data['Data'] = data	
			return Response(data=return_data)


@api_view(['POST', ])
@permission_classes((HasAPIKey,))
def api_room_destroyed_view(request):
	if request.method == 'POST':
		data = request.data
		try:
			try:
				occupant_info = data['all_occupants']
				for item in occupant_info:
					item['joined_at'] = format_local_time_api(item['joined_at'])
					item['left_at'] = format_local_time_api(item['left_at'])
			except Exception as e:
				print("Top Exception", e)			

			# print('\n\n occupant_info', occupant_info, type(occupant_info))
			data['created_at'] = format_local_time_api(data['created_at'])
			data['destroyed_at'] = format_local_time_api(data['destroyed_at'])
			data['all_occupants'] = occupant_info
			
			serializer = Jitsi_Room_Update_Serializer(data=data)
					
			data = {}
			if serializer.is_valid():
				print("Yes, Valid")
				room, created = serializer.save()

				print("Room....", room)
				data['response'] = UPDATE_SUCCESS
				data['created'] = created
				print("Destroyed", created)
				data['id'] = room.id
				layer = get_channel_layer()
				async_to_sync(layer.group_send)(
					'jitsi_data',
					{
						"type": "room_destroyed",
						"room_created" : created,
						"event_name" : room.event_name,
						"room_name" : room.room_name,                      
					}
				)
				return Response(data=data, status=status.HTTP_200_OK)
			else:
				print("serializer.errors", serializer.errors)
				
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			print("\n\n\n\n144 views.py Exception", e)
			Jitsi_Data_Websocket_Error.objects.create(file="views.py",
					function_name="api_room_created_view",
					location_in_function="try block for incoming data",
					occurred_for_user=str(request.user),
					error_text=str(e) + " - " + json.dumps(data))
			return_data ={}
			return_data['Error'] = str(e)
			return_data['Data'] = data	
			return Response(data=return_data)



@api_view(['POST', ])
@permission_classes((HasAPIKey,))
def api_create_jitsi_event_view(request):
	if request.method == 'POST':
		data = request.data
		try:
			occupant_info = data['occupant']
			user_info = {}
			user_info['event_name'] = data['event_name']
			user_info['room_name'] = data['room_name']
			user_info['room_jid'] = data['room_jid']
			user_info['occupant_name'] = occupant_info['name']
			user_info['occupant_email'] = occupant_info['email']			
			user_info['occupant_jid'] = occupant_info['occupant_jid']
			user_info['occupant_joined_at'] = occupant_info['joined_at']
			if 'left_at' in occupant_info:
				user_info['occupant_left_at'] = occupant_info['left_at']
			else:
				user_info['occupant_left_at'] = None

			data['occupant']= request.data['occupant']

		except Exception as e:
			Jitsi_Data_Websocket_Error.objects.create(file="views.py",
					function_name="api_create_jitsi_event_view",
					location_in_function="try block for incoming data",
					occurred_for_user=str(request.user),
					error_text=data)
		
		serializer = Jitsi_User_Event_Create_Serializer(data=user_info)
		data = {}
		if serializer.is_valid():
			status = serializer.save()
			data['response'] = CREATE_SUCCESS
			data['id'] = status.id
			layer = get_channel_layer()
			async_to_sync(layer.group_send)(
				'jitsi_data',
				{
					"type": "jitsi_event",
					"status_event" : status.event_name,
					"name" : status.occupant_name,                      
				}
			)
			return Response(data=data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_jitsi_user_status_view(request, username):
	try:
		user_status = Jitsi_User_Status.objects.get(user__username=username)
	except Jitsi_User_Status.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = Jitsi_User_Status_Serializer(status)
		return Response(serializer.data)