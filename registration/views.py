from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from registration.forms import Volunteer_Registration_Form
from registration.forms import Student_Registration_Form
from registration.forms import Staff_Registration_Form
from registration.forms import Pre_Registration_Form
from registration.forms import Parent_Registration_Form
from registration.forms import Volunteer_Video_Form, Volunteer_Testing_Form
from buddy_program_data.models import Session_Day_Option, Session_Time_Option
from buddy_program_data.models import Session_Meeting_Option, Ethnicity
from buddy_program_data.models import Form_Message, Question, Server_Schedule
from buddy_program_data.models import Application_Recipient
from buddy_program_data.models import Program_Semester, Program_Form, Answer_Type
from buddy_program_data.models import Language, Parent_Additional_Information
from buddy_program_data.models import Student_Characteristic
from users.models import CustomUser, Program
from registration.models import Volunteer_Registration, Student_Registration
from registration.models import Parent_Registration, Staff_Registration
from registration.models import Volunteer_Registration_IP_Info, Parent_Registration_IP_Info
from registration.models import Volunteer_Registration_Status
from registration.models import Volunteer_Registration_Note, Registration_Error
from registration.models import Student_Registration_Status
from registration.models import Student_Registration_Note, Parent_Registration_Note
from registration.models import Staff_Registration_Note, Staff_Registration_IP_Info

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64
import requests
from django.core import files
from django.http import JsonResponse, HttpResponse

import logging
import boto3

from botocore.client import Config
from botocore.exceptions import ClientError
import numpy as np
import urllib
from django.core.files.base import ContentFile

import socket
import geoip2.database

from django.core import mail
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string
from django.utils.html import strip_tags

DEV = True
SEND_EMAILS = True

def volunteer_testing_times_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Tech Testing"
	context['display_login_logout']= False	
	context['load_vol_testing_scripts'] = True

	todays_date = timezone.localtime(timezone.now()).date()
	context['todays_date'] = todays_date

	server_schedule = Server_Schedule.objects.get(name="Volunteer Testing")
	server_times = server_schedule.schedule.filter(date__gte=todays_date)
	context['server_times'] = server_times
	context['offset'] = server_schedule.offset
	if server_times.filter(date=todays_date).exists():
		todays_time = server_times.get(date = todays_date)
		context['todays_time'] = todays_time
		context['today_time_start'] = todays_time.start_time
		context['today_time_end'] = todays_time.end_time
		context['server_open_today'] = True
		time_now = timezone.localtime(timezone.now()).time()
		print("Time Now", time_now)
		if time_now >= todays_time.start_time and time_now < todays_time.end_time:
			context['display_form'] = True
			print("Show Form")
		else:
			context['display_form'] = False
			print("Hide Form")

	else:
		todays_time = None
		context['todays_time'] = todays_time
		context['today_time_start'] = None
		context['today_time_end'] = None
		context['display_form'] = False
		context['server_open_today'] = False


	if request.method == "POST":
		form = Volunteer_Testing_Form(request.POST, label_suffix='')
		if form.is_valid():
			form_data = form.cleaned_data
			registration = form_data.get('registration')
			return redirect('reading_sessions:volunteer_testing', registration_id=registration.id)			
	else:
		form = Volunteer_Testing_Form(label_suffix='')

	context['form'] = form

	return render(request, "registration/volunteer_testing_times.html", context)


def staff_registration_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Staff Registration"
	context['load_staff_registration_scripts'] = True
	context['load_cropperjs_scripts'] = True
	context['display_login_logout']= False
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	context = volunteer_registration_additional_context(context)


	if request.method == "POST":
		form = Staff_Registration_Form(request.POST, request.FILES, label_suffix='')
		imageString = request.POST.get('imageString')
		inputX = request.POST.get('cropX')
		inputY = request.POST.get('cropY')
		inputW = request.POST.get('cropW')
		inputH = request.POST.get('cropH')

		if form.is_valid():		
			obj = form.save()
			Staff_Registration_Note.objects.create(registration = obj,
														name="Registration Submitted",
														)
			
			visitor_ip_address(request, obj, "Staff")

			Staff_Registration_Note.objects.create(registration = obj,
																name="Staff IP Info Created",
																)

			if obj.profile_image:					
				save_cropped_image_to_registration(obj, inputX, inputY, inputW, inputH )

	
			return redirect('registration:staff_confirmation', registration_id = obj.id)
		else:
			print("errors", form.errors)

	else:
		form = Staff_Registration_Form(label_suffix='')


	context['form'] = form


	return render(request, "registration/staff_registration.html", context)

