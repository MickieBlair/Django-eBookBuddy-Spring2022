from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from localflavor.us.models import USStateField
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from cropperjs.models import CropperImageField
from django.utils import timezone
from datetime import datetime, timedelta, date
from PIL import Image
import os
from users.models import Program, CustomUser
from buddy_program_data.models import Program_Form, Program_Semester
from buddy_program_data.models import Gender, Ethnicity
from buddy_program_data.models import Current_Education_Level, Current_Education_Class
from buddy_program_data.models import Team_Meeting_Time, Session_Meeting_Option
from buddy_program_data.models import Opportunity_Source, Social_Media_Source
from buddy_program_data.models import Device_Type, Volunteer_Opportunity
from buddy_program_data.models import Volunteer_Reason
from buddy_program_data.models import Web_Source, Message_App
from buddy_program_data.models import Grade, School, Language
from buddy_program_data.models import Parent_Additional_Information, Student_Characteristic
from buddy_program_data.models import Reading_Description
from registration.formatChecker import ContentTypeRestrictedFileField

RETURNING_VOLUNTEER_CHOICES = [("New","New Volunteer"),("Returning","Returning Volunteer")]
YES_NO_CHOICES_ENG = [("Yes","Yes"),("No","No")]
YES_NO_CHOICES_ENG_SPAN = [("Yes","Yes / Si"),("No","No / No"),]
YES_NO_CHOICES_SPAN = [("Yes","Si"),("No","No"),]
YES_NO_ONLY = [("Yes","Yes"),("No","No")]
STATUS_TECH_SCREENING = [("Not Attempted","Not Attempted"),
						("Failed","Failed"),
						("Passed","Passed")]

def staff_temp_images(instance, filename):
	name = slugify(instance.first_name + "_" + instance.last_name)
	new_file_name = "%s-%s.%s" % (name, "temp_img", "png")
	file_path = 'temp_profile_images/staff/{new_file_name}'.format(
				new_file_name=new_file_name)
	return file_path


