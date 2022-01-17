from django import template
from django.template.defaultfilters import stringfilter
from users.models import CustomUser
from registration.models import Volunteer_Registration
from registration.models import Volunteer_Registration_Note
from registration.models import Volunteer_Registration_Status
from registration.models import Student_Registration
from registration.models import Parent_Registration
from registration.models import Parent_Registration_Note
from registration.models import Student_Registration_Note
from registration.models import Student_Registration_Status

register = template.Library()

@register.filter(name='user_exists')
def user_exists(registration):
	exists = False
	reg_type = registration._meta.model.__name__
	print("\n\n\n\nregistration", registration, reg_type)
	return exists

@register.filter(name='testing_sent')
def testing_sent(registration):
	total_sent = 0
	registration_status = Volunteer_Registration_Status.objects.get(registration=registration)
	qs = Volunteer_Registration_Note.objects.filter(registration=registration, name="Email Sent For Tech Testing")
	total_sent = qs.count()
	return total_sent

@register.filter(name='user_info_sent')
def user_info_sent(registration):
	total_sent = 0
	registration_status = Volunteer_Registration_Status.objects.get(registration=registration)
	qs = Volunteer_Registration_Note.objects.filter(registration=registration, name="User Info Email Sent")
	total_sent = qs.count()
	return total_sent


@register.filter(name='total_children')
def total_children(registration):
	total_children = 0
	qs = Student_Registration.objects.filter(parent=registration)
	total_children = qs.count()
	return total_children



@register.filter(name='parent_email_register_children')
def parent_email_register_children(registration):
	total_sent = 0
	qs = Parent_Registration_Note.objects.filter(registration=registration, name="Email Sent After Registration Submitted")
	total_sent = qs.count()
	return total_sent

@register.filter(name='whatsapp_email_reminder')
def whatsapp_email_reminder(registration):
	total_sent = 0
	qs = Parent_Registration_Note.objects.filter(registration=registration, name="WhatsApp Reminder Email Sent")
	total_sent = qs.count()
	return total_sent



@register.filter(name='video_reminder')
def video_reminder(registration):
	total_sent = 0
	registration_status = Volunteer_Registration_Status.objects.get(registration=registration)
	qs = Volunteer_Registration_Note.objects.filter(registration=registration, name="Video Reminder Email Sent")
	total_sent = qs.count()
	return total_sent