#emails
def registration_email_check(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.   
		email = request.GET.get("email", None)
		type_reg = request.GET.get("type_reg", None)
		reg_lang = request.GET.get("reg_lang", None)
		# print(email, type_reg, reg_lang)

		# check database.
		if type_reg == "Volunteer":
			qs = Volunteer_Registration.objects.filter(email = email)
			qs2 = Parent_Registration.objects.filter(email = email)
			qs3 = Staff_Registration.objects.filter(email = email)
			# print("Query SET VOLUNTEERS", qs)
			total_count = qs.count() + qs2.count() + qs3.count()

			if total_count > 0:
				response['valid'] = False
			else:
				qs = CustomUser.objects.filter(email=email)
				if qs.count() > 0:
					response['valid'] = False
				else:
					response['valid'] = True

		elif type_reg == "Parent":
			qs = Volunteer_Registration.objects.filter(email = email)
			qs2 = Parent_Registration.objects.filter(email = email)
			qs3 = Staff_Registration.objects.filter(email = email)

			total_count = qs.count() + qs2.count() + qs3.count()

			if total_count > 0:
				response['valid'] = False
			else:
				qs = CustomUser.objects.filter(email=email)
				if qs.count() > 0:
					response['valid'] = False
				else:
					response['valid'] = True

		elif type_reg == "Volunteer Video":
			qs = Volunteer_Registration.objects.filter(email = email)
			# print("Query SET VOLUNTEERS Email", qs)

			if qs.count() == 1:
				response['valid'] = True
			else:
				response['valid'] = False

		elif type_reg == "Staff":
			qs = Volunteer_Registration.objects.filter(email = email)
			qs2 = Parent_Registration.objects.filter(email = email)
			qs3 = Staff_Registration.objects.filter(email = email)

			total_count = qs.count() + qs2.count() + qs3.count()
			if total_count > 0:
				response['valid'] = False
			else:
				qs = CustomUser.objects.filter(email=email)
				if qs.count() > 0:
					response['valid'] = False
				else:
					response['valid'] = True


		return HttpResponse(json.dumps(response), content_type="application/json")
	else:
		response['valid'] = False
		return HttpResponse(json.dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)

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



def email_link_additional_registration(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			lang = registration.registration_language.iso
			if lang == "en":
				context['card_title']= get_form_message("Title Student Submitted", "Student Registration")
				context['text_link']= get_form_message("For Email Link", "Student Registration")
				context['child_list']= get_form_message("Child List", "Student Registration")
				context['register_another']= get_form_message("Register Another", "Student Registration")
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"
				# print("\n\n\n\nlink", context['link'] )
				subject = 'eBookBuddy | Student Confirmation - You Are Registered!'
				html_message = render_to_string('registration/email_templates/student_confirmation_en.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'info@ebookbuddy.org'
				to = registration.email
			elif lang == "es":
				context['card_title']= get_form_message("Title Student Submitted", "Student Registration")
				context['text_link']= get_form_message("For Email Link", "Student Registration")
				context['child_list']= get_form_message("Child List", "Student Registration")
				context['register_another']= get_form_message("Register Another", "Student Registration")
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"
				# print("\n\n\n\nlink", context['link'] )
				subject = 'eBookBuddy | Estudiante Confirmación - ¡Está registrado!'
				html_message = render_to_string('registration/email_templates/student_confirmation_es.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'info@ebookbuddy.org'
				to = registration.email

			email_address_parameters("Tails", subject, plain_message, to, html_message)
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Registration Submitted",
																)


		except Exception as e:
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Registration Submitted",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_link_additional_registration",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))
		
def email_staff(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			subject = 'eBookBuddy Staff Registration'
			html_message = render_to_string('registration/email_templates/staff_submitted.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Staff", subject, plain_message, to, html_message)
			Staff_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Registration Submitted",
																)
			
		except Exception as e:
			Staff_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Registration Submitted",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_staff",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))
		

