from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from urllib.parse import urlencode
from itertools import chain
import datetime
import calendar
import requests

import json
from json import dumps
from django.http import JsonResponse, HttpResponse
from testing import testing_tokens
# Create your views here.

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from buddy_program_data.models import Room_Type, Room


def testing_home_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Testing Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Staff"
			context['room_name'] = "Example_Room"
			return render(request, "testing/testing_home.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')



def testing_staff_view(request, room_name):
	print("ROOM NAME", room_name)
	context = {}
	context['page_title'] = "Staff Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Staff"
			context['room_name'] = room_name
			token = testing_tokens.generateBaseTokenTesting("StaffMember","staff@email.com", "Staff")
			context['token']=token
			return render(request, "testing/test_staff.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def testing_student_view(request, room_name):
	context = {}
	context['page_title'] = "Student Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Student"
			context['room_name'] = room_name
			token = testing_tokens.generateBaseTokenTesting("StudentMember","student@email.com", "Student")
			context['token']=token
			return render(request, "testing/test_student.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def testing_volunteer_view(request, room_name):
	context = {}
	context['page_title'] = "Volunteer Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Volunteer"
			context['room_name'] = room_name
			token = testing_tokens.generateBaseTokenTesting("VolunteerMember","volunteer@email.com", "Volunteer")
			context['token']=token
			return render(request, "testing/test_volunteer.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def check_all_rooms(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		all_rooms = Room.objects.all()

		all_room_info = []

		for room in all_rooms:
			url = "https://sessions.goebookbuddy.org/room" +"?" + "room=" + room.name
			print("URL", url)
			r = requests.get(url)
			room_info = r.json()
			print('room_info', room_info)
			ws_users = []
			for user in room.participants.ws_users.all():
				ws_users.append(user.username)
			room_info['ws_users'] = ws_users
			room_info['room_id'] = room.id
			room_info['ws_count'] = room.participants.ws_users.all().count()
			all_room_info.append(room_info)

		response['updated_info'] = all_room_info

		# layer = get_channel_layer()
		# async_to_sync(layer.group_send)(
		# 	'jitsi_data',
		# 	{
		# 		"type": "room_update",
		# 		"data" : all_room_info                      
		# 	}
		# )

	return HttpResponse(dumps(response), content_type="application/json")

