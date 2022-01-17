from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.core.mail import EmailMultiAlternatives
from users.models import CustomUser, User_Note, User_View
from site_admin.forms import Create_Student_User_Form
from site_admin.forms import Create_Volunteer_User_Form
from users.models import Program, Role, User_Session, Login_Logout_Log, Session_Log
from buddy_program_data.models import Program_Status, Program_Semester
from buddy_program_data.models import Server_Schedule, Server_Time
from site_admin.models import User_Team_Info
from registration.models import Volunteer_Registration, Parent_Registration
from registration.models import Student_Registration, Staff_Registration
from registration.models import Staff_Registration_Note, Registration_Error
from registration.models import Volunteer_Registration_Status, Volunteer_Video, Volunteer_Registration_Note
from registration.models import Student_Registration_Status, Student_Registration_Note
from site_admin.forms import Volunteer_Status_Form, Staff_Registration_Note_Form
from site_admin.forms import Create_Staff_User_Form, User_Update_Form
from registration.models import Parent_Registration_Note
from site_admin.send_sms import send_text_message
from site_admin.forms import Volunteer_Registration_Display_Form, Staff_Registration_Display_Form
from site_admin.forms import Student_Registration_Display_Form, Create_Any_User_Form
from site_admin.forms import Volunteer_Registration_Note_Form, Student_Registration_Note_Form
from site_admin.forms import Student_Status_Form, Parent_Registration_Display_Form
from site_admin.forms import User_Team_Info_Create_Form, Mega_Team_Form, Team_Form
from buddy_program_data.models import Team_Meeting_Time, Session_Day_Option
from buddy_program_data.models import Team, Mega_Team
from buddy_program_data.models import Session_Time_Option, Session_Meeting_Option
from buddy_program_data.models import Question, Room, Room_Type
from matches.models import Student_Match_Profile, Reader_Match_Profile
from buddy_program_data.models import Reading_Session_Day_Time
from reading_sessions.models import User_Session_Status, Room_Participants
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from django.forms.models import model_to_dict
from registration.serializers import Volunteer_Registration_Serializer
from registration.serializers import Student_Registration_Serializer
from registration.serializers import Parent_Registration_Serializer
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files import File
import os
from uuid import uuid4
from django.core.files.base import ContentFile
from django.db.models import Count

SEND_EMAILS = True

def edit_team_view(request, team_id, **kwargs):
	context = {}
	context['page_title'] = "Edit Team"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				team = Team.objects.get(id=team_id)
				context['team'] = team

				team_leader = team.leader
				if team_leader:
					team_leader.team_info.team_role = None
					team_leader.team_info.team = None
					team_leader.team_info.mega = None
					team_leader.team_info.save()

				if request.method == "POST":
					form = Team_Form(request.POST, instance=team, label_suffix='')
					if form.is_valid():	
						obj = form.save()	
						obj.room.name = str(obj)
						obj.room.save()	

						if obj.leader:
							print("Yes Team Leader")
							obj.leader.team_info.team_role = "Team Leader"
							obj.leader.team_info.mega = obj.mega
							obj.leader.team_info.team = obj
							obj.leader.team_info.save()
						else:
							print("NO TEAM LEADER")

						mega_team = obj.mega
						mega_team.team_leaders.clear()
						all_mega_team_leaders = mega_team.user_mega.filter(team_role="Team Leader")
						for item in all_mega_team_leaders.all():
							mega_team.team_leaders.add(item.user)


						
						return redirect('site_admin:mega_teams')
					else:
						print("errors", form.errors)
						print("cleaned data", form.cleaned_data)

				else:
					form = Team_Form(instance=team, label_suffix='')

				context['form'] = form

				return render(request, "site_admin/teams/edit_team.html", context)	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def edit_mega_teams_view(request, mega_id, **kwargs):
	context = {}
	context['page_title'] = "Edit Mega Team"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				mega_team = Mega_Team.objects.get(id=mega_id)
				context['mega_team'] = mega_team
				coordinator_mega = mega_team.coordinator
				print("Mega Coordinator", coordinator_mega)
				if coordinator_mega:
					coordinator_mega.team_info.team_role = None
					coordinator_mega.team_info.mega = None
					coordinator_mega.team_info.save()

				if request.method == "POST":
					form = Mega_Team_Form(request.POST, instance=mega_team, label_suffix='')
					if form.is_valid():	
						obj = form.save()
						teams = obj.teams.all()
						for team in teams:							
							team.room.name = str(team)
							team.room.save()


						if obj.coordinator:
							obj.coordinator.team_info.team_role = "Coordinator"
							obj.coordinator.team_info.mega = obj
							obj.coordinator.team_info.save()



						return redirect('site_admin:mega_teams')
					else:
						print("errors", form.errors)
						print("cleaned data", form.cleaned_data)

				else:
					form = Mega_Team_Form(instance=mega_team, label_suffix='')

				context['form'] = form

				return render(request, "site_admin/teams/edit_mega_team.html", context)	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def mega_teams_view(request, **kwargs):
	context = {}
	context['page_title'] = "Mega Teams"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				mega_teams = Mega_Team.objects.all()
				context['mega_teams'] = mega_teams

				# room_type = Room_Type.objects.get(name="Team Meeting")
				# print("Room_Type", room_type)

				# for team in Team.objects.all():
				# 	print(team)
				# 	room, created = Room.objects.get_or_create(
				# 			name=team,
				# 			room_type=room_type)
				# 	team.room = room
				# 	team.save()

				return render(request, "site_admin/teams/mega_teams.html", context)	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def convert_team_choices():
	options = Team.objects.all()
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options

def create_user_team_info_view(request, user_id, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Team"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				member = CustomUser.objects.get(id=user_id)
				context['member'] = member
				context['team_choices'] = convert_team_choices()
				context['teams'] = Team.objects.all()
				context['mega_teams'] = Mega_Team.objects.all()

				user_roles = member.roles.all()
				team_leader_role = Role.objects.get(name='Team Leader')
				coordinator_role = Role.objects.get(name='Coordinator')
				if team_leader_role in user_roles:
					initial_role = team_leader_role.name
				elif coordinator_role in user_roles:
					initial_role = coordinator_role.name
				else:
					initial_role = "Member"

				if request.method == "POST":
					form = User_Team_Info_Create_Form(request.POST, instance=member.team_info, label_suffix='')
					if form.is_valid():	
						obj = form.save()
						mega= obj.mega
						team = obj.team

						mega.volunteers.clear()
						team.volunteers.clear()

						all_mega_users = mega.user_mega.filter(team_role="Member")
						for item in all_mega_users:
							mega.volunteers.add(item.user)

						all_team_users = team.user_team.filter(team_role="Member")
						for item in all_team_users:
							team.volunteers.add(item.user)



						
						return redirect('site_admin:view_users', role="Volunteer")
					else:
						print("errors", form.errors)
						print("cleaned data", form.cleaned_data)
						if "team" in form.cleaned_data:
							context['cleaned_team']= form.cleaned_data['team']
						
				else:
					form = User_Team_Info_Create_Form(label_suffix='',
											instance=member.team_info,
											# initial={
											# 'user': member,
											# 'team_role': initial_role,
											# }
											)

				context['form'] = form

				return render(request, "site_admin/teams/create_team_info.html", context)	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def email_video_reminder(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			subject = 'eBookBuddy | Volunteer Video Reminder'
			context['link'] = settings.BASE_URL + "/registration/volunteer/video/upload/"
			html_message = render_to_string('site_admin/email_templates/reminder_video_upload.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Volunteer", subject, plain_message, to, html_message)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Video Reminder Email Sent",
																)
			
		except Exception as e:
			print("SOME Exception", e)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Video Reminder Email Failed",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_video_reminder site admin",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))


def video_reminder_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Emails"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				registration = Volunteer_Registration.objects.get(id=registration_id)
				print("Registration for Email", registration)
				email_video_reminder(registration)
				return redirect('site_admin:registrations_volunteers', search_title="All")	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')