def email_link_volunteer_video(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			context['link'] = settings.BASE_URL + "/registration/volunteer/video/upload/"
			# print("\n\n\n\nlink", context['link'] )
			context['testing_link'] = settings.BASE_URL + "/registration/volunteer/testing/"
			subject = 'eBookBuddy Volunteer Registration'
			html_message = render_to_string('registration/email_templates/volunteer_submitted.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Volunteer", subject, plain_message, to, html_message)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Registration Submitted",
																)
			
		except Exception as e:
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Registration Submitted",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_link_volunteer_video",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))
		

def email_after_volunteer_video(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			context['link'] = settings.BASE_URL + "/registration/volunteer/video/upload/"
			print("\n\n\n\nlink", context['link'] )
			subject = 'eBookBuddy Volunteer Registration'
			html_message = render_to_string('registration/email_templates/video_submitted.html', context)
			plain_message = strip_tags(html_message)
			from_email = 'registration@ebookbuddy.org'
			to = registration.email
			email_address_parameters("Volunteer", subject, plain_message, to, html_message)
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Video Submit",
																)
		except Exception as e:
			Volunteer_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Video Submit",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_after_volunteer_video",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))
		
#functions for options
def convert_characteristics_choices():
	options = Student_Characteristic.objects.filter(active=True)
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options

def convert_additional_info_choices():
	options = Parent_Additional_Information.objects.filter(active=True)
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options

def convert_ethnicity_choices():
	options = Ethnicity.objects.filter(active=True)
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options

def convert_session_meeting_choices():
	options = Session_Meeting_Option.objects.filter(active=True)
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options

def get_form_message(name, form):
	message = Form_Message.objects.get(name=name, for_form__name=form,
										active=True)
	return message


def email_parent_registration_submitted(registration):
	if SEND_EMAILS:
		try:
			context = {}
			context['registration'] = registration
			lang = registration.registration_language.iso
			children = Student_Registration.objects.filter(parent=registration)
			context['children'] = children
			count = children.count()
			context['count']= count
			context['register_another']= get_form_message("Register Another", "Student Registration")
			if lang == "en":
				print("English")
				context['card_title']= "Parent Registration Submitted"
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"
				# print("\n\n\n\nlink", context['link'] )				
				subject = 'eBookBuddy | Parent Confirmation'
				html_message = render_to_string('registration/email_templates/additional_child_eng.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'info@ebookbuddy.org'
				to = registration.email
			elif lang == "es":
				print("Spanish")
				context['card_title']= "Parent Registration Submitted"
				context['link'] = settings.BASE_URL + "/registration/student/"+ lang + "/" + str(registration.id) + "/"
				# print("\n\n\n\nlink", context['link'] )
				subject = 'eBookBuddy | Confirmación de los padres'
				html_message = render_to_string('registration/email_templates/additional_child_span.html', context)
				plain_message = strip_tags(html_message)
				from_email = 'info@ebookbuddy.org'
				to = registration.email
			else:
				print("Neither")

			email_address_parameters("Tails", subject, plain_message, to, html_message)
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Sent After Registration Submitted",
																)
		except Exception as e:
			Parent_Registration_Note.objects.create(registration = registration,
																name="Email Failed After Registration Submitted",
																)
			Registration_Error.objects.create(file="views.py",
						function_name="email_parent_registration_submitted",
						location_in_function="try block for sending email",
						occurred_for_user="No User",
						error_text=str(e))