def staff_profile_images(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s-%s.%s" % (instance.id, "profile_img", "png")
    file_path = 'user_profile_images/staff/{filename}'.format(
				filename=filename)
    return file_path

def volunteer_temp_images(instance, filename):
	name = slugify(instance.first_name + "_" + instance.last_name)
	new_file_name = "%s-%s.%s" % (name, "temp_img", "png")
	file_path = 'temp_profile_images/volunteer/{new_file_name}'.format(
				new_file_name=new_file_name)
	return file_path


def volunteer_profile_images(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s-%s.%s" % (instance.id, "profile_img", "png")
    file_path = 'user_profile_images/volunteer/{filename}'.format(
				filename=filename)
    return file_path

class Volunteer_Registration(models.Model):
	program = models.ForeignKey(Program, related_name="volunteer_registration_program",
								 on_delete=models.CASCADE, null=True, blank=True)
	program_semester = models.ForeignKey(Program_Semester, related_name="volunteer_registration_program_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	volunteer_type = models.CharField(max_length=30, choices=RETURNING_VOLUNTEER_CHOICES,
										null=True, blank=True, verbose_name="Type")
	dob = models.DateField(null=True, blank=True)
	parent_name = models.CharField(max_length=255, null=True, blank=True)
	parent_email = models.EmailField(verbose_name="Parent Email", max_length=80,
									 null=True, blank=True)
	first_name = models.CharField(max_length=150, null=False, blank=False)
	last_name = models.CharField(max_length=150, null=False, blank=False)
	country = CountryField(null=True, blank=True)
	address = models.CharField(max_length=150, null=True, blank=True)
	city = models.CharField(max_length=150, null=True, blank=True)
	state = USStateField(null=True, blank=True)	
	zip_code = models.CharField(max_length=10, null=True, blank=True)
	email = models.EmailField(verbose_name="email", max_length=80, null=True, blank=True)
	phone = PhoneNumberField(null=True, blank=True, max_length=16)
	gender = models.ForeignKey(Gender, related_name="vol_gender",
								 on_delete=models.CASCADE, null=True, blank=True)
	ethnicity = models.ForeignKey(Ethnicity, related_name="vol_ethnicity",
								 on_delete=models.CASCADE, null=True, blank=True)
	in_school = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	current_education_level = models.ForeignKey(Current_Education_Level, related_name="current_level",
								 on_delete=models.CASCADE, null=True, blank=True)
	current_education_class = models.ForeignKey(Current_Education_Class, related_name="current_class",
								 on_delete=models.CASCADE, null=True, blank=True)
	current_school = models.CharField(max_length=150, null=True, blank=True)
	highest_education_level = models.ForeignKey(Current_Education_Level, related_name="highest_education",
								 on_delete=models.CASCADE, null=True, blank=True)
	previously_paired = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	student_name = models.CharField(max_length=255, null=True, blank=True)
	teamleader_name = models.CharField(max_length=255, null=True, blank=True)
	returning_referred = models.CharField(max_length=255, null=True, blank=True)
	meeting_times = models.ManyToManyField(Team_Meeting_Time, related_name="team_meeting_times",
					blank=True,)
	session_choices = models.ManyToManyField(Session_Meeting_Option, related_name="choices_sessions",
					blank=True,)

	fluent_spanish = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	opportunity_source = models.ForeignKey(Opportunity_Source, related_name="hear_about_us",
								 on_delete=models.CASCADE, null=True, blank=True)
	social_media_source = models.ForeignKey(Social_Media_Source, related_name="social",
								 on_delete=models.CASCADE, null=True, blank=True)
	person_referral = models.CharField(max_length=255, null=True, blank=True)

	computer = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)

	device_type = models.ForeignKey(Device_Type, related_name="device",
								 on_delete=models.CASCADE, null=True, blank=True)
	children_experience = models.TextField(max_length=5000, null=True, blank=True)
	reason = models.TextField(max_length=2000, null=True, blank=True)
	other_reasons = models.ManyToManyField(Volunteer_Reason, related_name="reasons_others",
					blank=True,)
	reason_not_listed = models.TextField(max_length=1000, null=True, blank=True)
	volunteer_other_areas = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)

	additional_interests = models.ManyToManyField(Volunteer_Opportunity, related_name="interest_additional",
					blank=True,)
	ref_name_1 = models.CharField( verbose_name="Name", max_length=255, null=True, blank=True)
	ref_email_1 = models.EmailField(verbose_name="Email", max_length=80,
									 null=True, blank=True)
	ref_phone_1 = PhoneNumberField(verbose_name="Phone Number",null=True, blank=True, max_length=16)
	ref_relationship_1 = models.CharField( verbose_name="Relationship to you", max_length=255, null=True, blank=True)

	ref_name_2 = models.CharField( verbose_name="Name", max_length=255, null=True, blank=True)
	ref_email_2 = models.EmailField(verbose_name="Email", max_length=80,
									 null=True, blank=True)
	ref_phone_2 = PhoneNumberField(verbose_name="Phone Number", null=True, blank=True, max_length=16)
	ref_relationship_2 = models.CharField( verbose_name="Relationship to you", max_length=255, null=True, blank=True)
	agree_requirements_initials = models.CharField(max_length=255, null=True, blank=True)
	statements_true_initials = models.CharField(max_length=255, null=True, blank=True)
	remove_volunteers_initials = models.CharField(max_length=255, null=True, blank=True)
	cropped_profile_image = models.ImageField(upload_to=volunteer_profile_images, null=True, blank=True)
	profile_image = models.ImageField(upload_to=volunteer_temp_images, null=True, blank=True)
	web_source = models.CharField(max_length=255, null=True, blank=True)
	sponsor_child = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	convicted = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	convicted_text = models.TextField(max_length=2000, null=True, blank=True)
	charges_pending = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	charges_pending_text = models.TextField(max_length=2000, null=True, blank=True)
	refused_participation = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	refused_participation_text = models.TextField(max_length=2000, null=True, blank=True)
	full_name_signature = models.CharField(max_length=255, null=True, blank=True)
	county = models.CharField(max_length=150, null=True, blank=True)	
	date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="date submitted")
	user = models.OneToOneField(CustomUser, related_name="vol_user",
								 on_delete=models.DO_NOTHING, null=True, blank=True)
	flagged = models.BooleanField(default=False)


	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Registration'
		verbose_name_plural = 'Volunteer Registrations'

	def full_name(self):
		return self.first_name + " " + self.last_name

	def location(self):
		location = ''
		if self.city and self.state and self.country:
			location = self.city + ", " + self.state + " - " + str(self.country)
		else:
			location = self.country.name

		return location

	def age(self):
		today = timezone.localtime(timezone.now()).date() 
		if self.dob:
			try:
				birthday = self.dob.replace(year = today.year) 

			except ValueError:
				birthday = self.dob.replace(year = today.year,
						month = self.dob.month + 1, day = 1) 

			if birthday > today:
				return today.year - self.dob.year - 1
			else:
				return today.year - self.dob.year 

	def phone_format(self):
		phone = str(self.phone)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone

	def ref1_phone_format(self):
		phone = str(self.ref_phone_1)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone

	def ref2_phone_format(self):
		phone = str(self.ref_phone_2)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone

	def status(self):
		approved_to_match = self.volunteer_registration_status.approved_to_match
		denied = self.volunteer_registration_status.denied
		if approved_to_match and not denied:
			status = "Approved"
		elif denied:
			status = "Denied"
		else:
			status = "Pending"
		return status

	def __str__(self):
		return "Volunteer: " + self.first_name + " " + self.last_name

