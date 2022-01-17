from django.shortcuts import render, redirect
from django.utils import timezone
import datetime
import calendar
import json
from json import dumps
from django.http import JsonResponse, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt

from buddy_program_data.models import Room, Room_Type, Server_Schedule, Server_Time
from buddy_program_data.models import Day, Day_With_Daily_Session
from users.models import CustomUser, Role, User_View
from staff_chat.models import Staff_Chat_Room, Staff_Room_Unread_Chat_Message
from reading_sessions.models import Help_Request, Redirect, Room_Participants
from reading_sessions.models import User_Session_Status, Match_Status_Option, Match_Session_Status
from matches.models import Scheduled_Match, Match_Type
from registration.models import Volunteer_Registration
from reading_sessions import vol_testing_token
from private_chat.models import User_Private_Room_List, PrivateChatRoom



def not_found_view(request, *kwargs):
	context = {}
	context['page_title'] = "Application Not Found"
	return render(request, "reading_sessions/not_found.html", context)


def testing_additional_context(context):
	# print("Testing additional_context Volunteer")
	context['room_role'] = "Moderator"
	todays_date = timezone.localtime(timezone.now()).date()
	context['todays_date'] = todays_date
	active_server_schedule = Server_Schedule.objects.get(name="Volunteer Testing")
	# print("active_server_schedule", active_server_schedule)
	context['offset'] = active_server_schedule.offset
	today = todays_date.weekday()
	today_day_of_week = calendar.day_name[today]
	context['today_day_of_week'] = today_day_of_week
	day_instance = Day.objects.get(name=today_day_of_week)
	# print("todays_date", todays_date)
	# print("day_instance", day_instance)

	if Server_Time.objects.filter(date=todays_date, server_schedule=active_server_schedule).exists():
	
		# print("Exists")
		server_time = Server_Time.objects.get(date=todays_date, server_schedule=active_server_schedule)
		# print("Server Time", server_time) 
		string_date = timezone.localtime(timezone.now()).time().strftime("%H:%M:%S")
		
		current_time =datetime.datetime.strptime(string_date,"%H:%M:%S").time()

		# print("Current Time =", current_time)

		if current_time >= server_time.start_time and current_time < server_time.end_time:

			context['jitsi_on'] = True
			# print("Here Jitsi on")
		else:
			# print("Here Jitsi off")
			context['jitsi_on'] = False
	else:
		# print("Jitsi off")
		context['jitsi_on'] = False

	return context
	

def tech_testing_room_view(request, registration_id, *kwargs):
	# print("Registration ID", registration_id, type(registration_id))
	context = {}
	context['page_title'] = "Testing Room"
	try:
		room=Room.objects.get(name="Testing Room")
		context['room'] = room
		if registration_id == '0':
			# print("Zero")
			user = request.user
			context['logged_in_user'] = user
			context= additional_context(context, user, room)
		else:
			# print("Else")
			registration = Volunteer_Registration.objects.get(id=registration_id)
			context['registration'] = registration
			context = testing_additional_context(context)
			context['room_name'] = room.name
			context['view'] = "Reader View"
			username = registration.first_name + registration.last_name[0]
			context['username'] = username
			role = "Volunteer"
			email= registration.email
			context['token'] = vol_testing_token.generateBaseTokenVolunteerTesting(username, email, role)
		
		return render(request, "reading_sessions/tech_testing_room.html", context)
	except Exception as e:
		print('Exception', e)
		return redirect('reading_sessions:not_found')
	
	
	
	
	


def student_processing(user):	
	temp_type = Match_Type.objects.get(name = "Temporary - In Session")
	sch_type = Match_Type.objects.get(name = "Scheduled")
	room = Room.objects.get(name="Match Pending") 
	user_session_status = User_Session_Status.objects.get(user = user)
	current_active_match_type = user_session_status.current_active_match_type
	print("Active Type", current_active_match_type)

	if user_session_status.needs_new_buddy:
		room = Room.objects.get(name="Match Pending") 
	else:						
		if current_active_match_type == sch_type:
			if user_session_status.active_scheduled_match:
				sch_match = user_session_status.active_scheduled_match
				buddy = sch_match.reader
				buddy_status = User_Session_Status.objects.get(user = buddy.id)
				if buddy_status.current_active_match_type == sch_type:
					# if buddy_status.buddies.count() == 1:
					if buddy_status.online_ws:
						room = buddy_status.room	
						user_session_status.needs_session_match = False
						user_session_status.save()
					else:
						user_session_status.needs_session_match = True
						user_session_status.save()
					# else:
					# 	print("Reader Has More Than One Student")
					# 	user_session_status.needs_session_match = True
					# 	user_session_status.save()

				else:
					print("Reader is not longer Scheduled Type")
					user_session_status.needs_session_match = True
					user_session_status.save()
			else:
				print("Student has no active match")
				user_session_status.needs_session_match = True
				user_session_status.save()
		else:
			print("Student is not longer Scheduled Type")
			user_session_status.needs_session_match = True
			user_session_status.save()


	return room
	