def parent_registration_view(request, form_language, **kwargs):
	context = {}
	context['page_title'] = "Program Registration"
	context['load_parent_registration_scripts'] = True
	context['display_login_logout']= False
	context['form_language']= form_language
	registration_language = Language.objects.get(iso=form_language)
	context['registration_language']= registration_language

	active_programs = Program_Semester.objects.filter(active_semester=True, accepting_students=True)
	# print("active_programs volunteer", active_programs)
	context['active_programs'] = active_programs

	if context['active_programs'].count() == 0:
		# print("NO ACTIVE PROGRAMS ACCEPTING Student")
		return redirect('registration:close_student')
	else:
		context['card_title']=get_form_message("Card Title", "Parent Registration")
		context['contact']= get_form_message("Parent Contact Information", "Parent Registration")
		context['other_help']=get_form_message("Other Help", "Parent Registration")
		context['languages'] = Language.objects.all()
		context['session_day_choices'] = Session_Day_Option.objects.filter(active=True)
		context['session_time_choices'] = Session_Time_Option.objects.filter(active=True)
		context['session_meeting_choices'] = Session_Meeting_Option.objects.filter(active=True)
		context['session_meeting_choices2'] = convert_session_meeting_choices()
		context['additional_info_choices'] =convert_additional_info_choices()
		context['consent_liability']=get_form_message("Parent Consent Liability", "Parent Registration")
		context['media_release']=get_form_message("Parent Media Release", "Parent Registration")
		
		context['button_text']=get_form_message("Enter Child Information", "Parent Registration")

		if form_language == "es":
			context['es_invalid_email'] = get_form_message('Spanish Invalid Email', 'Parent Registration')
			context['es_invalid_phone'] = get_form_message('Spanish Invalid Phone', 'Parent Registration')
			

		if request.method == "POST":
			form = Parent_Registration_Form(request.POST, label_suffix='')
			if form.is_valid():
				obj = form.save()
				Parent_Registration_Note.objects.create(registration = obj,
																name="Parent Registration Submitted",
																)
				visitor_ip_address(request, obj, "Parent")
				Parent_Registration_Note.objects.create(registration = obj,
																name="Parent IP Info Created",
																)
				kwargs = {}
				kwargs['form_language'] = form_language
				kwargs['parent_id'] = obj.id

				# email_parent_registration_submitted(obj)
			
				return redirect('registration:student_registration', form_language=form_language, parent_id = obj.id)
			else:
				# print("errors", form.errors)
				if "session_choices" in form.cleaned_data:
					context['cleaned_data_sessions']= form.cleaned_data['session_choices']
				if "additional_info" in form.cleaned_data:
					context['cleaned_data_additional_info']= form.cleaned_data['additional_info']
				
		else:
			form = Parent_Registration_Form(label_suffix='',
				initial={'registration_language': registration_language})

		context['form'] = form

		return render(request, "registration/parent_registration.html", context)



def student_registration_view(request, form_language, parent_id, **kwargs):
	context = {}
	context['page_title'] = "Student Registration"
	context['card_title']=get_form_message("Card Title", "Student Registration")
	context['load_child_registration_scripts'] = True
	context['load_cropperjs_scripts'] = True

	active_programs = Program_Semester.objects.filter(active_semester=True, accepting_students=True)
	# print("active_programs volunteer", active_programs)
	context['active_programs'] = active_programs

	if context['active_programs'].count() == 0:
		# print("NO ACTIVE PROGRAMS ACCEPTING Student")
		return redirect('registration:close_student')
	else:
		context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
		context['display_login_logout']= False
		context['form_language']= form_language
		registration_language = Language.objects.get(iso=form_language)
		context['registration_language']= registration_language
		parent_registration = Parent_Registration.objects.get(id=parent_id)
		context['registration_id'] = parent_registration.id
		context['registration_type'] = "Parent"
		context['load_registration_websocket'] = True
		context['button_text']=get_form_message("Submit Registration", "Student Registration")
		context['ethnicities'] = convert_ethnicity_choices()
		context['characteristics_choices'] =convert_characteristics_choices()
		context['qualities']=get_form_message("Child Qualities", "Student Registration")

		if request.method == "POST":
			form = Student_Registration_Form(request.POST, request.FILES, label_suffix='')
			imageString = request.POST.get('imageString')
			inputX = request.POST.get('cropX')
			inputY = request.POST.get('cropY')
			inputW = request.POST.get('cropW')
			inputH = request.POST.get('cropH')

			if form.is_valid():
				obj = form.save()
				Student_Registration_Note.objects.create(registration = obj,
																name="Student Registration Submitted",
																)
				Parent_Registration_Note.objects.create(registration = obj.parent,
																name="Child Added",
																)
				status_stu, created = Student_Registration_Status.objects.get_or_create(tech_screening="Not Attempted", registration=obj)

				Student_Registration_Note.objects.create(registration = obj,
														name="Student Checklist Created",
														)
				if obj.profile_image:					
					save_cropped_image_to_registration(obj, inputX, inputY, inputW, inputH )

				email_link_additional_registration(obj.parent)

				return redirect('registration:student_confirmation',
												 form_language=form_language,
												 parent_id=parent_id)
			else:
				if "ethnicity" in form.cleaned_data:
					context['cleaned_data_ethnicity']= form.cleaned_data['ethnicity']
				if "characteristics" in form.cleaned_data:
					context['cleaned_data_characteristics']= form.cleaned_data['characteristics']
		else:
			if context['active_programs'].count() == 1:
				form = Student_Registration_Form(label_suffix='',
					initial={
					'program_semester': context['active_programs'].first(),
					'registration_language': registration_language,
					'parent': parent_registration,
					})
			else:
				form = Student_Registration_Form(label_suffix='',
					initial={'registration_language': registration_language,
							'parent': parent_registration,})

		context['form'] = form
		

		return render(request, "registration/student_registration.html", context)