def pre_save_volunteer_registration_receiver(sender, instance, *args, **kwargs):
	if instance.program_semester:
		instance.program = instance.program_semester.program
	if instance.first_name:
		instance.first_name= instance.first_name.title()
	if instance.last_name:
		instance.last_name= instance.last_name.title() 

pre_save.connect(pre_save_volunteer_registration_receiver, sender=Volunteer_Registration)

@receiver(post_delete, sender=Volunteer_Registration)
def registration_delete(sender, instance, **kwargs):
	if instance.profile_image:
		instance.profile_image.delete(False)
	if instance.cropped_profile_image:
		instance.cropped_profile_image.delete(False)  

# @receiver(post_save, sender=Volunteer_Registration)
# def create_registration(sender, instance, created, **kwargs):
# 	content_type = ContentType.objects.get_for_model(instance)
# 	try:
# 			reg= Registration.objects.get(content_type=content_type,
# 										object_id=instance.id)
# 	except Registration.DoesNotExist:
# 		reg = Registration(content_type=content_type, object_id=instance.id)

# 	reg.created = instance.date_submitted
# 	reg.reg_type = "Volunteer"
# 	reg.save()






class Volunteer_Registration_IP_Info(models.Model):
	registration = models.ForeignKey(Volunteer_Registration, related_name="vol_reg_ip",
								 on_delete=models.CASCADE, null=True, blank=True)
	ip = models.CharField(max_length=255, null=True, blank=True)
	ip_valid = models.BooleanField(default=False)
	country = models.CharField(max_length=255, null=True, blank=True)
	city = models.CharField(max_length=255, null=True, blank=True)
	latitude =  models.CharField(max_length=255, null=True, blank=True)	
	longitude =  models.CharField(max_length=255, null=True, blank=True)
	ws_connected = models.BooleanField(default=False)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Registration IP Info'
		verbose_name_plural = 'Volunteer Registration IP Info'

	def string_for_return(self):
		if self.registration.last_name != None:
			string_for_return = str(self.registration.id) + "-" + self.registration.last_name
		else:
			string_for_return = str(self.registration.id)

		return string_for_return

	def __str__(self):
		return self.string_for_return()

