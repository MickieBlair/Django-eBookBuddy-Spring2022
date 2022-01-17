from django import template
from django.template.defaultfilters import stringfilter
from users.models import CustomUser
from users.models import Role
from matches.models import Student_Match_Profile, Reader_Match_Profile

staff_role = Role.objects.get(name="Staff")
student_role = Role.objects.get(name="Student")
volunteer_role = Role.objects.get(name="Volunteer")
parent_role = Role.objects.get(name="Parent/Guardian")
reader_role = Role.objects.get(name="Reader")

register = template.Library()

@register.filter(name='user_role')
def user_role(member):
	# print("\n\n\n\n\n",member)
	if reader_role in member.roles.all():
		# print("Staff")
		return "Reader"
	elif student_role in member.roles.all():
		# print("Student")
		return "Student"


@register.filter(name='show_rooms_button')
def show_rooms_button(member):
	if staff_role in member.roles.all():
		return True



	

	