def confirm_student_registration_view(request, form_language, parent_id, **kwargs):
	context = {}
	context['page_title'] = "Student Registration"
	context['display_login_logout']= False
	context['form_language']= form_language
	registration_language = Language.objects.get(iso=form_language)
	context['registration_language']= registration_language
	parent_registration = Parent_Registration.objects.get(id=parent_id)
	context['parent_registration'] = parent_registration
	context['card_title']= get_form_message("Title Student Submitted", "Student Registration")
	context['check_email']= get_form_message("Check Email", "Student Registration")
	context['child_list']= get_form_message("Child List", "Student Registration")
	context['register_another']= get_form_message("Register Another", "Student Registration")
	
	return render(request, "registration/student_confirmation.html", context)

def pre_registration_student_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Student Registration"
	context['load_parent_registration_scripts'] = True
	context['display_login_logout']= False
	context['languages'] = Language.objects.filter(display_form_language = True)

	active_programs = Program_Semester.objects.filter(active_semester=True, accepting_students=True)
	# print("active_programs volunteer", active_programs)
	context['active_programs'] = active_programs

	if context['active_programs'].count() == 0:
		# print("NO ACTIVE PROGRAMS ACCEPTING Student")
		return redirect('registration:close_student')
	else:
		context['card_title']= get_form_message("Title", "Student Pre-Registration")
		context['header1']= get_form_message("Header1", "Student Pre-Registration")

		if request.method == "POST":
			form = Pre_Registration_Form(request.POST, label_suffix='')
			if form.is_valid():
				form_data = form.cleaned_data
				language = form_data.get('language')
				# return redirect('registration:student_confirmation')
				# print("language", language)
				return redirect('registration:parent_registration', form_language=language.iso)			
		else:
			form = Pre_Registration_Form(label_suffix='')

		context['form'] = form

		return render(request, "registration/pre_registration_student.html", context)

def visitor_ip_address(request, registration, role):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	# print("settings.GEOIP_PATH", settings.GEOIP_PATH)
	file_name_db = "GeoLite2-City.mmdb"
	path_db = os.path.join(settings.GEOIP_PATH, file_name_db)
	# print("path_db", path_db)

	reader = geoip2.database.Reader(path_db)

	if x_forwarded_for:
		try:
			ip = x_forwarded_for.split(',')[0]
			socket.inet_aton(ip)
			ip_valid = True
			response = reader.city(str(ip))
			country = response.country.iso_code
			city = response.city.name
			latitude = response.location.latitude
			longitude = response.location.longitude
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)

			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)


		except socket.error:
			ip_valid = False
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									) 
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									)
			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									)

		except Exception as e:
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 

			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 

	else:
		
		try:
			ip = request.META.get('REMOTE_ADDR')
			socket.inet_aton(ip)
			ip_valid = True
			response = reader.city(str(ip))
			country = response.country.iso_code
			city = response.city.name
			latitude = response.location.latitude
			longitude = response.location.longitude
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)

			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									country=country,
									city=city,
									latitude=latitude,
									longitude=longitude)

		except socket.error:
			ip_valid = False 
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									) 
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									) 
			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=ip,
									ip_valid=ip_valid,
									) 

		except Exception as e:
			if role == "Volunteer":
				info_instance = Volunteer_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 
			elif role == "Parent":
				info_instance = Parent_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 
			elif role == "Staff":
				info_instance = Staff_Registration_IP_Info.objects.get_or_create(
									registration=registration,
									ip=str(e),
									ip_valid=False,
									) 


	reader.close()


 