def email_whatsapp(registration):
	if SEND_EMAILS:
		print("email_whatsapp send emails True", registration)
		try:
			context = {}
			context['registration'] = registration
			lang = registration.registration_language.iso
			if lang == "en":
				subject = 'eBookBuddy | Urgent Reminder'
				html_message = render_to_string('site_admin/email_templates/student_reminder_eng.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'registration@ebookbuddy.org'
				to = registration.email
				
			elif lang == "es":
				subject = 'eBookBuddy | Recordatorio urgente'
				html_message = render_to_string('site_admin/email_templates/student_reminder_span.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'registration@ebookbuddy.org'
				to = registration.email
				
			email_address_parameters("Tails", subject, plain_message, to, html_message)
			Parent_Registration_Note.objects.create(registration = registration,
																name="WhatsApp Reminder Email Sent",
																)
			
		except Exception as e:
			print("SOME Exception", e)
			Parent_Registration_Note.objects.create(registration = registration,
																name="WhatsApp Reminder Email Failed",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_whatsapp site admin",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))

	else:
		print("email_whatsapp send emails False", registration)



def whatsapp_email(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Emails"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				registration = Parent_Registration.objects.get(id=registration_id)
				email_whatsapp(registration)
				return redirect('site_admin:registrations_students', search_title="All")	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def email_parent(registration):
	if SEND_EMAILS:
		print("email_link_server_times send emails True", registration)
		try:
			context = {}
			context['registration'] = registration
			lang = registration.registration_language.iso
			if lang == "en":
				subject = 'eBookBuddy | Parent Information Received'
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"

				html_message = render_to_string('site_admin/email_templates/resend_parent_register_children.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'registration@ebookbuddy.org'
				to = registration.email
				
			elif lang == "es":
				subject = 'eBookBuddy | Parent Information Received'
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"

				html_message = render_to_string('site_admin/email_templates/spanish_resend.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'registration@ebookbuddy.org'
				to = registration.email
				
			email_address_parameters("Tails", subject, plain_message, to, html_message)
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Registration Submitted",
																)
			
		except Exception as e:
			print("SOME Exception", e)
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Registration Submitted",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_parent site admin",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))

	else:
		print("email_parent send emails False", registration)



def send_parent_email(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Emails"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				registration = Parent_Registration.objects.get(id=registration_id)
				email_parent(registration)
				return redirect('site_admin:registrations_parents', search_title="All")	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')



def get_parent_regs_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		users = Parent_Registration.objects.filter(
			Q(parent_first_name__icontains=q)|
			Q(parent_last_name__icontains=q)|
			Q(email__icontains=q)
			).order_by('date_created')

		for user in users:
			queryset.append(user)

	return list(set(queryset))

def total_parent_registrations():
	qs = Parent_Registration.objects.all()
	return qs

def no_children():
	new_qs = []
	count = 0
	qs = Parent_Registration.objects.all()
	for reg in qs:
		if reg.parent_info.all().count() == 0:
			new_qs.append(reg)
			count = count+1
	return new_qs, count

def registrations_parents_view(request, search_title, **kwargs):
	context = {}
	context['page_title'] = "All Parents Registrations"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['regs'] = get_parent_regs_queryset(query)
						context['count'] = len(context['regs'])
						context['search_title'] = "Matching"
					else:
						context['regs'] = total_parent_registrations()
						context['count'] = total_parent_registrations().count()
						context['search_title'] = "All"


				else:
					
					if search_title == "All":
						context['regs'] = total_parent_registrations()
						context['count'] = total_parent_registrations().count()
						context['search_title'] = "All"
					elif search_title == "No_Children":
						no_children_qs, no_count = no_children()
						context['regs'] = no_children_qs
						context['count'] = no_count
						context['search_title'] = "No Children"

					
				no_children_qs, no_count = no_children()
				context['total_parent_registrations'] = total_parent_registrations().count()
				context['no_children_count'] = no_count
				
				return render(request, "site_admin/registrations/all_parents.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def send_volunteer_user_info_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Emails"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				registration = Volunteer_Registration.objects.get(id=registration_id)
				print("User Info Email", registration)
				email_volunteer_user_info(registration)
				return redirect('site_admin:registrations_volunteers', search_title="All")	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def server_times_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Emails"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				registration = Volunteer_Registration.objects.get(id=registration_id)
				print("Registration for Email", registration)
				email_link_server_times(registration)
				return redirect('site_admin:registrations_volunteers', search_title="All")	
			else:				
				return redirect('access_denied')

		else:
			return redirect('login')

def email_address_parameters(from_user, subject, plain_message, to_user, html_message):

	if from_user == "Tails":
		with get_connection(
				host=settings.STU_REG_EMAIL_HOST, 
				port=settings.STU_REG_EMAIL_PORT, 
				username=settings.STU_REG_EMAIL_HOST_USER, 
				password=settings.STU_REG_EMAIL_HOST_PASSWORD, 
				use_tls=settings.STU_REG_EMAIL_USE_TLS
		) as connection:
			msg = EmailMultiAlternatives(subject, plain_message, settings.STU_REG_DEFAULT_FROM_EMAIL, [to_user], connection=connection)
			msg.attach_alternative(html_message, "text/html")
			msg.send()

	elif from_user == "Volunteer":
		with get_connection(
				host=settings.VOL_REG_EMAIL_HOST, 
				port=settings.VOL_REG_EMAIL_PORT, 
				username=settings.VOL_REG_EMAIL_HOST_USER, 
				password=settings.VOL_REG_EMAIL_HOST_PASSWORD, 
				use_tls=settings.VOL_REG_EMAIL_USE_TLS
		) as connection:
			msg = EmailMultiAlternatives(subject, plain_message, settings.VOL_REG_DEFAULT_FROM_EMAIL, [to_user], connection=connection)
			msg.attach_alternative(html_message, "text/html")
			msg.send()

	elif from_user == "Staff":
		with get_connection(
				host=settings.EMAIL_HOST, 
				port=settings.EMAIL_PORT, 
				username=settings.EMAIL_HOST_USER, 
				password=settings.EMAIL_HOST_PASSWORD, 
				use_tls=settings.EMAIL_USE_TLS
		) as connection:
			msg = EmailMultiAlternatives(subject, plain_message, settings.VOL_REG_DEFAULT_FROM_EMAIL, [to_user], connection=connection)
			msg.attach_alternative(html_message, "text/html")
			msg.send()

def email_volunteer_user_info(registration):
	if SEND_EMAILS:
		print("email_volunteer_user_info send emails True", registration)
		try:
			context = {}
			context['registration'] = registration
			context['login_link'] = settings.BASE_URL
			context['username'] = registration.user.username
			context['password'] = "ebookbuddy"

			subject = 'eBookBuddy | Approved - You are officially a volunteer member!'
			html_message = render_to_string('site_admin/email_templates/volunteer_created.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Volunteer", subject, plain_message, to, html_message)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="User Info Email Sent",
																)
			
		except Exception as e:
			print("SOME Exception", e)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="User Info Email Failed",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_volunteer_user_info site admin",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))

	else:
		print("email_volunteer_user_info send emails False", registration)


def email_link_server_times(registration):
	if SEND_EMAILS:
		print("email_link_server_times send emails True", registration)
		try:
			context = {}
			context['registration'] = registration
			context['testing_link'] = settings.BASE_URL + "/registration/volunteer/testing/"

			todays_date = timezone.localtime(timezone.now()).date()
			context['todays_date'] = todays_date
			server_schedule = Server_Schedule.objects.get(name="Volunteer Testing")
			server_times = server_schedule.schedule.filter(date__gte=todays_date)
			context['server_times'] = server_times

			subject = 'eBookBuddy Tech Testing'
			html_message = render_to_string('registration/email_templates/tech_testing_vol.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Volunteer", subject, plain_message, to, html_message)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Sent For Tech Testing",
																)
			
		except Exception as e:
			print("SOME Exception", e)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Failed For Tech Testing",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_link_server_times site admin",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))

	else:
		print("email_link_server_times send emails False", registration)	


def edit_user_view(request, user_id, **kwargs):
	context = {}
	context['page_title'] = "Edit User"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				programs = Program.objects.filter(name="eBookBuddy")

				member = CustomUser.objects.get(id=user_id)
				volunteer_role = Role.objects.get(name="Volunteer")
				reader_role = Role.objects.get(name="Reader")
				staff_role = Role.objects.get(name="Staff")
				student_role = Role.objects.get(name="Student")

				try:
					edit_user = CustomUser.objects.get(id=user_id)
					if Volunteer_Registration.objects.filter(user=edit_user):
						registration = Volunteer_Registration.objects.get(user=edit_user)
					elif Staff_Registration.objects.filter(user=edit_user):
						registration = Staff_Registration.objects.get(user=edit_user)
					elif Student_Registration.objects.filter(user=edit_user):
						registration = Student_Registration.objects.get(user=edit_user)
					else:
						registration = None


				except Exception as e:
					print("Exception", e)

		

				if request.method == "POST":
					form = User_Update_Form(request.POST, instance=member, label_suffix='')
					if form.is_valid():
						obj = form.save()
						# form.save_m2m()						
						note = User_Note.objects.create(about_user=obj,
														note="User Account Updated",
														note_by=request.user)

						if reader_role in obj.roles.all():
							
							reader_profile, reader_created = Reader_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])
							if reader_created:
								all_slots = Reading_Session_Day_Time.objects.all()
								reader_profile.add_open_slots(all_slots)
								note2 = User_Note.objects.create(about_user=obj,
														note="Reader Match Profile Created",
														note_by=request.user)
						else:
							reader_profile, reader_created = Reader_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])
							reader_profile.delete()


						if student_role in obj.roles.all():
							
							student_profile, student_created = Student_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])
							if student_created:
								note2 = User_Note.objects.create(about_user=obj,
														note="Student Match Profile Created",
														note_by=request.user)
								
						
						return redirect('site_admin:view_users', role="All")
					else:
						print("errors", form.errors)
						
				else:
					form = User_Update_Form(label_suffix='',
											instance=member)

				context['form'] = form

				return render(request, "site_admin/users/edit_user.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')


def create_user_session_status(user):
	session_status, created = User_Session_Status.objects.get_or_create(
													user=user)


def get_users_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		users = CustomUser.objects.filter(
			Q(first_name__icontains=q)|
			Q(last_name__icontains=q)
			).order_by('username')

		for user in users:
			queryset.append(user)

	return list(set(queryset))

def all_users():
	qs = CustomUser.objects.all().order_by('username')
	return qs

def staff_users():
	staff_role = Role.objects.get(name="Staff")
	qs = staff_role.user_roles.all().order_by('username')
	# CustomUser.objects.filter(roles__in=staff_role)
	return qs

def volunteer_users():
	vol_role = Role.objects.get(name="Volunteer")
	qs = vol_role.user_roles.all().order_by('username')
	# qs = CustomUser.objects.filter(roles__in=vol_role)
	return qs

def student_users():
	stu_role = Role.objects.get(name="Student")
	qs = stu_role.user_roles.all().order_by('username')
	# qs = CustomUser.objects.filter(roles__in=stu_role)
	return qs

def matched_student_users():
	stu_role = Role.objects.get(name="Student")
	qs = CustomUser.objects.filter(roles__in=[stu_role, ],
								student_match_profile__match_needed=False)
	return qs

def unmatched_student_users():
	stu_role = Role.objects.get(name="Student")
	qs = CustomUser.objects.filter(roles__in=[stu_role, ],
								student_match_profile__match_needed=True)
	return qs


def readers_users():
	reader_role = Role.objects.get(name="Reader")
	qs = reader_role.user_roles.all().order_by('username')
	# qs = CustomUser.objects.filter(roles__in=stu_role)
	return qs

def open_readers_users():
	reader_role = Role.objects.get(name="Reader")
	qs = CustomUser.objects.filter(roles__in=[reader_role, ],
								reader_match_profile__open_slot_count__gt=0)
	print("Open QS",  qs.count())
	return qs

def closed_readers_users():
	reader_role = Role.objects.get(name="Reader")
	qs = CustomUser.objects.filter(roles__in=[reader_role, ],
								reader_match_profile__open_slot_count=0)

	print("Full", qs)
	return qs

def has_team():
	vol_role = Role.objects.get(name="Volunteer")
	qs = CustomUser.objects.filter(roles__in=[vol_role, ], team_info__isnull=False)
	print("\n\n\n\nHas Team, qs count")
	print(qs)
	print(qs.count())
	return qs

def needs_team():
	vol_role = Role.objects.get(name="Volunteer")
	qs = CustomUser.objects.filter(roles__in=[vol_role, ],  team_info__isnull=True)
	print("\n\n\n\nNeeds Team, qs count")
	print(qs)
	print(qs.count())
	return qs

def display_users_view(request, role, **kwargs):
	context = {}
	context['page_title'] = "Users"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['members'] = get_users_queryset(query)
						context['count'] = len(context['members'])
						context['role'] = "Matching"
					else:
						context['members'] = all_users()
						context['count'] = all_users().count()
						context['role'] = "All"


				else:
					
					if role == "All":
						context['members'] = all_users()
						context['count'] = context['members'].count()
						context['role'] = "All"
					elif role == "Staff":
						context['members'] = staff_users()
						context['count'] = context['members'].count()
						context['role'] = "Staff"

					elif role == "Student":
						context['members'] = student_users()
						context['count'] = context['members'].count()
						context['role'] = "Student"

					elif role == "Matched":
						context['members'] = matched_student_users()
						context['count'] = context['members'].count()
						context['role'] = "Student"

					elif role == "Unmatched":
						context['members'] = unmatched_student_users()
						context['count'] = context['members'].count()
						context['role'] = "Student"

					elif role == "Volunteer":
						context['members'] = volunteer_users()
						context['count'] = context['members'].count()
						context['role'] = "Volunteer"

					elif role == "Reader":
						context['members'] = readers_users()
						context['count'] = context['members'].count()
						context['role'] = "All Reader"

					elif role == "Open":
						context['members'] = open_readers_users()
						context['count'] = context['members'].count()
						context['role'] = "Open Reader"

					elif role == "Full":
						context['members'] = closed_readers_users()
						context['count'] = context['members'].count()
						context['role'] = "Full Reader"

					elif role == "Volunteer_No_Team":
						context['members'] = needs_team()
						context['count'] = context['members'].count()
						context['role'] = "No Team - Volunteer"

					elif role == "Volunteer_With_Team":
						context['members'] = has_team()
						context['count'] = context['members'].count()
						context['role'] = "Has Team - Volunteer"
						

					

				context['total_users'] = all_users().count()
				context['staff_count'] = staff_users().count()
				context['student_count'] = student_users().count()		
				context['volunteer_count'] = volunteer_users().count()
				context['reader_count'] = readers_users().count()
				context['has_team_count'] = has_team().count()
				context['needs_team_count'] = needs_team().count()

				
				return render(request, "site_admin/users/view_users.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def create_any_user_view(request, **kwargs):
	context = {}
	context['page_title'] = "Create User"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				programs = Program.objects.filter(name="eBookBuddy")

				if request.method == "POST":
					form = Create_Any_User_Form(request.POST, label_suffix='')
					if form.is_valid():
						obj = form.save()
						form.save_m2m()						
						note = User_Note.objects.create(about_user=obj,
														note="User Account Created",
														note_by=request.user)
						content_text = "Username: " + obj.username

						# registration.user = obj
						# registration.save()
						# copy_image(registration)
						create_avatar(obj)
						create_user_session_status(obj)
						
						return redirect('site_admin:view_users', role="All")
					else:
						print("errors", form.errors)
						
				else:
					form = Create_Any_User_Form(label_suffix='',
						initial={
								'is_approved': True,
								'programs': programs,										
								})

				context['form'] = form

				return render(request, "site_admin/users/create_user.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def registration_create_staff_user_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Create Staff User"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				registration = Staff_Registration.objects.get(id=registration_id)
				context['registration'] = registration
				staff_role = Role.objects.get(name="Staff")
				context['role'] = staff_role
				user_view = User_View.objects.get(name="Staff View")
				programs = Program.objects.filter(name="eBookBuddy")

				if request.method == "POST":
					form = Create_Staff_User_Form(request.POST, label_suffix='')
					if form.is_valid():
						password_change_required = request.POST.get('password_change_required')
						print("PASSWORD CHANGE REQUIRED", password_change_required)
						obj = form.save()
						print("PASSWORD 1", obj.password_change_required)
						form.save_m2m()	
						print("PASSWORD 2", obj.password_change_required)					
						note = User_Note.objects.create(about_user=obj,
														note="User Account Created",
														note_by=request.user)
						content_text = "Username: " + obj.username
						reg_note = Staff_Registration_Note.objects.create(registration=registration,
														name="User Account Created",
														content=content_text ,
														created_user=request.user)
						registration.user = obj
						registration.save()
						print("PASSWORD 3", obj.password_change_required)	

						reader_role = Role.objects.get(name="Reader")
						if reader_role in obj.roles.all():
							
							reader_profile, created = Reader_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])
							all_slots = Reading_Session_Day_Time.objects.all()
							reader_profile.add_open_slots(all_slots)
								
							content_text = "No Available Slots in Registration"
							reg_note2 = Staff_Registration_Note.objects.create(registration=registration,
														name="Reader Match Profile Created",
														content=content_text ,
														created_user=request.user)

						copy_image(registration)
						print("PASSWORD 4", obj.password_change_required)	
						create_avatar(obj)
						print("PASSWORD 5", obj.password_change_required)	
						create_user_session_status(obj)
						print("PASSWORD 6", obj.password_change_required)	
						
						return redirect('site_admin:registrations_staff', search_title="All")
					else:
						print("errors", form.errors)
						
				else:					
					suggested = registration.first_name.replace(" ", "")
					print("Suggested 1", suggested)
					if CustomUser.objects.filter(username = suggested).exists():
						print("Plain First Name Exists", suggested)
						print("Get a second one")
						suggested = registration.first_name.replace(" ", "") + registration.last_name.capitalize()[0]

					if CustomUser.objects.filter(username = suggested).exists():
						print("Second ChoiceExists", suggested)
						print("Get a third one")
						suggested = registration.first_name.replace(" ", "") + str(registration.dob.year)
						print("The")
					if CustomUser.objects.filter(username = suggested).exists():
						print("Third ChoiceExists", suggested)
						print("Get a 4th one")
						suggested = registration.first_name.replace(" ", "") + registration.last_name.capitalize()[0] + str(registration.dob.year)

					if CustomUser.objects.filter(username = suggested).exists():
						suggested = ""

					form = Create_Staff_User_Form(label_suffix='',
						initial={'roles': [staff_role,],
								'user_view':user_view,
								'username': suggested,
								'first_name': registration.first_name,
								'last_name': registration.last_name,
								'email': registration.email,
								'password1': "buddystaff",
								'password2': "buddystaff",
								'is_approved': True,
								'programs': programs,
										
								})

				context['form'] = form

				return render(request, "site_admin/users/create_staff_user.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def staff_status_application_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Staff Review"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				context = additional_context_all(context)
				
				registration = Staff_Registration.objects.get(id=registration_id)
				context['page_title'] ="Staff: " + registration.full_name()
				# send_text_message(str(registration.phone), registration.full_name())	
				context['registration'] = registration

				context['reg_form'] = Staff_Registration_Display_Form(instance=registration)
				if request.method == "POST":
					note_form = Staff_Registration_Note_Form(request.POST, label_suffix='')
					if 'add_note' in request.POST:
						print("add_note", request.POST.get('registration'))						
						if note_form.is_valid():
							new_note = note_form.save()											
							return redirect('site_admin:staff_review', registration_id=registration.id)
						else:
							print("errors", note_form.errors)
						
				else:
					note_form = Staff_Registration_Note_Form(label_suffix='',
					initial={
							'registration': registration,
							'name': "Staff Review Note",
							'created_user': request.user,								
							})

				context['note_form'] = note_form

				return render(request, "site_admin/registrations/staff_review.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def registration_create_volunteer_user_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Create Volunteer User"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				registration = Volunteer_Registration.objects.get(id=registration_id)
				context['registration'] = registration
				status = registration.volunteer_registration_status
				context['status'] = status
				vol_role = Role.objects.get(name="Volunteer")
				reader_role = Role.objects.get(name="Reader")
				context['role'] = vol_role
				user_view = User_View.objects.get(name="Reader Only View")
				programs = Program.objects.filter(name="eBookBuddy")

				if request.method == "POST":
					form = Create_Volunteer_User_Form(request.POST, label_suffix='')
					if form.is_valid():
						password_change_required = request.POST.get('password_change_required')
						print("PASSWORD CHANGE REQUIRED", password_change_required)
						obj = form.save()
						print("PASSWORD 1", obj.password_change_required)
						form.save_m2m()	
						print("PASSWORD 2", obj.password_change_required)					
						note = User_Note.objects.create(about_user=obj,
														note="User Account Created",
														note_by=request.user)
						content_text = "Username: " + obj.username
						reg_note = Volunteer_Registration_Note.objects.create(registration=registration,
														name="User Account Created",
														content=content_text ,
														created_user=request.user)
						registration.user = obj
						registration.save()

						team_info, created = User_Team_Info.objects.get_or_create(user=obj)

						if reader_role in obj.roles.all():
							reader_profile, created = Reader_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])
							all_slots = Reading_Session_Day_Time.objects.all()
							reader_profile.add_open_slots(all_slots)

							content_text = "Available Slots Listed in Registration"
							reg_note2 = Volunteer_Registration_Note.objects.create(registration=registration,
														name="Reader Match Profile Created",
														content=content_text ,
														created_user=request.user)

						copy_image(registration)					
						create_avatar(obj)
						create_user_session_status(obj)
					
						
						return redirect('site_admin:registrations_volunteers', search_title="All")
					else:
						print("errors", form.errors)
						
				else:
					suggested = registration.first_name.replace(" ", "")
					print("Suggested 1", suggested)
					if CustomUser.objects.filter(username = suggested).exists():
						print("Plain First Name Exists", suggested)
						print("Get a second one")
						suggested = registration.first_name.replace(" ", "") + registration.last_name.capitalize()[0]

					if CustomUser.objects.filter(username = suggested).exists():
						print("Second ChoiceExists", suggested)
						print("Get a third one")
						suggested = registration.first_name.replace(" ", "") + str(registration.dob.year)
						print("The")
					if CustomUser.objects.filter(username = suggested).exists():
						print("Third ChoiceExists", suggested)
						print("Get a 4th one")
						suggested = registration.first_name.replace(" ", "")+ registration.last_name.capitalize()[0] + str(registration.dob.year)

					if CustomUser.objects.filter(username = suggested).exists():
						suggested = ""

					form = Create_Volunteer_User_Form(label_suffix='',
						initial={'roles': [vol_role, reader_role],
								'user_view':user_view,
								'username': suggested,
								'first_name': registration.first_name,
								'last_name': registration.last_name,
								'email': registration.email,
								'password1': "ebookbuddy",
								'password2': "ebookbuddy",
								'is_approved': True,
								'programs': programs,
										
								})

				context['form'] = form

				return render(request, "site_admin/users/create_volunteer_user.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')


def copy_image(registration):
	# _, ext = os.path.splitext(registration.cropped_profile_image.path)
	name = registration.user.username + ".png"
	registration.user.profile_img.save(
	name,
	content=ContentFile(registration.cropped_profile_image.read()),
	save=True
	)

def create_avatar(user):
	bg_color=(250, 213, 165)
	text_color = "black"

	student_bg_color =(24, 153, 104)
	vol_bg_color = (30, 129, 176)
	staff_bg_color = (171, 189, 192)

	user_roles = user.roles.all()
	vol_role = Role.objects.get(name="Volunteer")
	student_role = Role.objects.get(name="Student")
	staff_role = Role.objects.get(name="Staff")

	if staff_role in user_roles:
		bg_color = staff_bg_color

	elif student_role in user_roles:
		bg_color = student_bg_color

	elif vol_role in user_roles:
		bg_color = vol_bg_color

	

	if user.avatar_img:
		user.avatar_img.delete()
		user.save()

	font_path = "static/fonts/consolab.ttf"
	W, H = (200,200)
	img = Image.new('RGBA', (W,H), color = bg_color)
	d = ImageDraw.Draw(img)
	font = ImageFont.truetype(font_path, size=120)
	letters = user.first_name[0].upper() + user.last_name[0].upper()
	w,h = font.getsize(letters)
	d.text(((W-w)/2,(H-h)/2.2), letters, fill=text_color, font=font, stroke_width=1, stroke_fill=(78, 79, 79))

	ava_io = BytesIO() 
	file_name = user.username +"-avatar.png" 

	img.save(ava_io, 'png', quality=85) # save image to BytesIO object

	avatar = File(ava_io, file_name)
	user.avatar_img = avatar
	user.save()


def format_date_str(date):
		date_str = date.strftime("%m/%d/%Y - %I:%M%p")
		return date_str


def format_time_str(time):
	str_time = time.strftime("%I:%M %p") 
	first = str_time.split(":")[0].replace("0","")
	second = str_time.split(":")[1]
	time_string = first + ":" + second

	return time_string

def registration_create_student_user_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Create Student User"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				registration = Student_Registration.objects.get(id=registration_id)
				parent_registration = registration.parent
				context['registration'] = registration
				context['parent'] = parent_registration
				status = registration.student_registration_status
				context['status'] = status
				student_role = Role.objects.get(name="Student")
				context['role'] = student_role
				user_view = User_View.objects.get(name="Student View")
				programs = Program.objects.filter(name="eBookBuddy")

				if request.method == "POST":
					form = Create_Student_User_Form(request.POST, label_suffix='')
					if form.is_valid():
						# obj = form.save(commit=False)
						obj = form.save()
						form.save_m2m()
						# obj.roles.add(student_role)
						# for item in programs:							
						# 	obj.programs.add(item)
						note = User_Note.objects.create(about_user=obj,
														note="User Account Created",
														note_by=request.user)
						content_text = "Username: " + obj.username
						reg_note = Student_Registration_Note.objects.create(registration=registration,
														name="User Account Created",
														content=content_text ,
														created_user=request.user)
						registration.user = obj
						registration.save()
						if student_role in obj.roles.all():
							student_profile, created = Student_Match_Profile.objects.get_or_create(
												user=obj, semester=context['active_semester'])

							content_text = "Available Slots Listed in Registration"
							reg_note2 = Student_Registration_Note.objects.create(registration=registration,
														name="Student Match Profile Created",
														content=content_text ,
														created_user=request.user)
						copy_image(registration)
						create_avatar(obj)
						create_user_session_status(obj)
						
						return redirect('site_admin:registrations_students', search_title="All")
					else:
						print("errors", form.errors)
						
				else:
					suggested = registration.child_first_name.replace(" ", "")
					print("Suggested 1", suggested)
					if CustomUser.objects.filter(username = suggested).exists():
						print("Plain First Name Exists", suggested)
						print("Get a second one")
						suggested = registration.child_first_name.replace(" ", "") + registration.child_last_name.capitalize()[0]

					if CustomUser.objects.filter(username = suggested).exists():
						print("Second ChoiceExists", suggested)
						print("Get a third one")
						suggested = registration.child_first_name.replace(" ", "") + str(registration.dob.year)
						print("The")
					if CustomUser.objects.filter(username = suggested).exists():
						print("Third ChoiceExists", suggested)
						print("Get a 4th one")
						suggested = registration.child_first_name.replace(" ", "") + registration.child_last_name.capitalize()[0] + str(registration.dob.year)

					if CustomUser.objects.filter(username = suggested).exists():
						suggested = ""


					form = Create_Student_User_Form(label_suffix='',
						initial={'roles': [student_role,],
								'user_view':user_view,
								'username': suggested,
								'first_name': registration.child_first_name,
								'last_name': registration.child_last_name,
								'password1': "readbook",
								'password2': "readbook",
								'is_approved': True,
								'programs': programs,
										
								})

				context['form'] = form

				return render(request, "site_admin/users/create_student_user.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')



def student_status_application_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Student Review"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:	

				context = additional_context_all(context)
				context['session_day_choices'] = Session_Day_Option.objects.filter(active=True)
				context['session_time_choices'] = Session_Time_Option.objects.filter(active=True)
				context['session_meeting_choices'] = Session_Meeting_Option.objects.filter(active=True)
			
				registration = Student_Registration.objects.get(id=registration_id)
				context['page_title'] ="S: " + registration.full_name()
				# send_text_message(str(registration.phone), registration.full_name())	
				context['registration'] = registration
				status = registration.student_registration_status
				parent = registration.parent
				context['parent'] = parent
				initial_approved = status.approved_to_match
				initial_waitlist = status.waitlist
				context['status'] = status
				# context['parent_form'] = Parent_Registration_Display_Form(instance=parent)
				# context['reg_form'] = Student_Registration_Display_Form(instance=registration)
				if request.method == "POST":
					form = Student_Status_Form(request.POST, instance=status, label_suffix='')
					if 'update_status' in request.POST:						
						if form.is_valid():
							obj = form.save(commit=False)
							obj.last_updated_by = request.user


							if not initial_approved and obj.approved_to_match:
								obj.approved_by = request.user
								obj.date_approved = timezone.now()

							elif initial_approved and not obj.approved_to_match:
								obj.approved_by = None	
								obj.date_approved = None

							if not initial_waitlist and obj.waitlist:
								obj.waitlist_by = request.user
								obj.date_waitlist = timezone.now()							

							elif initial_waitlist and not obj.waitlist:
								obj.waitlist_by = None	
								obj.date_waitlist = None

							obj = form.save()
							
							return redirect('site_admin:student_review', registration_id=registration.id)
						else:
							print("errors", form.errors)
					
					note_form = Student_Registration_Note_Form(request.POST, label_suffix='')
					
					if 'add_note' in request.POST:
						print("add_note", request.POST.get('registration'))						
						if note_form.is_valid():
							new_note = note_form.save()											
							return redirect('site_admin:student_review', registration_id=registration.id)
						else:
							print("errors", note_form.errors)
						
				else:
					form = Student_Status_Form(label_suffix='',
						initial={'registration': status.registration,
								'responsive': status.responsive,
								'confirm': status.confirm,
								'tech_screening': status.tech_screening,
								'approved_to_match': status.approved_to_match,
								'approved_by': status.approved_by,
								'date_approved': status.date_approved,
								'date_created': status.date_created,
								'last_updated_by': status.last_updated_by,
								'last_updated': status.last_updated,
								'waitlist': status.waitlist,
								'waitlist_by': status.waitlist_by,
								'date_waitlist': status.date_waitlist,
								'waitlist_reason': status.waitlist_reason,
								})

					note_form = Student_Registration_Note_Form(label_suffix='',
					initial={
							'registration': registration,
							'name': "Student Review Note",
							'created_user': request.user,								
							})

				context['form'] = form
				context['note_form'] = note_form				

				return render(request, "site_admin/registrations/student_review.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def get_stu_regs_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		users = Student_Registration.objects.filter(
			Q(child_first_name__icontains=q)|
			Q(child_last_name__icontains=q)|
			Q(parent__parent_first_name__icontains=q)|
			Q(school__name__icontains=q)|
			Q(other_school__icontains=q)|
			Q(parent__parent_last_name__icontains=q)|
			Q(parent__email__icontains=q)).order_by('date_created')

		for user in users:
			queryset.append(user)

	return list(set(queryset))

def total_student_registrations():
	qs = Student_Registration.objects.all()
	return qs

def approved_to_match_stu_regs():
	qs = Student_Registration.objects.filter(
							student_registration_status__approved_to_match = True,
							student_registration_status__waitlist = False)
	return qs

def waitlist_stu_regs():
	qs = Student_Registration.objects.filter(student_registration_status__waitlist = True)
	return qs

def pending_stu_regs():
	qs = Student_Registration.objects.filter(
							student_registration_status__approved_to_match = False,
							student_registration_status__waitlist = False)
	return qs

def registrations_students_view(request, search_title, **kwargs):
	context = {}
	context['page_title'] = "All Students Registrations"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['regs'] = get_stu_regs_queryset(query)
						context['count'] = len(context['regs'])
						context['search_title'] = "Matching"
					else:
						context['regs'] = total_student_registrations()
						context['count'] = total_student_registrations().count()
						context['search_title'] = "All"


				else:
					
					if search_title == "All":
						context['regs'] = total_student_registrations()
						context['count'] = total_student_registrations().count()
						context['search_title'] = "All"
					elif search_title == "Pending":
						context['regs'] = pending_stu_regs()
						context['count'] = pending_stu_regs().count()
						context['search_title'] = "Pending"

					elif search_title == "Approved":
						context['regs'] = approved_to_match_stu_regs()
						context['count'] = approved_to_match_stu_regs().count()
						context['search_title'] = "Approved"

					elif search_title == "Waitlist":
						context['regs'] = waitlist_stu_regs()
						context['count'] = waitlist_stu_regs().count()
						context['search_title'] = "Waitlist"

					

				context['total_stu_registrations'] = total_student_registrations().count()
				context['stu_pending_count'] = pending_stu_regs().count()
				context['stu_approved_count'] = approved_to_match_stu_regs().count()		
				context['stu_waitlist_count'] = waitlist_stu_regs().count()

				
				return render(request, "site_admin/registrations/all_student.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def eng_label(fieldname, for_form):
	label = Question.objects.get(for_form__name=for_form, field_name=fieldname)
	# print("eng_text", label.eng_text)
	return label.eng_text

def total_volunteer_registrations():
	qs = Volunteer_Registration.objects.all()
	return qs

def approved_to_match_vol_regs():
	qs = Volunteer_Registration.objects.filter(
							volunteer_registration_status__approved_to_match = True,
							volunteer_registration_status__denied = False)
	return qs

def denied_vol_regs():
	qs = Volunteer_Registration.objects.filter(volunteer_registration_status__denied = True)
	return qs

def pending_vol_regs():
	qs = Volunteer_Registration.objects.filter(
							volunteer_registration_status__approved_to_match = False,
							volunteer_registration_status__denied = False)
	return qs


def get_vol_regs_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		users = Volunteer_Registration.objects.filter(
			Q(first_name__icontains=q)|
			Q(last_name__icontains=q)|
			Q(email__icontains=q)).order_by('date_submitted')

		for user in users:
			queryset.append(user)

	return list(set(queryset))


def volunteer_status_application_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Review"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				context = additional_context_all(context)
				context['agree_requirements_initials'] = eng_label('agree_requirements_initials', 'Volunteer Registration')
				context['statements_true_initials'] = eng_label('statements_true_initials', 'Volunteer Registration')
				context['remove_volunteers_initials'] = eng_label('remove_volunteers_initials', 'Volunteer Registration')
				context['convicted'] = eng_label('convicted', 'Volunteer Registration')
				context['charges_pending'] = eng_label('charges_pending', 'Volunteer Registration')
				context['refused_participation'] = eng_label('refused_participation', 'Volunteer Registration')
				context['session_day_choices'] = Session_Day_Option.objects.filter(active=True)
				context['session_time_choices'] = Session_Time_Option.objects.filter(active=True)
				context['session_meeting_choices'] = Session_Meeting_Option.objects.filter(active=True)
				context['team_meeting_times'] = Team_Meeting_Time.objects.filter(active=True)
				registration = Volunteer_Registration.objects.get(id=registration_id)
				# send_text_message(str(registration.phone), registration.full_name())	
				context['registration'] = registration
				context['page_title'] ="V: " + registration.full_name()
				status = registration.volunteer_registration_status
				initial_approved = status.approved_to_match
				initial_denied = status.denied
				context['status'] = status
				# context['reg_form'] = Volunteer_Registration_Display_Form(instance=registration)
				if request.method == "POST":
					form = Volunteer_Status_Form(request.POST, instance=status, label_suffix='')
					if 'update_status' in request.POST:
						# form = Volunteer_Status_Form(request.POST, instance=status, label_suffix='')
						if form.is_valid():
							obj = form.save(commit=False)
							obj.last_updated_by = request.user
							if not initial_approved and obj.approved_to_match:
								print("Was not approved but now is")
								obj.approved_by = request.user
								obj.date_approved = timezone.now()
							elif initial_approved and not obj.approved_to_match:
								print("Was approved but now is not")
								obj.approved_by = None	
								obj.date_approved = None

							if not initial_denied and obj.denied:
								obj.denied_by = request.user
								obj.date_denied = timezone.now()
								obj.approved_by = None
								obj.date_approved = None
								obj.approved_to_match = False

							elif initial_denied and not obj.denied:
								obj.denied_by = None	
								obj.date_denied = None

							obj = form.save()

							if registration.user:
								print("User Associated with registration")
								if Reader_Match_Profile.objects.filter(user=registration.user).exists():
									reader_match_profile = Reader_Match_Profile.objects.get(user=registration.user)
									print("reader_match_profile", reader_match_profile)
									if not obj.approved_to_match:
										reader_match_profile.delete()

								else:
									print("No Match Profile")
									if obj.approved_to_match:
										print("Approved")
										reader_role = Role.objects.get(name='Reader')
										if reader_role in registration.user.roles.all():
											print("is reader")
											reader_profile, reader_created = Reader_Match_Profile.objects.get_or_create(
													user=registration.user, semester=context['active_semester'])
											if reader_created:
												all_slots = Reading_Session_Day_Time.objects.all()
												reader_profile.add_open_slots(all_slots)
												note2 = User_Note.objects.create(about_user=registration.user,
																		note="Reader Match Profile Created",
																		note_by=request.user)
							else:
								print("No User")
							
							return redirect('site_admin:volunteer_review', registration_id=registration.id)
						else:
							print("errors", form.errors)

					note_form = Volunteer_Registration_Note_Form(request.POST, label_suffix='')
					if 'add_note' in request.POST:
						print("add_note", request.POST.get('registration'))						
						if note_form.is_valid():
							new_note = note_form.save()											
							return redirect('site_admin:volunteer_review', registration_id=registration.id)
						else:
							print("errors", note_form.errors)
						
				else:
					form = Volunteer_Status_Form(label_suffix='',
						initial={'registration': status.registration,
								'tech_screening': status.tech_screening,
								'online_training_completed': status.online_training_completed,
								'video_uploaded': status.video_uploaded,
								'video_reviewed': status.video_reviewed,
								'live_screening_passed': status.live_screening_passed,
								'orientation': status.orientation,
								'reference_check': status.reference_check,
								'approved_to_match': status.approved_to_match,
								'approved_by': status.approved_by,
								'date_approved': status.date_approved,
								'date_created': status.date_created,
								'last_updated_by': status.last_updated_by,
								'last_updated': status.last_updated,
								'denied': status.denied,
								'denied_by': status.denied_by,
								'date_denied': status.date_denied,
								'denied_reason': status.denied_reason,
								})

					note_form = Volunteer_Registration_Note_Form(label_suffix='',
					initial={
							'registration': registration,
							'name': "Volunteer Review Note",
							'created_user': request.user,								
							})

				context['form'] = form
				context['note_form'] = note_form

				return render(request, "site_admin/registrations/volunteer_review.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def get_staff_regs_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		users = Staff_Registration.objects.filter(
			Q(first_name__icontains=q)|
			Q(last_name__icontains=q)|
			Q(email__icontains=q)).order_by('date_submitted')

		for user in users:
			queryset.append(user)

	return list(set(queryset))

def total_staff_registrations():
	qs = Staff_Registration.objects.all()
	return qs

def staff_needs_username():
	qs = Staff_Registration.objects.filter(user__isnull = True)
	return qs

def staff_has_username():
	qs = Staff_Registration.objects.filter(user__isnull = False)
	return qs

def registrations_staff_view(request, search_title, **kwargs):
	context = {}
	context['page_title'] = "All Staff Registrations"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['regs'] = get_staff_regs_queryset(query)
						context['count'] = len(context['regs'])
						context['search_title'] = "Matching"
					else:
						context['regs'] = total_staff_registrations()
						context['count'] = total_staff_registrations().count()
						context['search_title'] = "All"

				else:
					
					if search_title == "All":
						context['regs'] = total_staff_registrations()
						context['count'] = total_staff_registrations().count()
						context['search_title'] = "All"
					elif search_title == "Needs Username":
						context['regs'] = staff_needs_username()
						context['count'] = staff_needs_username().count()
						context['search_title'] = "Needs Username"

					elif search_title == "Has Username":
						context['regs'] = staff_has_username()
						context['count'] = staff_has_username().count()
						context['search_title'] = "Has Username"

					print(context['regs'])

				context['total_staff_registrations'] = total_staff_registrations().count()
				context['has_username'] = staff_has_username().count()
				context['needs_username'] = staff_needs_username().count()	

			
				return render(request, "site_admin/registrations/all_staff.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def registrations_volunteers_view(request, search_title, **kwargs):
	context = {}
	context['page_title'] = "All Volunteer Registrations"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['regs'] = get_vol_regs_queryset(query)
						context['count'] = len(context['regs'])
						context['search_title'] = "Matching"
					else:
						context['regs'] = total_volunteer_registrations()
						context['count'] = total_volunteer_registrations().count()
						context['search_title'] = "All"

				else:
					
					if search_title == "All":
						context['regs'] = total_volunteer_registrations()
						context['count'] = total_volunteer_registrations().count()
						context['search_title'] = "All"
					elif search_title == "Pending":
						context['regs'] = pending_vol_regs()
						context['count'] = pending_vol_regs().count()
						context['search_title'] = "Pending"

					elif search_title == "Approved":
						context['regs'] = approved_to_match_vol_regs()
						context['count'] = approved_to_match_vol_regs().count()
						context['search_title'] = "Approved"

					elif search_title == "Denied":
						context['regs'] = denied_vol_regs()
						context['count'] = denied_vol_regs().count()
						context['search_title'] = "Denied"

					print(context['regs'])

				context['total_vol_registrations'] = total_volunteer_registrations().count()
				context['vol_pending_count'] = pending_vol_regs().count()
				context['vol_approved_count'] = approved_to_match_vol_regs().count()		
				context['vol_denied_count'] = denied_vol_regs().count()

			
				return render(request, "site_admin/registrations/all_volunteer.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def additional_context_all(context):
	active_semester = get_active_semester()
	context['active_semester'] = active_semester

	return context

def get_updating_status():
	updating_now = Program_Status.objects.filter(updating=True)
	if updating_now.count() == 0:
		return False
	else:
		return True

def get_active_semester():
	return Program_Semester.objects.get(active_semester = True)

def site_admin_home_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Site Admin Home"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				
				context = additional_context_all(context)
				context['registrations_open_volunteers'] = context['active_semester'].accepting_volunteers
				context['registrations_open_student'] = context['active_semester'].accepting_students

				if context['active_semester'].accepting_volunteers:
					context['total_vol_registrations'] = total_volunteer_registrations().count()
					context['vol_pending_count'] = pending_vol_regs().count()
					context['vol_approved_count'] = approved_to_match_vol_regs().count()		
					context['vol_denied_count'] = denied_vol_regs().count()
				if context['active_semester'].accepting_students:
					context['total_stu_registrations'] = total_student_registrations().count()
					context['stu_pending_count'] = pending_stu_regs().count()
					context['stu_approved_count'] = approved_to_match_stu_regs().count()		
					context['stu_waitlist_count'] = waitlist_stu_regs().count()


				return render(request, "site_admin/site_admin_home.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def display_login_logout_logs_view(request, search_title, **kwargs):
	context = {}
	context['page_title'] = "Session Logs"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user

			all_logs = Login_Logout_Log.objects.all()
			# rooms = Room.objects.all()
			# for room in rooms:
			# 	participants, created = Room_Participants.objects.get_or_create(room=room)
			
			# breakout, created = Room_Type.objects.get_or_create(name="Breakout", letter = "B")
			# num_of_breakouts = 30
			# for x in range(1, num_of_breakouts + 1):
			# 	name = "Breakout " + str(x)
			# 	room, created = Room.objects.get_or_create(name=name, number = x,  room_type=breakout)

			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['logs'] = get_users_queryset(query)
						context['count'] = len(context['members'])
						context['search_title'] = "Matching"
					else:
						context['logs'] = all_users()
						context['count'] = all_users().count()
						context['search_title'] = "All"


				else:
					
					if search_title == "All":
						context['logs'] = all_logs
						context['count'] = all_logs.count()
						context['search_title'] = "All"
					# elif search_title == "Staff":
					# 	context['members'] = staff_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Staff"

					# elif search_title == "Student":
					# 	context['members'] = student_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Student"

					# elif search_title == "Matched":
					# 	context['members'] = matched_student_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Student"

					# elif role == "Unmatched":
					# 	context['members'] = unmatched_student_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Student"

					# elif role == "Volunteer":
					# 	context['members'] = volunteer_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Volunteer"

					# elif role == "Reader":
					# 	context['members'] = readers_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "All Reader"

					# elif role == "Open":
					# 	context['members'] = open_readers_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Open Reader"

					# elif role == "Full":
					# 	context['members'] = closed_readers_users()
					# 	context['count'] = context['members'].count()
					# 	context['role'] = "Full Reader"
						

					

				context['total_count'] = all_logs.count()
				# context['staff_count'] = staff_users().count()
				# context['student_count'] = student_users().count()		
				# context['volunteer_count'] = volunteer_users().count()
				# context['reader_count'] = readers_users().count()

				
				return render(request, "site_admin/user_info/session_logs.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def download_student_registrations_csv(request):
	response = HttpResponse(content_type='text/csv')
	today = timezone.localtime(timezone.now()).date()
	date = today.strftime("%m-%d-%Y")
	filename = "Student_Registrations_" + date + ".csv"
	all_stu_regs = Student_Registration.objects.all()

	response['Content-Disposition'] = 'attachment; filename=' + filename
	writer = csv.writer(response)

	fields = Student_Registration._meta.get_fields()
	parent_fields = Parent_Registration._meta.get_fields()
	status_fields = Student_Registration_Status._meta.get_fields()
	# print(type(fields))

	# for field in parent_fields:
	# 	print(field.name)
	
	# for field in status_fields:
	# 	print(field.name)
	# 	# header.append(field.name)

	header = [
			# 'student_registration_status',
			# 'notes',
			# 'program',
			# 'program_semester',
			# 'cropped_profile_image',
			# 'profile_image',			
			# 'last_updated',
			'id',
			'date_created',			
			'child_first_name',
			'child_last_name',
						
			'dob',
			'gender',
			'ethnicity',
			'current_grade',
			'school',
			'other_school',
			'prior_participation',
			'primary_language',
			'other_primary_language',
			'secondary_language',
			'other_secondary_language',

			'reading_level',			
			'child_comment',
			'characteristics',

			'internet',
			'computer',
			'session_device',
			'other_session_device',	
			'registration_language',
			'parent',
			'relationship_to_child',
			'email',
			'phone',
			'flexible_schedule',
			'parent_can_help',
			'help_name',
			'help_phone',
			'help_relationship',	

			'country',
			'address',
			'city',
			'state',
			'zip_code',			
			'county',	

			'session_choices',
			'additional_info',

			'consent_liability_initials',
			'media_release_initials',	
			

			
			'responsive',
			'confirm',
			'tech_screening',
			'approved_to_match',
			'approved_by',
			'date_approved',
			# 'date_created',
			'last_updated_by',
			'last_updated',
			'waitlist',
			'waitlist_by',
			'date_waitlist',
			'waitlist_reason',
			'overall_status',

			# No Status
			# 'id',
			# 'registration',			
			


			# No Parent
			# 'id',
			# 'registration_language',
			# 'parent_first_name',
			# 'parent_last_name',
			# 'date_created',
			# 'last_updated',
			# 'parent_info',
			# 'parent_reg_ip',
			# 'notes',	
	]

	writer.writerow(header)

	for stu in all_stu_regs:
		data = Student_Registration_Serializer(stu).data
		field_vals = []
		# print(type(data))
		# for k, v in data.items():
		# 	print(k, v)

		for item in header:
			try:
				if item == "date_created":
					val = format_date_str(stu.date_created)
					# val = data[item].split("T")[0]
					field_vals.append(val)
				elif item == "registration_language":
					val = stu.registration_language.eng_name
					field_vals.append(val)
				elif item == "parent":
					val = stu.parent.full_name()
					field_vals.append(val)
				elif item == "internet":
					val = stu.parent.internet
					field_vals.append(val)
				elif item == "computer":
					val = stu.parent.computer
					field_vals.append(val)

				elif item == "country":
					val = stu.parent.country
					field_vals.append(val)
				elif item == "county":
					val = stu.parent.county
					field_vals.append(val)
				elif item == "address":
					val = stu.parent.address
					field_vals.append(val)
				elif item == "city":
					val = stu.parent.city
					field_vals.append(val)
				elif item == "state":
					val = stu.parent.state
					field_vals.append(val)
				elif item == "zip_code":
					val = stu.parent.zip_code
					field_vals.append(val)

				elif item == "email":
					val = stu.parent.email
					field_vals.append(val)
				elif item == "phone":
					val = stu.parent.phone_format()
					field_vals.append(val)
				elif item == "flexible_schedule":
					val = stu.parent.flexible_schedule
					field_vals.append(val)
				elif item == "parent_can_help":
					val = stu.parent.parent_can_help
					field_vals.append(val)
				elif item == "help_name":
					val = stu.parent.help_name
					field_vals.append(val)
				elif item == "help_phone":
					val = stu.parent.help_phone_format()
					field_vals.append(val)
				elif item == "help_relationship":
					val = stu.parent.help_relationship
					field_vals.append(val)

				elif item == "characteristics":
					str_val = ""
					for item in stu.characteristics.all():
						val = item.name
						if item != stu.characteristics.all().last():
							val = val + ", "
						else:
							val = val
						str_val = str_val + val		
					field_vals.append(str_val)

				elif item == "session_choices":
					str_val = ""
					for item in stu.parent.session_choices.all():
						# print(item)
						day_option = item.day_option
						# print(day_option)
						day_str = ""
						for day in day_option.days.all():

							day_str = day_str + day.letter
							# if day != day_option.days.all().last():
						day_str = day_str + "/" + item.time_option.time_string()													
						
						str_val = str_val + day_str
						if item != stu.parent.session_choices.all().last():
							str_val = str_val + ", "										
					field_vals.append(str_val)


				elif item == "additional_info":
					str_val = ""
					for item in stu.parent.additional_info.all():
						val = item.name
						if item != stu.parent.additional_info.all().last():
							val = val + ", "
						else:
							val = val
						str_val = str_val + val		
					field_vals.append(str_val)

				elif item == "consent_liability_initials":
					val = stu.parent.consent_liability_initials
					field_vals.append(val)
				elif item == "media_release_initials":
					val = stu.parent.media_release_initials
					field_vals.append(val)
				
				elif item == "overall_status":
					val = stu.status()
					field_vals.append(val)
				elif item == "tech_screening":
					val = stu.student_registration_status.tech_screening
					field_vals.append(val)
					
				elif item == "responsive":
					val = stu.student_registration_status.responsive
					field_vals.append(val)
				elif item == "confirm":
					val = stu.student_registration_status.confirm
					field_vals.append(val)

				elif item == "approved_to_match":
					val = stu.student_registration_status.approved_to_match
					field_vals.append(val)
				elif item == "waitlist":
					val = stu.student_registration_status.waitlist
					field_vals.append(val)
				elif item == "waitlist_reason":
					val = stu.student_registration_status.waitlist_reason
					field_vals.append(val)
				elif item == "approved_by":
					val = str(stu.student_registration_status.approved_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "waitlist_by":
					val = str(stu.student_registration_status.waitlist_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "last_updated_by":
					val = str(stu.student_registration_status.last_updated_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "date_approved":
					if stu.student_registration_status.date_approved:
						val = format_date_str(stu.student_registration_status.date_approved)
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "date_waitlist":
					if stu.student_registration_status.date_waitlist:
						val = format_date_str(stu.student_registration_status.date_denied)
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "last_updated":
					if stu.student_registration_status.last_updated:
						val = format_date_str(stu.student_registration_status.last_updated)
						field_vals.append(val)
					else:
						field_vals.append("")

				else:					
					val = data[item]
					field_vals.append(val)

			except Exception as e:
				print("Exception", stu, e, item)
				field_vals.append(item)		
		writer.writerow(field_vals)
	return response

def download_volunteer_registrations_csv(request):
	response = HttpResponse(content_type='text/csv')
	today = timezone.localtime(timezone.now()).date()
	date = today.strftime("%m-%d-%Y")
	filename = "Volunteer_Registrations_" + date + ".csv"
	all_vol_regs = Volunteer_Registration.objects.all()

	response['Content-Disposition'] = 'attachment; filename=' + filename
	writer = csv.writer(response)

	fields = Volunteer_Registration._meta.get_fields()
	status_fields = Volunteer_Registration_Status._meta.get_fields()
	# print(type(fields))
	
	# for field in status_fields:
	# 	print(field.name)
		# header.append(field.name)

	header = [
			'id',
			'date_submitted',
			'first_name',
			'last_name',
			'volunteer_type',
			'opportunity_source',
			'social_media_source',
			'person_referral',
			'web_source',
			'previously_paired',
			'student_name',
			'teamleader_name',
			'returning_referred',
			'country',
			'address',
			'city',
			'state',
			'zip_code',
			'county',
			'email',
			'phone',
			'dob',
			'parent_name',
			'parent_email',
			'gender',
			'ethnicity',
			'in_school',
			'current_education_level',
			'current_education_class',
			'current_school',
			'highest_education_level',				
			'fluent_spanish',
			'computer',
			'device_type',
			'children_experience',
			'reason',
			'other_reasons',
			'reason_not_listed',
			'volunteer_other_areas',
			'additional_interests',
			'ref_name_1',
			'ref_email_1',
			'ref_phone_1',
			'ref_relationship_1',
			'ref_name_2',
			'ref_email_2',
			'ref_phone_2',
			'ref_relationship_2',
			'sponsor_child',
			'meeting_times',
			'session_choices',
			'convicted',
			'convicted_text',
			'charges_pending',
			'charges_pending_text',
			'refused_participation',
			'refused_participation_text',
			'agree_requirements_initials',
			'statements_true_initials',
			'remove_volunteers_initials',				
			'full_name_signature',
			'tech_screening',
			'online_training_completed',
			'video_uploaded',
			'video_reviewed',
			'live_screening_passed',
			'orientation',
			'reference_check',
			'approved_to_match',
			'approved_by',
			'date_approved',		
			'denied',
			'denied_by',
			'date_denied',
			'denied_reason',
			'last_updated_by',
			'last_updated',
			'overall_status',			
			# 'vol_reg_ip',		
			# 'volunteer_registration_status',
			# 'notes',				
			# 'program',
			# 'program_semester',	
			# 'cropped_profile_image',
			# 'profile_image',	
	]

	writer.writerow(header)

	for vol in all_vol_regs:
		data = Volunteer_Registration_Serializer(vol).data
		field_vals = []
		# print(type(data))
		# for k, v in data.items():
		# 	print(k, v)

		for item in header:
			try:
				if item == "date_submitted":
					val = format_date_str(vol.date_submitted)
					# val = data[item].split("T")[0]
					field_vals.append(val)
				elif item == "phone":
					val = vol.phone_format()
					field_vals.append(val)

				elif item == "other_reasons":
					str_val = ''
					info = data[item]
					if len(info) > 0:
						for i in info[:-1]:
							str_val = str_val + i + ", "
						str_val = str_val + info[-1]
					field_vals.append(str_val)
				elif item == "additional_interests":
					str_val = ''
					info = data[item]
					if len(info) > 0:
						for i in info[:-1]:
							str_val = str_val + i + ", "
						str_val = str_val + info[-1]
					field_vals.append(str_val)
				elif item == "ref_phone_1":
					val = vol.ref1_phone_format()
					field_vals.append(val)
				elif item == "ref_phone_2":
					val = vol.ref2_phone_format()
					field_vals.append(val)

				elif item == "meeting_times":
					str_val = ""
					for item in vol.meeting_times.all():
						day_val = item.meeting_day.short_name + " - " + format_time_str(item.meeting_time)
						if item != vol.meeting_times.all().last():
							day_val = day_val + ", "
						else:
							day_val = day_val

						str_val = str_val + day_val					
					field_vals.append(str_val)

				elif item == "session_choices":
					str_val = ""
					for item in vol.session_choices.all():
						# print(item)
						day_option = item.day_option
						# print(day_option)
						day_str = ""
						for day in day_option.days.all():

							day_str = day_str + day.letter
							# if day != day_option.days.all().last():
						day_str = day_str + "/" + item.time_option.time_string()													
						
						str_val = str_val + day_str
						if item != vol.session_choices.all().last():
							str_val = str_val + ", "
					# print("Str Val", str_val)					
					field_vals.append(str_val)
				
				elif item == "overall_status":
					val = vol.status()
					field_vals.append(val)
				elif item == "tech_screening":
					val = vol.volunteer_registration_status.tech_screening
					field_vals.append(val)
					
				elif item == "online_training_completed":
					val = vol.volunteer_registration_status.online_training_completed
					field_vals.append(val)
				elif item == "video_uploaded":
					val = vol.volunteer_registration_status.video_uploaded
					field_vals.append(val)
				elif item == "video_reviewed":
					val = vol.volunteer_registration_status.video_reviewed
					field_vals.append(val)
				elif item == "live_screening_passed":
					val = vol.volunteer_registration_status.live_screening_passed
					field_vals.append(val)
				elif item == "orientation":
					val = vol.volunteer_registration_status.orientation
					field_vals.append(val)
				elif item == "reference_check":
					val = vol.volunteer_registration_status.reference_check
					field_vals.append(val)
				elif item == "approved_to_match":
					val = vol.volunteer_registration_status.approved_to_match
					field_vals.append(val)
				elif item == "denied":
					val = vol.volunteer_registration_status.denied
					field_vals.append(val)
				elif item == "denied_reason":
					val = vol.volunteer_registration_status.denied_reason
					field_vals.append(val)
				elif item == "approved_by":
					val = str(vol.volunteer_registration_status.approved_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "denied_by":
					val = str(vol.volunteer_registration_status.denied_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "last_updated_by":
					val = str(vol.volunteer_registration_status.last_updated_by)
					if val != "None":
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "date_approved":
					if vol.volunteer_registration_status.date_approved:
						val = format_date_str(vol.volunteer_registration_status.date_approved)
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "date_denied":
					if vol.volunteer_registration_status.date_denied:
						val = format_date_str(vol.volunteer_registration_status.date_denied)
						field_vals.append(val)
					else:
						field_vals.append("")
				elif item == "last_updated":
					if vol.volunteer_registration_status.last_updated:
						val = format_date_str(vol.volunteer_registration_status.last_updated)
						field_vals.append(val)
					else:
						field_vals.append("")

				else:					
					val = data[item]
					field_vals.append(val)

			except Exception as e:
				print("Exception", vol, e, item)
				field_vals.append(item)		
		writer.writerow(field_vals)
	return response