# def reader_processing(user):
# 	temp_type = Match_Type.objects.get(name = "Temporary - In Session")
# 	sch_type = Match_Type.objects.get(name = "Scheduled")
# 	# room = Room.objects.get(name="Match Pending") 
# 	user_session_status = User_Session_Status.objects.get(user = user)
# 	scheduled_matches = user_session_status.scheduled_matches.all()
# 	if scheduled_matches.count() == 1:
# 		active_scheduled_match = scheduled_matches.first()
# 		user_session_status.active_scheduled_match = active_scheduled_match
# 		user_session_status.active_buddy = active_scheduled_match.student
# 		user_session_status.save()
# 	else:


# 	return room


def initial_entry_view(request, **kwargs):
	context = {}
	context['page_title'] = "Initial Entry"
	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			view = user.view()
			print("\n\n\n\n*****view", view)
			match_pending = Room.objects.get(name="Match Pending") 
			reader_role = Role.objects.get(name="Reader")

			if view == "Student View":
				room = student_processing(user)
				return redirect('reading_sessions:room', room_slug=room.slug)

			elif view == "Reader View":
				room = Room_Participants.unoccupied_breakout_first()
				return redirect('reading_sessions:room', room_slug=room.slug)

			elif view == "Staff View":
				if reader_role in user.roles.all():
					room = Room_Participants.unoccupied_breakout_first()
					return redirect('reading_sessions:room', room_slug=room.slug)

				else:
					return redirect('reading_sessions:room', room_slug=match_pending.slug)

			else:
				return redirect('reading_sessions:room', room_slug=match_pending.slug)

		else:
			return redirect('pending_approval')
	else:
		return redirect('login')

def todays_staff_chat(todays_date):
	staff_view = User_View.objects.get(name="Staff View")
	staff = staff_view.user_view.filter(is_approved=True)

	todays_staff_chat, created = Staff_Chat_Room.objects.get_or_create(
												date_created=todays_date,
												)
	if created:
		title = "Staff Chat - " + todays_date.strftime("%B %d, %Y")
		todays_staff_chat.title = title
		todays_staff_chat.save()
		for u in staff:
			unread_items, created = Staff_Room_Unread_Chat_Message.objects.get_or_create(user=u)
			unread_items.room = todays_staff_chat
			unread_items.unread_count = 0
			unread_items.save()
		
	return todays_staff_chat

# Create your views here.

def staff_users():
	staff_view = User_View.objects.get(name="Staff View")
	qs = CustomUser.objects.filter(user_view=staff_view).exclude(username="Buddy_Admin").exclude(username="Mickie").order_by('username')
	return qs

def remaining_users():
	student_role = Role.objects.get(name="Student")
	reader_role = Role.objects.get(name="Reader")
	qs = CustomUser.objects.all().exclude(roles__in=[student_role, reader_role]).order_by('username')
	return qs

def unmatched_student_users():
	student_role = Role.objects.get(name="Student")
	qs = CustomUser.objects.filter(roles__in=[student_role,], session_status__needs_session_match=True)
	return qs

def unmatched_reader_users():
	reader_role = Role.objects.get(name="Reader")
	qs = CustomUser.objects.filter(roles__in=[reader_role,], session_status__needs_session_match=True)
	return qs