def get_program_status(name):
	program = Program.objects.get(name=name)
	updating_now = program.program_status.updating
	return updating_now


def save_cropped_image_to_registration(registration, inputX, inputY, inputW, inputH):

	registration_id = registration.id
	profile_image_name = registration.profile_image.name

	# print("profile_image_name",profile_image_name)
	# full_url = os.path.join(settings.PROJECT_ROOT, registration.profile_image.url)

	try:

		if DEV:
			full_url = os.path.join(settings.MEDIA_ROOT, profile_image_name)
			img = cv2.imread(full_url)
		else:
			full_url = registration.profile_image.url
			resp = urllib.request.urlopen(full_url)
			image = np.asarray(bytearray(resp.read()), dtype="uint8")
			img = cv2.imdecode(image, cv2.IMREAD_COLOR)
	    	# image = cv2.imdecode(image, cv2.IMREAD_COLOR)

		# print("FULL URL", full_url)

		cropX = int(float(str(inputX)))
		cropY = int(float(str(inputY)))
		cropW = int(float(str(inputW)))
		cropH = int(float(str(inputH)))

		if cropX < 0:
			cropX = 0

		if cropY < 0:
			cropY = 0

		crop_img = img[cropY:cropY + cropH, cropX:cropX + cropW]

		cv2.imwrite(full_url, crop_img)
		try:
			if DEV:
				file_name = str(registration_id) + "_profile_img.png"
				registration.cropped_profile_image.save(file_name, files.File(open(full_url, "rb")))
				registration.profile_image.delete()
			else:
				ret, buf = cv2.imencode('.png', crop_img) # cropped_image: cv2 / np array
				content = ContentFile(buf.tobytes())
				file_name = str(registration_id) + "_profile_img.png"
				registration.cropped_profile_image.save(file_name, content)
				registration.profile_image.delete()

		except Exception as e:
			print("Exception Inner", e, full_url)
			Registration_Error.objects.create(file="views.py",
						function_name="save_cropped_image_to_registration",
						location_in_function="inner try block for cropping image",
						occurred_for_user="No User",
						error_text=str(e) + " - " + full_url)
		
		


	except Exception as e:
		print("Exception Outer", e, full_url)
		Registration_Error.objects.create(file="views.py",
						function_name="save_cropped_image_to_registration",
						location_in_function="Outer try block for cropping image",
						occurred_for_user="No User",
						error_text=str(e) + " - " + full_url)


def get_reference_question(form):
	question = Question.objects.get(for_form__name=form, field_name="references")
	return question


def get_ii_sub_child_protection(form):
	list_sub = []
	num = 1
	child_1 = Form_Message.objects.get(name="1-II. - Child Protection Policy", for_form__name=form,
										active=True)
	list_sub.append((num, child_1))
	num = num + 1

	child_2 = Form_Message.objects.get(name="2-II. - Child Protection Policy", for_form__name=form,
										active=True)
	list_sub.append((num, child_2))
	num = num + 1

	child_3 = Form_Message.objects.get(name="3-II. - Child Protection Policy", for_form__name=form,
										active=True)
	list_sub.append((num, child_3))
	num = num + 1

	child_4 = Form_Message.objects.get(name="4-II. - Child Protection Policy", for_form__name=form,
										active=True)
	list_sub.append((num, child_4))
	num = num + 1

	child_5 = Form_Message.objects.get(name="5-II. - Child Protection Policy", for_form__name=form,
										active=True)
	list_sub.append((num, child_5))

	return list_sub

def volunteer_registration_additional_context(context):
	context['session_day_choices'] = Session_Day_Option.objects.filter(active=True)
	context['session_time_choices'] = Session_Time_Option.objects.filter(active=True)
	context['session_meeting_choices'] = Session_Meeting_Option.objects.filter(active=True)
	context['session_meeting_choices2'] = convert_session_meeting_choices()
	context['ref_msg'] = get_form_message("References", "Volunteer Registration")
	context['ref_q'] = get_reference_question("Volunteer Registration")
	context['child_protection_title'] = get_form_message("Title - Child Protection Policy", "Volunteer Registration")
	context['child_protection_p1'] = get_form_message("P1 - Child Protection Policy", "Volunteer Registration")
	context['child_protection_i'] = get_form_message("I. - Child Protection Policy", "Volunteer Registration")
	context['child_protection_ii'] = get_form_message("II. - Child Protection Policy", "Volunteer Registration")
	context['child_protection_ii_sub'] = get_ii_sub_child_protection("Volunteer Registration")
	context['too_young'] = Form_Message.objects.get(name="Too Young", for_form__name="Volunteer Registration",
										active=True)

	active_programs = Program_Semester.objects.filter(active_semester=True, accepting_volunteers=True)
	print("active_programs volunteer", active_programs)
	context['active_programs'] = active_programs

	return context


