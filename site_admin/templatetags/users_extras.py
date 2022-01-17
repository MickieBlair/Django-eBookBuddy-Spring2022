from django import template
from django.template.defaultfilters import stringfilter
from users.models import CustomUser
from users.models import Role
from matches.models import Student_Match_Profile, Reader_Match_Profile
from site_admin.models import User_Team_Info

staff_role = Role.objects.get(name="Staff")
student_role = Role.objects.get(name="Student")
volunteer_role = Role.objects.get(name="Volunteer")
parent_role = Role.objects.get(name="Parent/Guardian")
reader_role = Role.objects.get(name="Reader")
coordinator_role = Role.objects.get(name="Coordinator")
team_leader_role = Role.objects.get(name="Team Leader")

register = template.Library()

@register.filter(name='user_registration')
def user_registration(member):
	# print("\n\n\n\n\n",member)
	if staff_role in member.roles.all():
		# print("Staff")
		return "Staff"
	elif student_role in member.roles.all():
		# print("Student")
		return "Student"
	elif volunteer_role in member.roles.all():
		# print("Volunteer")
		return "Volunteer"
	elif parent_role in member.roles.all():
		# print("Parent")
		return "Parent"

@register.filter(name='user_status')
def user_status(member):
	# print("\n\n\n\n\n",member)
	if reader_role in member.roles.all():
		return "Reader"
	elif student_role in member.roles.all():
		return "Student"
	else:
		return "None"

# @register.filter(name='match_status')
# def match_status(member):
# 	print("\n\n\n\n\n",member)
# 	if reader_role in member.roles.all():
# 		reader_profile = Reader_Match_Profile.objects.get(user=member)
# 		return reader_profile
# 	elif student_role in member.roles.all():
# 		student_profile = Student_Match_Profile.objects.get(user=member)
# 		return student_profile


@register.filter(name='is_volunteer')
def is_volunteer(member):
	if volunteer_role in member.roles.all():
		return True
	else: 
		return False

@register.filter(name='team_info')
def team_info(member):
	if User_Team_Info.objects.filter(user=member).exists():
		return True
	else:
		return False

	
@register.filter(name='team_status')
def team_status(member):
	# print("\n\n\n\n\n",member)
	if coordinator_role in member.roles.all():
		return "Coordinator"
	elif team_leader_role in member.roles.all():
		return "Team Leader"
	else:
		return "Member"
	