def additional_context(context, user, room):
	todays_date = timezone.localtime(timezone.now()).date()
	view = user.view()
	context['view'] = view
	main_role = user.main_role()
	context['main_role'] = main_role
	has_staff_role = user.has_staff_role()
	context['has_staff_role'] = has_staff_role
	context['token'] = user.get_token()
	context['room_name'] = room.name
	context['room_id'] = room.id

	testing_room = Room.objects.get(name="Testing Room")

	if main_role == "Staff" or has_staff_role:
		context['unmatched_students'] = unmatched_student_users()
		context['unmatched_readers'] = unmatched_reader_users()
		context['session_lobby'] = Room.objects.get(name="Session Lobby")
		context['testing_room'] = Room.objects.get(name="Testing Room")
		context['match_pending'] = Room.objects.get(name="Match Pending")
		context['all_rooms'] = Room.objects.filter(show_in_session_list=True)
		student_role = Role.objects.get(name="Student")
		context['all_students'] = student_role.user_roles.filter(is_approved=True).order_by('username')
		reader_role = Role.objects.get(name="Reader")
		context['all_readers'] = reader_role.user_roles.filter(is_approved=True).order_by('username')
		context['all_rest'] = remaining_users()
		context['room_role'] = "Owner"
		msg_users = CustomUser.objects.filter(is_approved = True).order_by('username')
		context['all_users'] = msg_users
		if Day_With_Daily_Session.objects.filter(date=timezone.localtime(timezone.now())).exists():
			day_with_session = Day_With_Daily_Session.objects.get(date=timezone.localtime(timezone.now()))
			context['day_with_session'] = day_with_session	

		staff_chat = todays_staff_chat(todays_date)
		context['staff_chat'] = staff_chat
		# context['room_role'] = "Moderator"
		all_helps=Help_Request.objects.filter(done=False)
		context['all_helps'] = all_helps
		all_helps=Help_Request.objects.filter(done=False)
		context['all_helps'] = all_helps
		match_redirects = Redirect.objects.filter(auto_send=False)
		context['match_redirects'] = match_redirects

	context['todays_date'] = todays_date

	if room == testing_room:
		active_server_schedule = Server_Schedule.objects.get(name="Volunteer Testing")
		context['offset'] = active_server_schedule.offset
		today = todays_date.weekday()
		today_day_of_week = calendar.day_name[today]
		context['today_day_of_week'] = today_day_of_week
		day_instance = Day.objects.get(name=today_day_of_week)
		if Server_Time.objects.filter(date=todays_date, server_schedule=active_server_schedule).exists():	
			print("Exists")
			server_time = Server_Time.objects.get(date=todays_date, server_schedule=active_server_schedule)
			print("Server Time", server_time) 
			string_date = timezone.localtime(timezone.now()).time().strftime("%H:%M:%S")
			
			current_time =datetime.datetime.strptime(string_date,"%H:%M:%S").time()

			print("Current Time =", current_time)

			if current_time >= server_time.start_time and current_time < server_time.end_time:

				context['jitsi_on'] = True
				print("Here Jitsi on")
			else:
				print("Here Jitsi off")
				context['jitsi_on'] = False
		else:
			print("Jitsi off")
			context['jitsi_on'] = False



	else:		
		active_server_schedule = Server_Schedule.objects.get(active=True)
		context['offset'] = active_server_schedule.offset
		today = todays_date.weekday()
		today_day_of_week = calendar.day_name[today]
		context['today_day_of_week'] = today_day_of_week
		day_instance = Day.objects.get(name=today_day_of_week)

		if Server_Time.objects.filter(day=day_instance, server_schedule=active_server_schedule).exists():
		# if active_server_schedule.times.get(day=day_instance).exists():
			server_time = Server_Time.objects.get(day=day_instance, server_schedule=active_server_schedule)
			print("Server Time", server_time) 
			string_date = timezone.localtime(timezone.now()).time().strftime("%H:%M:%S")
			
			current_time =datetime.datetime.strptime(string_date,"%H:%M:%S").time()

			print("Current Time =", current_time)

			if current_time >= server_time.start_time and current_time < server_time.end_time:
				context['jitsi_on'] = True
				print("Jitsi on")
			else:
				print("Jitsi off")
				context['jitsi_on'] = False
		else:
			print("Jitsi off")
			context['jitsi_on'] = False

	return context


def room_view(request, room_slug, *args, **kwargs):
	context = {}
	room = Room.objects.get(slug=room_slug)
	context['room'] = room
	context['page_title'] = room.name
	context['display_login_logout']= True

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context = additional_context(context, user, room)
			user.session_status.on_landing_page = False
			user.session_status.all_connected = False
			user.session_status.room = room
			user.session_status.save()
			private_chat, created= User_Private_Room_List.objects.get_or_create(
															user=user) 
			context['private_chat'] = private_chat

			context['staff_users'] = staff_users()

			return render(request, "reading_sessions/room.html", context)
		else:
			return redirect('pending_approval')
	else:
		return redirect('login')