def volunteer_registration_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Registration"
	context['load_vol_registration_scripts'] = True
	context['load_cropperjs_scripts'] = True
	context['display_login_logout']= False
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	context = volunteer_registration_additional_context(context)

	if context['active_programs'].count() == 0:
		print("NO ACTIVE PROGRAMS ACCEPTING VOLUNTEERS")
		return redirect('registration:close_volunteer')


	if request.method == "POST":
		form = Volunteer_Registration_Form(request.POST, request.FILES, label_suffix='')
		imageString = request.POST.get('imageString')
		inputX = request.POST.get('cropX')
		inputY = request.POST.get('cropY')
		inputW = request.POST.get('cropW')
		inputH = request.POST.get('cropH')

		if form.is_valid():		
			obj = form.save()
			Volunteer_Registration_Note.objects.create(registration = obj,
														name="Registration Submitted",
														)
			
			if obj.convicted == "Yes" or obj.charges_pending == "Yes" or obj.refused_participation == "Yes":
				obj.flagged = True
				obj.save()
				Volunteer_Registration_Note.objects.create(registration = obj,
																name="Registration Flagged",
																)

			visitor_ip_address(request, obj, "Volunteer")

			Volunteer_Registration_Note.objects.create(registration = obj,
																name="Volunteer IP Info Created",
																)

			status_vol, created = Volunteer_Registration_Status.objects.get_or_create(tech_screening="Not Attempted",
																					 registration=obj)

			if obj.profile_image:					
				save_cropped_image_to_registration(obj, inputX, inputY, inputW, inputH )

			Volunteer_Registration_Note.objects.create(registration = obj,
																name="Volunteer Checklist Created",
																)

			return redirect('registration:volunteer_confirmation', registration_id = obj.id)
		else:
			# print("errors", form.errors)
			if "session_choices" in form.cleaned_data:
				context['cleaned_data_sessions']= form.cleaned_data['session_choices']
				# print("*****CLEANED DATA", form.cleaned_data['session_choices'])
	else:
		if context['active_programs'].count() == 1:
			form = Volunteer_Registration_Form(label_suffix='',
				initial={
				'program_semester': context['active_programs'].first()
				})
		else:
			form = Volunteer_Registration_Form(label_suffix='')


	context['form'] = form


	return render(request, "registration/volunteer_registration.html", context)

def video_volunteer_registration_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Upload Registration Video"
	context['load_vol_registration_scripts'] = False
	context['load_cropperjs_scripts'] = False
	context['display_login_logout']= False
	context['file_upload_scripts'] = True
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	error_url = settings.BASE_URL + '/registration/volunteer/video/error/'
	context['error_url'] = error_url

	if request.method == "POST":
		form = Volunteer_Video_Form(request.POST, request.FILES, label_suffix='')

		if form.is_valid():		
			obj = form.save()
			if obj.registration:
				status_vol, created = Volunteer_Registration_Status.objects.get_or_create(registration=obj.registration)
				status_vol.video_uploaded = True
				status_vol.save()
				Volunteer_Registration_Note.objects.create(registration = status_vol.registration,
																name="Video Uploaded",
																)

			submitted_url = settings.BASE_URL + '/registration/volunteer/video/submitted/' + str(obj.registration.id)

			return JsonResponse({'data':'Data uploaded', 'next_url': submitted_url})

			# return redirect('registration:volunteer_video_confirmation', registration_id = obj.registration.id)
		else:
			context['form'] = form
			return render(request, "registration/video_volunteer_registration.html", context)
			
			# return JsonResponse({'data':'Something Went Wrong', 'next_url': error_url, 'registration_id': obj.registration.id})

	else:
		form = Volunteer_Video_Form(label_suffix='')
		# print("form", form)


	context['form'] = form


	return render(request, "registration/video_volunteer_registration.html", context)


