from django import template
from django.template.defaultfilters import stringfilter
from users.models import CustomUser
from users.models import Role
from matches.models import Student_Match_Profile, Reader_Match_Profile
from reading_sessions.models import Match_Session_Status, User_Session_Status

staff_role = Role.objects.get(name="Staff")
student_role = Role.objects.get(name="Student")
volunteer_role = Role.objects.get(name="Volunteer")
parent_role = Role.objects.get(name="Parent/Guardian")
reader_role = Role.objects.get(name="Reader")

register = template.Library()

@register.filter(name='user_icon_class')

def user_icon_class(member):
	# print('user_icon_class', member)
	user_status = User_Session_Status.objects.get(user=member)
	css_class = ""
	if user_status.online_ws or user_status.online_jitsi:
		css_class = "user_online"
	# elif user_status.online_ws or user_status.online_jitsi:
	# 	css_class = "user_limbo"
	else:
		css_class = "user_offline"

	return css_class

@register.filter(name='ws_online')
def ws_online(member):
	user_status = User_Session_Status.objects.get(user=member)
	css_class = ""
	if user_status.online_ws:
		css_class = "user_online"
	else:
		css_class = "user_offline"
	
	return css_class

@register.filter(name='jitsi_online')
def jitsi_online(member):
	user_status = User_Session_Status.objects.get(user=member)
	css_class = ""
	if user_status.online_jitsi:
		css_class = "user_online"
	else:
		css_class = "user_offline"
	
	return css_class

@register.filter(name='user_role')
def user_role(member):
	if student_role in member.roles.all():
		return "Student"

	elif reader_role in member.roles.all():
		return "Reader"

	elif staff_role in member.roles.all():
		return "Staff"
	
	elif volunteer_role in member.roles.all():
		return "Volunteer"











	

	







	

	