def reading_sessions_home(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Let's Read!"
	context['display_login_logout']= True

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:

			return render(request, "reading_sessions/reading_session_home.html", context)
		else:
			return redirect('pending_approval')
	else:
		return redirect('login')

def session_end_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Session End"
	context['display_login_logout']= True

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:

			return render(request, "reading_sessions/session_end.html", context)
		else:
			return redirect('pending_approval')
	else:
		return redirect('login')


def staff_reset_count(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		user_id = request.GET.get("user_id", None)
		# print(user_id)

		# check database.
		if CustomUser.objects.filter(id = user_id).exists():
			user = CustomUser.objects.get(id=user_id)
			user.unread_staff.reset_count()
			
			response['valid'] = True
			response['unread_staff_count'] = user.unread_staff.unread_count
			return HttpResponse(dumps(response), content_type="application/json")
		else:
			response['valid'] = False
			return HttpResponse(dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)

@csrf_exempt
def create_help_request(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "POST":
		# get from the client side.	
		# print("from user", request.POST.get('from_user_id'))
		# print("from_room ", request.POST.get('from_room_id'))
		# print("message ", request.POST.get('message'))	
		# print("user_message ", request.POST.get('user_message'))		
		from_user=CustomUser.objects.get(id=int(request.POST.get('from_user_id')))
		from_room=Room.objects.get(id=int(request.POST.get('from_room_id')))
		message=request.POST.get('message')
		user_message = request.POST.get('user_message')
		new_request = Help_Request.objects.create(from_user=from_user,
													from_room = from_room,
													message= message,
													user_message = user_message)
		response['valid'] = True

		response['new_help'] = from_room.name + ": " + from_user.username

		layer = get_channel_layer()
		async_to_sync(layer.group_send)(
			'status',
			{
				"type": "help_requests",
				"username" : from_user.username,                    
			}
		)

	return HttpResponse(dumps(response), content_type="application/json")

@csrf_exempt
def ajax_help_mark_as_done(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "POST":

		user_id = request.POST.get('user_id')
		request_id = request.POST.get('request_id')
		send_to_staff = request.POST.get('send_to_staff')

		print("ajax_help_mark_as_done", user_id, request_id, send_to_staff)

		try:
			user_marking_done = CustomUser.objects.get(id=user_id)
			help_request = Help_Request.objects.get(id=request_id)
			help_request.mark_as_done(user_marking_done.id)
			
			not_done_count = Help_Request.objects.filter(done=False).count()
			if send_to_staff:
				layer = get_channel_layer()
				async_to_sync(layer.group_send)(
					'status',
					{
						"type": "help_requests",
						"username" : request.user.username,                    
					}
				)

			response['valid'] = True
			response['not_done_count'] = not_done_count


		except Exception as e:
			print("BROKEN mark_help_request_done", e)
			response['valid'] = False	

		response['send_to_staff'] = send_to_staff

	return HttpResponse(dumps(response), content_type="application/json")



def ajax_check_user_status(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":

		user_id = request.GET.get('user_id')
		user_view = request.GET.get('user_view')
		all_connected = request.GET.get('all_connected')

		# print("ajax_check_user_status", user_id)
		# print("user_view", user_view)
		# print("all_connected", all_connected)

		try:
			stats_user = CustomUser.objects.get(id=user_id)
			user_session_status = User_Session_Status.objects.get(user=stats_user)
			if all_connected == 'true':
				user_session_status.all_connected = True
			if all_connected == "false":
				user_session_status.all_connected = False

			user_session_status.save()

			response['valid'] = True



		except Exception as e:
			print("BROKEN ajax_check_user_status", e)
			response['valid'] = False

	return HttpResponse(dumps(response), content_type="application/json")


def ajax_get_private_chats(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":

		user_id = request.GET.get('user_id')
		current_unread_count = request.GET.get('current_unread_count')


		print("ajax_check_user_status", user_id)
		print('current_unread_count', current_unread_count)
	
		try:
			this_user = CustomUser.objects.get(id=user_id)
			private_chat, created= User_Private_Room_List.objects.get_or_create(
															user=this_user) 
			new_total_unread_count = private_chat.total_unread_private
			response['total_unread_private'] =new_total_unread_count
			response['valid'] = True



		except Exception as e:
			print("BROKEN ajax_check_user_status", e)
			response['valid'] = False

	return HttpResponse(dumps(response), content_type="application/json")


def ajax_get_private_room(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":

		user_id = request.GET.get('user_id', None)
		msg_to = request.GET.get('msg_to', None)
		p_msg = request.GET.get('p_msg', None)



		print("user_id", user_id)
		print('msg_to', msg_to)
		print('p_msg', p_msg)
	
		try:
			user1 = CustomUser.objects.get(id=user_id)
			user2 = CustomUser.objects.get(id=msg_to)
			response['user1'] = user1.id
			response['user2'] = user2.id
			response['sender_connected'] = user1.session_status.all_connected
			response['receiver_connected'] = user2.session_status.all_connected

			if PrivateChatRoom.objects.filter(user1=user1, user2=user2).exists():
				private_chat = PrivateChatRoom.objects.get(user1=user1, 
															user2=user2)
			elif PrivateChatRoom.objects.filter(user1=user2, user2=user1).exists():
				private_chat = PrivateChatRoom.objects.get(user1=user2, 
														user2=user1)
			else:
				private_chat, created = PrivateChatRoom.objects.get_or_create(user1=user1,
																user2=user2,
																last_use=timezone.localtime(timezone.now()))
				private_chat.last_use=timezone.localtime(timezone.now())
				private_chat.save()


			response['private_room_id'] = private_chat.id
			user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
			user1_list.add_room(private_chat)

			user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
			user2_list.add_room(private_chat)

			response['valid'] = True


		except Exception as e:
			print("BROKEN ajax_get_private_room", e)
			response['valid'] = False

	return HttpResponse(dumps(response), content_type="application/json")