class Parent_Registration(models.Model):
	registration_language = models.ForeignKey(Language, related_name="registration_language",
								 on_delete=models.CASCADE, null=True, blank=True)
	parent_first_name = models.CharField(max_length=150, null=False, blank=False)
	parent_last_name = models.CharField(max_length=150, null=False, blank=False)
	country = CountryField(null=True, blank=True)
	address = models.CharField(max_length=150, null=True, blank=True)
	city = models.CharField(max_length=150, null=True, blank=True)
	state = USStateField(null=True, blank=True)	
	zip_code = models.CharField(max_length=10, null=True, blank=True)
	email = models.EmailField(verbose_name="email", max_length=80, null=True, blank=True)
	phone = PhoneNumberField(null=True, blank=True, max_length=16)
	county = models.CharField(max_length=150, null=True, blank=True)
	# preferred_contact_language = models.ForeignKey(Language, related_name="contact_language",
								 # on_delete=models.CASCADE, null=True, blank=True)
	# device_in_touch = models.ForeignKey(Device_Type, related_name="in_touch_device",
								 # on_delete=models.CASCADE, null=True, blank=True)
	# other_device_in_touch = models.CharField(max_length=255, null=True, blank=True)

	internet = models.CharField(max_length=30, choices=YES_NO_ONLY, null=True, blank=True)
	computer = models.CharField(max_length=30, choices=YES_NO_ONLY, null=True, blank=True)


	session_choices = models.ManyToManyField(Session_Meeting_Option,
											related_name="student_choices_sessions",
											blank=True,)
	flexible_schedule = models.CharField(max_length=30, choices=YES_NO_ONLY, null=True, blank=True)

	# parent_available = models.CharField(max_length=30, choices=YES_NO_ONLY,
	# 									null=True, blank=True)
	parent_can_help = models.CharField(max_length=30, choices=YES_NO_ONLY,
										null=True, blank=True)
	help_name = models.CharField(max_length=255, null=True, blank=True)
	help_phone = PhoneNumberField(null=True, blank=True, max_length=16)
	help_relationship= models.CharField(max_length=255, null=True, blank=True)

	
	
	additional_info = models.ManyToManyField(Parent_Additional_Information,
											related_name="additional_checks",
											blank=True,)

	
	consent_liability_initials = models.CharField(max_length=255, null=True, blank=True)
	media_release_initials = models.CharField(max_length=255, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")	
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	user = models.OneToOneField(CustomUser, related_name="parent_user",
								 on_delete=models.DO_NOTHING, null=True, blank=True)
	flagged = models.BooleanField(default=False)



	class Meta:
		ordering = ['id']
		verbose_name = 'Parent Registration'
		verbose_name_plural = 'Parent Registrations'

	def full_name(self):
		return self.parent_first_name + " " + self.parent_last_name

	def phone_format(self):
		phone = str(self.phone)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone

	def help_phone_format(self):
		phone = str(self.help_phone)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone


	def __str__(self):
		return "Parent: " + self.parent_first_name + " " + self.parent_last_name

def pre_save_parent_registration_receiver(sender, instance, *args, **kwargs):
	if instance.parent_first_name:
		instance.parent_first_name= instance.parent_first_name.title()
	if instance.parent_last_name:
		instance.parent_last_name= instance.parent_last_name.title() 

pre_save.connect(pre_save_parent_registration_receiver, sender=Parent_Registration)

# @receiver(post_save, sender=Parent_Registration)
# def create_registration(sender, instance, created, **kwargs):
# 	content_type = ContentType.objects.get_for_model(instance)
# 	try:
# 			reg= Registration.objects.get(content_type=content_type,
# 										object_id=instance.id)
# 	except Registration.DoesNotExist:
# 		reg = Registration(content_type=content_type, object_id=instance.id)

# 	reg.created = instance.date_created
# 	reg.reg_type = "Parent"
# 	reg.save()

class Student_Registration(models.Model):
	program = models.ForeignKey(Program, related_name="child_program",
								 on_delete=models.CASCADE, null=True, blank=True)
	program_semester = models.ForeignKey(Program_Semester, related_name="child_registration_program_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	registration_language = models.ForeignKey(Language, related_name="registration_lang",
								 on_delete=models.CASCADE, null=True, blank=True)
	parent = models.ForeignKey(Parent_Registration, related_name="parent_info",
								 on_delete=models.CASCADE, null=True, blank=True)

	child_first_name = models.CharField(max_length=150, null=False, blank=False)
	child_last_name = models.CharField(max_length=150, null=False, blank=False)
	dob = models.DateField(null=True, blank=True)
	gender = models.ForeignKey(Gender, related_name="child_gender",
								 on_delete=models.CASCADE, null=True, blank=True)
	ethnicity = models.ForeignKey(Ethnicity, related_name="child_ethnicity",
								 on_delete=models.CASCADE, null=True, blank=True)
	current_grade = models.ForeignKey(Grade, related_name="child_grade",
								 on_delete=models.CASCADE, null=True, blank=True)
	school = models.ForeignKey(School, related_name="child_grade",
								 on_delete=models.CASCADE, null=True, blank=True)
	other_school = models.CharField(max_length=255, null=True, blank=True)
	
	prior_participation = models.CharField(max_length=30, choices=YES_NO_ONLY,
										null=True, blank=True)
	primary_language = models.ForeignKey(Language, related_name="first_language",
								 on_delete=models.CASCADE, null=True, blank=True)
	other_primary_language = models.CharField(max_length=255, null=True, blank=True)
	secondary_language = models.ForeignKey(Language, related_name="second_language",
								 on_delete=models.CASCADE, null=True, blank=True)
	other_secondary_language = models.CharField(max_length=255, null=True, blank=True)
	reading_level = models.ForeignKey(Reading_Description, related_name="child_level",
								 on_delete=models.CASCADE, null=True, blank=True)

	relationship_to_child = models.CharField(max_length=255, null=True, blank=True)
	child_comment = models.TextField(max_length=3000, null=True, blank=True)
	session_device = models.ForeignKey(Device_Type, related_name="device_session",
								 on_delete=models.CASCADE, null=True, blank=True)
	other_session_device = models.CharField(max_length=255, null=True, blank=True)
	cropped_profile_image = models.ImageField(upload_to='user_profile_images/student', null=True, blank=True)
	profile_image = models.ImageField(upload_to='temp_profile_images/student', null=True, blank=True)
	characteristics = models.ManyToManyField(Student_Characteristic,
											related_name="student_characteristics",
											blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")	
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	user = models.OneToOneField(CustomUser, related_name="student_user",
								 on_delete=models.DO_NOTHING, null=True, blank=True)
	flagged = models.BooleanField(default=False)

	class Meta:
		ordering = ['id']
		verbose_name = 'Student Registration'
		verbose_name_plural = 'Student Registrations'

	def age(self):
		today = timezone.localtime(timezone.now()).date() 
		if self.dob:
			try:
				birthday = self.dob.replace(year = today.year) 

			except ValueError:
				birthday = self.dob.replace(year = today.year,
						month = self.dob.month + 1, day = 1) 

			if birthday > today:
				return today.year - self.dob.year - 1
			else:
				return today.year - self.dob.year 

	def full_name(self):
		return self.child_first_name + " " + self.child_last_name

	def get_school(self):
		school = ""
		if self.school:
			if self.school.name == "Other (Please Specify)":
				school = self.other_school
			else:
				school = self.school.name

		return school

	def first_lang(self):
		first_lang = ""
		if self.primary_language:
			if self.primary_language.eng_name == "Other (Please Specify)":
				first_lang = self.other_primary_language
			else:
				first_lang = self.primary_language.eng_name

		return first_lang

	def second_lang(self):
		second_lang = ""
		if self.secondary_language:
			if self.secondary_language.eng_name == "Other (Please Specify)":
				second_lang = self.other_secondary_language
			else:
				second_lang = self.secondary_language.eng_name

		return second_lang

	def get_session_device(self):
		device = ""
		if self.session_device:
			if self.session_device.name == "Other (Please Specify)":
				device = self.other_session_device
			else:
				device = self.session_device.name

		return device

	def status(self):
		approved_to_match = self.student_registration_status.approved_to_match
		waitlist = self.student_registration_status.waitlist
		if approved_to_match and not waitlist:
			status = "Approved"
		elif waitlist:
			status = "Waitlist"
		else:
			status = "Pending"
		return status	


	def __str__(self):
		return "Student: " + self.child_first_name + " " + self.child_last_name

def pre_save_student_registration_receiver(sender, instance, *args, **kwargs):
	if instance.program_semester:
		instance.program = instance.program_semester.program
	if instance.child_first_name:
		instance.child_first_name= instance.child_first_name.title()
	if instance.child_last_name:
		instance.child_last_name= instance.child_last_name.title() 

pre_save.connect(pre_save_student_registration_receiver, sender=Student_Registration)

@receiver(post_delete, sender=Student_Registration)
def registration_delete(sender, instance, **kwargs):
	if instance.profile_image:
		instance.profile_image.delete(False)
	if instance.cropped_profile_image:
		instance.cropped_profile_image.delete(False)  

# @receiver(post_save, sender=Student_Registration)
# def create_registration(sender, instance, created, **kwargs):
# 	content_type = ContentType.objects.get_for_model(instance)
# 	try:
# 			reg= Registration.objects.get(content_type=content_type,
# 										object_id=instance.id)
# 	except Registration.DoesNotExist:
# 		reg = Registration(content_type=content_type, object_id=instance.id)

# 	reg.created = instance.date_created
# 	reg.reg_type = "Student"
# 	reg.save()




class Registration_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Registration Error'
		verbose_name_plural = 'Registration Errors'

	def __str__(self):
		return self.file


class Parent_Registration_IP_Info(models.Model):
	registration = models.ForeignKey(Parent_Registration, related_name="parent_reg_ip",
								 on_delete=models.CASCADE, null=True, blank=True)
	ip = models.CharField(max_length=255, null=True, blank=True)
	ip_valid = models.BooleanField(default=False)
	country = models.CharField(max_length=255, null=True, blank=True)
	city = models.CharField(max_length=255, null=True, blank=True)
	latitude =  models.CharField(max_length=255, null=True, blank=True)	
	longitude =  models.CharField(max_length=255, null=True, blank=True)
	ws_connected = models.BooleanField(default=False)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Parent Registration IP Info'
		verbose_name_plural = 'Parent Registration IP Info'

	def string_for_return(self):
		if self.registration.parent_last_name != None:
			string_for_return = str(self.registration.id) + "-" + self.registration.parent_last_name
		else:
			string_for_return = str(self.registration.id)

		return string_for_return

	def __str__(self):
		return self.string_for_return()


def volunteer_videos(instance, filename):
	name = slugify(instance.email)
	ext = filename.split('.')[-1]
	filename = "%s.%s" % (name, ext)
	file_path = 'videos/volunteer/{filename}'.format(filename=filename)
	return file_path

class Volunteer_Video(models.Model):
	email = email = models.EmailField(verbose_name="email", max_length=80, null=False, blank=False)
	videofile= models.FileField(upload_to=volunteer_videos, null=False, verbose_name="")
	times_clicked = models.PositiveIntegerField(default=0,)	
	registration = models.OneToOneField(Volunteer_Registration, related_name="volunteer_video",
								 on_delete=models.CASCADE, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Video'
		verbose_name_plural = 'Volunteer Videos'

	def __str__(self):
		return self.email

@receiver(post_delete, sender=Volunteer_Video)
def video_delete(sender, instance, **kwargs):
	if instance.videofile:
		instance.videofile.delete(False)


class Volunteer_Registration_Status(models.Model):
	registration = models.OneToOneField(Volunteer_Registration, related_name="volunteer_registration_status",
								 on_delete=models.CASCADE, null=False, blank=False)
	tech_screening= models.CharField(max_length=30, choices=STATUS_TECH_SCREENING,
										null=True, blank=True, verbose_name="Tech Screening")
	online_training_completed = models.BooleanField(default=False)
	video_uploaded = models.BooleanField(default=False)
	video_reviewed = models.BooleanField(default=False)
	live_screening_passed = models.BooleanField(default=False)
	orientation = models.BooleanField(default=False)
	reference_check = models.BooleanField(default=False)
	approved_to_match = models.BooleanField(default=False)
	approved_by = models.ForeignKey(CustomUser, related_name="vols_approved",
								 on_delete=models.CASCADE, null=True, blank=True)
	date_approved= models.DateTimeField(verbose_name="date approved", null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created", )

	last_updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='vols_last_updated', null=True, blank=True,)
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	denied = models.BooleanField(default=False)
	denied_by = models.ForeignKey(CustomUser, related_name="vols_denied",
								 on_delete=models.CASCADE, null=True, blank=True)
	date_denied = models.DateTimeField(verbose_name="date denied", null=True, blank=True,)
	denied_reason = models.TextField(max_length=2000, null=True, blank=True)

	
	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Registration Status'
		verbose_name_plural = 'Volunteer Registration Statuses'

	def __str__(self):
		return str(self.registration)

class Volunteer_Registration_Note(models.Model):
	registration = models.ForeignKey(Volunteer_Registration, related_name="notes",
								 on_delete=models.CASCADE, null=False, blank=False)
	name = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(max_length=2000, null=True, blank=True)
	created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='vol_registration_notes', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Registration Note'
		verbose_name_plural = 'Volunteer Registration Notes'

	def __str__(self):
		return str(self.name)

class Student_Registration_Status(models.Model):
	registration = models.OneToOneField(Student_Registration, related_name="student_registration_status",
								 on_delete=models.CASCADE, null=False, blank=False)	
	responsive = models.BooleanField(default=False)
	confirm = models.BooleanField(default=False)
	tech_screening= models.CharField(max_length=30, choices=STATUS_TECH_SCREENING,
										null=True, blank=True, verbose_name="Tech Screening")
	approved_to_match = models.BooleanField(default=False)
	approved_by = models.ForeignKey(CustomUser, related_name="stu_approved",
								 on_delete=models.CASCADE, null=True, blank=True)
	date_approved= models.DateTimeField(verbose_name="date approved", null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	last_updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='stu_last_updated', null=True, blank=True,)
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	waitlist = models.BooleanField(default=False)
	waitlist_by = models.ForeignKey(CustomUser, related_name="stus_waitlisted",
								 on_delete=models.CASCADE, null=True, blank=True)
	date_waitlist = models.DateTimeField(verbose_name="date waitlisted", null=True, blank=True,)
	waitlist_reason = models.TextField(max_length=2000, null=True, blank=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Student Registration Status'
		verbose_name_plural = 'Student Registration Statuses'

	def __str__(self):
		return str(self.registration)

class Student_Registration_Note(models.Model):
	registration = models.ForeignKey(Student_Registration, related_name="notes",
								 on_delete=models.CASCADE, null=False, blank=False)
	name = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(max_length=2000, null=True, blank=True)
	created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='stu_registration_notes', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Student Registration Note'
		verbose_name_plural = 'Student Registration Notes'

	def __str__(self):
		return str(self.name)

class Parent_Registration_Note(models.Model):
	registration = models.ForeignKey(Parent_Registration, related_name="notes",
								 on_delete=models.CASCADE, null=False, blank=False)
	name = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(max_length=2000, null=True, blank=True)
	created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='parent_registration_notes', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Parent Registration Note'
		verbose_name_plural = 'Parent Registration Notes'

	def __str__(self):
		return str(self.name)



class Staff_Registration(models.Model):
	dob = models.DateField(null=True, blank=True)
	first_name = models.CharField(max_length=150, null=False, blank=False)
	last_name = models.CharField(max_length=150, null=False, blank=False)
	email = models.EmailField(verbose_name="email", max_length=80, null=True, blank=True)
	phone = PhoneNumberField(null=True, blank=True, max_length=16)
	country = CountryField(null=True, blank=True)
	city = models.CharField(max_length=150, null=True, blank=True)
	state = USStateField(null=True, blank=True)
	gender = models.ForeignKey(Gender, related_name="staff_gender",
								 on_delete=models.CASCADE, null=True, blank=True)
	in_school = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	current_education_level = models.ForeignKey(Current_Education_Level, related_name="staff_current_level",
								 on_delete=models.CASCADE, null=True, blank=True)
	current_education_class = models.ForeignKey(Current_Education_Class, related_name="staff_current_class",
								 on_delete=models.CASCADE, null=True, blank=True)
	current_school = models.CharField(max_length=150, null=True, blank=True)
	highest_education_level = models.ForeignKey(Current_Education_Level, related_name="staff_highest_education",
								 on_delete=models.CASCADE, null=True, blank=True)
	fluent_spanish = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)
	computer = models.CharField(max_length=30, choices=YES_NO_CHOICES_ENG, null=True, blank=True)

	device_type = models.ForeignKey(Device_Type, related_name="staff_device",
								 on_delete=models.CASCADE, null=True, blank=True)	
	cropped_profile_image = models.ImageField(upload_to=staff_profile_images, null=True, blank=True)
	profile_image = models.ImageField(upload_to=staff_temp_images, null=True, blank=True)
	date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="date submitted")
	user = models.OneToOneField(CustomUser, related_name="staff_user",
								 on_delete=models.DO_NOTHING, null=True, blank=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Staff Registration'
		verbose_name_plural = 'Staff Registrations'

	def full_name(self):
		return self.first_name + " " + self.last_name

	def location(self):
		location = ''
		if self.city and self.state and self.country:
			location = self.city + ", " + self.state + " - " + str(self.country)
		else:
			location = self.country.name
		return location

	def age(self):
		today = timezone.localtime(timezone.now()).date() 
		if self.dob:
			try:
				birthday = self.dob.replace(year = today.year) 

			except ValueError:
				birthday = self.dob.replace(year = today.year,
						month = self.dob.month + 1, day = 1) 

			if birthday > today:
				return today.year - self.dob.year - 1
			else:
				return today.year - self.dob.year 

	def phone_format(self):
		phone = str(self.phone)
		if phone.startswith("+1"):
			return phone[2:5] + "-" + phone[5:8] + "-" + phone[8:12]
		else:
			return self.phone




	def __str__(self):
		return "Staff: " + self.first_name + " " + self.last_name

@receiver(pre_save, sender=Staff_Registration)
def staff_capitialize_first_last(sender, instance, **kwargs):
	if instance.first_name:
		instance.first_name= instance.first_name.title()
	if instance.last_name:
		instance.last_name= instance.last_name.title() 

@receiver(post_delete, sender=Staff_Registration)
def registration_delete(sender, instance, **kwargs):
	if instance.profile_image:
		instance.profile_image.delete(False)
	if instance.cropped_profile_image:
		instance.cropped_profile_image.delete(False)  


# @receiver(post_save, sender=Staff_Registration)
# def create_registration(sender, instance, created, **kwargs):
# 	content_type = ContentType.objects.get_for_model(instance)
# 	try:
# 			reg= Registration.objects.get(content_type=content_type,
# 										object_id=instance.id)
# 	except Registration.DoesNotExist:
# 		reg = Registration(content_type=content_type, object_id=instance.id)

# 	reg.created = instance.date_submitted
# 	reg.reg_type = "Staff"
# 	reg.save()

class Staff_Registration_IP_Info(models.Model):
	registration = models.ForeignKey(Staff_Registration, related_name="staff_reg_ip",
								 on_delete=models.CASCADE, null=True, blank=True)
	ip = models.CharField(max_length=255, null=True, blank=True)
	ip_valid = models.BooleanField(default=False)
	country = models.CharField(max_length=255, null=True, blank=True)
	city = models.CharField(max_length=255, null=True, blank=True)
	latitude =  models.CharField(max_length=255, null=True, blank=True)	
	longitude =  models.CharField(max_length=255, null=True, blank=True)
	ws_connected = models.BooleanField(default=False)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Staff Registration IP Info'
		verbose_name_plural = 'Staff Registration IP Info'

	def string_for_return(self):
		if self.registration.last_name != None:
			string_for_return = str(self.registration.id) + "-" + self.registration.last_name
		else:
			string_for_return = str(self.registration.id)

		return string_for_return

	def __str__(self):
		return self.string_for_return()


class Staff_Registration_Note(models.Model):
	registration = models.ForeignKey(Staff_Registration, related_name="notes",
								 on_delete=models.CASCADE, null=False, blank=False)
	name = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(max_length=2000, null=True, blank=True)
	created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='staff_registration_notes', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Staff Registration Note'
		verbose_name_plural = 'Staff Registration Notes'

	def __str__(self):
		return str(self.name)

# class Registration(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     created = models.DateTimeField()
#     reg_type = models.CharField(max_length=255, null=True, blank=True)
#     class Meta:
#         ordering = ['-created']
#     def __str__(self):
#         return "{0} - {1}".format(self.content_object.full_name,
#                                   self.reg_type)