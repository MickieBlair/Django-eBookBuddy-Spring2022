from django.shortcuts import render, redirect
from users.views import get_program_status
from django.utils import timezone
import datetime
import calendar
from buddy_program_data.models import Server_Schedule, Server_Time, Day
from buddy_program_data.models import Reading_Session_Day_Time
from buddy_program_data.models import Room, Room_Type
from reading_sessions.models import User_Session_Status
from users.models import CustomUser, Role
from matches.models import Scheduled_Match


def home_screen_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Home"

	user = request.user
	

	# if updating_now:
	# 	return redirect('update_in_progress')

	# else:

	if user.is_authenticated:
		context['logged_in_user'] = user
		user_session_status, created = User_Session_Status.objects.get_or_create(user=request.user)		
		if user.is_approved:
			return redirect('landing')				
		else:
			return redirect('pending_approval')

	else:
		return redirect('login')

	# return render(request, "pages/home.html", context)


def all_additional_context(context, user):
	view = user.view()
	context['view'] = view
	main_role = user.main_role()
	context['main_role'] = main_role
	has_staff_role = user.has_staff_role()
	context['has_staff_role'] = has_staff_role

	if main_role == "Staff" or view == "Staff View":
		context['session_lobby'] = Room.objects.get(name="Session Lobby")
		context['match_pending'] = Room.objects.get(name="Match Pending")
		context['testing_room'] = Room.objects.get(name="Testing Room")
		
		context['lobby'] = Room.objects.get(name="Session Lobby")
		context['match_pending'] = Room.objects.get(name="Match Pending")
		context['breakout'] = Room.objects.get(name="Breakout 1")

		reader_role = Role.objects.get(name="Reader")
		if reader_role in user.roles.all():
			context['show_schedule'] = True
			scheduled_slots = user.reader_match_profile.scheduled_slots
			context['scheduled_slots'] =scheduled_slots
			context['scheduled_matches'] =user.scheduled_matches
		else:
			context['show_schedule'] = False


	elif main_role == "Student":
		context['show_schedule'] = True
		scheduled_slots = user.student_match_profile.scheduled_slots
		context['scheduled_slots'] =scheduled_slots
		if user.session_status.active_scheduled_match:
			active_scheduled_match = user.session_status.active_scheduled_match
			context['active_scheduled_match'] = active_scheduled_match
		else:
			context['active_scheduled_match'] = None
		# context['match_pending'] = Room.objects.get(name="Match Pending")
		# context['breakout'] = Room.objects.get(name="Breakout 1")

	elif main_role == "Reader" :
		context['show_schedule'] = True
		scheduled_slots = user.reader_match_profile.scheduled_slots
		context['scheduled_slots'] =scheduled_slots
		context['scheduled_matches'] =user.scheduled_matches
		context['breakout'] = Room.objects.get(name="Breakout 1")

		if has_staff_role:
			context['session_lobby'] = Room.objects.get(name="Session Lobby")
			context['match_pending'] = Room.objects.get(name="Match Pending")

	else:
		context['show_schedule'] = False
		




		

	todays_date = timezone.localtime(timezone.now()).date()
	context['todays_date'] = todays_date
	active_server_schedule = Server_Schedule.objects.get(active=True)
	context['offset'] = active_server_schedule.offset


	

	if context['show_schedule']:
		context['days'] = Day.objects.all()
		today = todays_date.weekday()
		today_day_of_week = calendar.day_name[today]
		context['today_name'] = today_day_of_week
		slots = Reading_Session_Day_Time.objects.filter(active=True)
		context['semester_slots'] = slots

	



	return context


def landing_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Sessions Home"
	context['display_login_logout']= True

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			if user.program_count() == 1:
				program = user.programs.all().first()
				context['program'] = program
				updating_now = get_program_status(program.name)
				if updating_now:
					return redirect('update_in_progress')
				else:
					context['user_view'] = request.user.user_view.name
					context = all_additional_context(context, user)

					user_session_status, created = User_Session_Status.objects.get_or_create(user=request.user)	
					user_session_status.on_landing_page = True
					user_session_status.save()

					return render(request, "pages/landing.html", context)

			else:
				context['programs'] = user.user_programs()
				return render(request, "pages/landing.html", context)
		else:
			return redirect('pending_approval')
	else:
		return redirect('login')



def pending_approval_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Pending Approval"
	context['display_login_logout']= True

	user = request.user


	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			return redirect('landing')				
		else:
			user.session_status.on_landing_page = False
			user.session_status.save()
			return render(request, "pages/pending_approval.html", context)
	else:
		return redirect('login')

	

def update_in_progress_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Update In Progress"
	context['display_login_logout']= True

	user = request.user

	# if user.is_authenticated:
	# 	context['logged_in_user'] = user
	# 	if user.is_approved:
	# 		return redirect('landing')				
	# 	else:
	# 		return redirect('pending_approval')
	# else:
	# 	return redirect('login')

	return render(request, "pages/update_in_progress.html", context)