def confirm_staff_registration_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Staff Registration"
	context['display_login_logout']= False
	context['load_registration_websocket'] = True


	registration = Staff_Registration.objects.get(id=registration_id)
	email_staff(registration)
	
	context['registration_id'] = registration.id
	context['registration_type'] = "Staff"

	return render(request, "registration/staff_confirmation.html", context)

def confirm_volunteer_registration_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Registration"
	context['display_login_logout']= False
	context['load_registration_websocket'] = True


	registration = Volunteer_Registration.objects.get(id=registration_id)
	email_link_volunteer_video(registration)
	
	context['registration_id'] = registration.id
	context['registration_type'] = "Volunteer"

	context['message_1'] = Form_Message.objects.get(name="Submission Received 1")
	context['message_2'] = Form_Message.objects.get(name="Submission Received 2")
	context['message_3'] = Form_Message.objects.get(name="Submission Received 3")

	return render(request, "registration/volunteer_confirmation.html", context)

def confirm_video_volunteer_registration_view(request, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Video Submitted"
	context['display_login_logout']= False

	registration = Volunteer_Registration.objects.get(id=registration_id)
	email_after_volunteer_video(registration)
	
	context['registration_id'] = registration.id
	context['registration_type'] = "Volunteer"

	# context['message_1'] = Form_Message.objects.get(name="Submission Received 1")
	# context['message_2'] = Form_Message.objects.get(name="Submission Received 2")
	# context['message_3'] = Form_Message.objects.get(name="Submission Received 3")

	return render(request, "registration/volunteer_video_confirmation.html", context)


def closed_volunteer_registration_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Registration"
	context['display_login_logout']= False

	return render(request, "registration/closed_volunteer_registration.html", context)

def closed_student_registration_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Student Registration"
	context['display_login_logout']= False

	return render(request, "registration/closed_student_registration.html", context)




# unused

def confirm_parent_registration_view(request,form_language, registration_id, **kwargs):
	context = {}
	context['page_title'] = "Program Registration"
	context['display_login_logout']= False
	context['form_language']= form_language

	registration = Parent_Registration.objects.get(id=registration_id)
	context['card_title'] = Form_Message.objects.get(name="Parent Submitted Card Title")


	return render(request, "registration/parent_confirmation.html", context)


def crop_image(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST:
		try:
			imageString = request.POST.get('profile_image')
			url = save_temp_profile_image(imageString, 2)
			img = cv2.imread(url)
			cropX = int(float(str(request.POST.get('cropX'))))
			cropY = int(float(str(request.POST.get('cropY'))))
			cropW = int(float(str(request.POST.get('cropW'))))
			cropH = int(float(str(request.POST.get('cropH'))))

			if cropX < 0:
				cropX = 0

			if cropY < 0:
				cropY = 0

			crop_img = img[cropY:cropY + cropH, cropX:cropX + cropW]

			cv2.imwrite(url, crop_img)

			user.profile_image.delete()

			file_name = str(2) + "_profile_img.png"

			user.profile_image.save(file_name, files.File(open(url, "rb")))

			os.remove(url)

		except Exception as e:
			print("Image crop ERROR", e)	

def save_temp_profile_image(imageString, registration_id):
	INCORRECT_PADDING_EXCEPTION = "Incorrect Padding"
	try:
		if not os.path.exists(setting.TEMP):
			os.mkdir(settings.TEMP)

		if not os.path.exists(settings.TEMP +"/" + str(registration_id)):
			os.mkdir(settings.TEMP +"/" + str(registration_id))

		url = os.path.join(settings.TEMP +"/" + str(registration_id), TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)

		with storage.open('','wb+') as destination:
			destination.write(image)
			destination.close()

		return url

	except Exception as e:
		print("save_temp_profile_image EXCEPTION", e)
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4- len(imageString)% 4) % 4)
			Registration_Error.objects.create(file="views.py",
						function_name="save_temp_profile_image",
						location_in_function="try block for saving profile image",
						occurred_for_user="No User",
						error_text=str(e) + " - " + registration_id)
			return save_temp_profile_image(imageString, registration_id)