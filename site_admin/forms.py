from django import forms
from registration.models import Volunteer_Registration_Note
from registration.models import Volunteer_Registration_Status
from registration.models import Volunteer_Registration
from registration.models import Staff_Registration
from registration.models import Staff_Registration_Note
from registration.models import Student_Registration_Status
from registration.models import Student_Registration_Note
from registration.models import Student_Registration, Parent_Registration
from site_admin.models import User_Team_Info
from buddy_program_data.models import Team, Team_Meeting_Time
from buddy_program_data.models import Mega_Team
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from users.models import Role, Program, User_View

def team_leader_choices():
	team_leader_role = Role.objects.get(name="Team Leader")
	choices = team_leader_role.user_roles.all()
	return choices

class Team_Form(forms.ModelForm):
	name = forms.CharField(
		max_length=150,
		required=False,
		label="Name: ",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('name')"})
	)

	mega=forms.ModelChoiceField(
		label="Mega Team: ",
		required=False,
		queryset=Mega_Team.objects.all(),
		widget=forms.RadioSelect(
									choices=Mega_Team.objects.all(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('mega')"})
	)

	leader=forms.ModelChoiceField(
		label="Team Leader: ",
		required=False,
		empty_label="---------------------",
		queryset=team_leader_choices(),
		widget=forms.Select(
									choices=team_leader_choices(),
									attrs={'class': "form_control_modified_flex",
									'onclick': "clear_input_errors('leader')"})
	)

	meeting_day_time=forms.ModelChoiceField(
		label="Meeting Time: ",
		required=False,
		queryset=Team_Meeting_Time.objects.all(),
		widget=forms.RadioSelect(
									choices=Team_Meeting_Time.objects.all(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('meeting_day_time')"})
	)
	class Meta:
		model = Team
		fields = (
				'name',
				'mega',
				'leader',
				'meeting_day_time',
				'volunteers',
				'room',
				'meeting_day',
				'meeting_time',
				

				)

def coordinator_choices():
	coordinator_role = Role.objects.get(name="Coordinator")
	choices = coordinator_role.user_roles.all()
	return choices

class Mega_Team_Form(forms.ModelForm):
	name = forms.CharField(
		max_length=150,
		required=False,
		label="Name: ",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('name')"})
	)
	coordinator=forms.ModelChoiceField(
		label="Coordinator: ",
		required=False,
		empty_label="---------------------",
		queryset=coordinator_choices(),
		widget=forms.Select(
									choices=coordinator_choices(),
									attrs={'class': "form_control_modified_flex",
									'onclick': "clear_input_errors('coordinator')"})
	)
	class Meta:
		model = Mega_Team
		fields = (
				'name',
				'coordinator',
				)

def team_role_choices():
	choices = [("Coordinator","Coordinator"),("Team Leader","Team Leader"),("Member","Member")]
	return choices

def team_choices():
	choices = Team.objects.all()
	return choices

class User_Team_Info_Create_Form(forms.ModelForm):

	team_role=forms.CharField(
		label="Team Role: ",
		required=False,
		widget=forms.RadioSelect(choices=team_role_choices(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('team_role')"})
	)

	team=forms.ModelChoiceField(
		label="Team: ",
		required=False,
		queryset=team_choices(),
		widget=forms.RadioSelect(
									choices=team_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('team')"})
	)

	class Meta:
		model = User_Team_Info
		fields = (
				'user',
				'team_role',
				'mega',
				'team',
				)

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance', None)

		super(User_Team_Info_Create_Form, self).__init__(*args, **kwargs)

		if instance:
			print("INSTANCE", instance)
			if instance.user:
				self.initial['user'] = instance.user
				if instance.team_role:
					self.initial['team_role'] = instance.team_role
					print("instance.team_role", instance.team_role)

				else:
					user_roles = instance.user.roles.all()
					team_leader_role = Role.objects.get(name='Team Leader')
					coordinator_role = Role.objects.get(name='Coordinator')
					if team_leader_role in user_roles:
						initial_role = team_leader_role.name
					elif coordinator_role in user_roles:
						initial_role = coordinator_role.name
					else:
						initial_role = "Member"

					self.initial['team_role'] = initial_role
					print("self.initial['team_role']", self.initial['team_role'])

			if instance.team:
				print("instance.team", instance.team)

				self.initial['team'] = instance.team.id

			if instance.mega:
				self.initial['mega'] = instance.mega


	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()

		user = cleaned_data.get("user")
		team_role = cleaned_data.get("team_role")
		mega = cleaned_data.get("mega")
		team = cleaned_data.get("team")

		if user:
			print("user", user)
		else:
			self.add_error('user', ValidationError(_('This field is required'), code='required'))							

		if team_role:
			print("team_role", team_role)
		else:
			self.add_error('team_role', ValidationError(_('This field is required'), code='required'))							
		
		if team:
			print("team", team)
		else:
			self.add_error('team', ValidationError(_('This field is required'), code='required'))


def create_volunteer_roles_choices():
	qs = Role.objects.all().exclude(name='Student').exclude(name="Staff").exclude(name="Parent/Guardian").exclude(name="Observer")
	return qs

def create_staff_roles_choices():
	qs = Role.objects.all().exclude(name='Student').exclude(name="Volunteer").exclude(name="Parent/Guardian").exclude(name="Observer")
	return qs


class User_Update_Form(forms.ModelForm):
	username = forms.CharField(
		max_length=255,
		required=False,		
		label="Username:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
									})
	)

	first_name = forms.CharField(
		max_length=255,
		required=False,
		label="First Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)
	last_name = forms.CharField(
		max_length=255,
		required=False,
		label="Last Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)

	email = forms.CharField(
		max_length=80,
		required=False,
		label="Email:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								})
	)

	user_view=forms.ModelChoiceField(
		label="User View:",
		required=False,
		queryset = User_View.objects.all(),
		widget=forms.RadioSelect(choices=User_View.objects.all(),
		attrs={'class': "registration_radio",})
	)

	roles=forms.ModelMultipleChoiceField(
		label="Roles:",
		required=False,
		queryset=Role.objects.all(),
		widget=forms.CheckboxSelectMultiple(
									choices=Role.objects.all(),
									attrs={'class': "registration_radio"})
	)

	access_site_admin = forms.CharField(
		label="Access Site Admin:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	password_change_required = forms.CharField(
		label="Password Change Required:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	
	

	class Meta:
		model = CustomUser
		fields = ('username','first_name', 'last_name', 'email','user_view',
				 'roles','access_site_admin','password_change_required', )

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance', None)

		super(User_Update_Form, self).__init__(*args, **kwargs)

		if instance:
			self.initial['username'] = instance.username
			self.initial['first_name'] = instance.first_name
			self.initial['last_name'] = instance.last_name
			self.initial['email'] = instance.email
			self.initial['user_view'] = instance.user_view
			self.initial['roles'] = instance.roles.all()
			self.initial['access_site_admin'] = instance.access_site_admin
			self.initial['password_change_required'] = instance.password_change_required


	def clean_username(self):
		username = self.cleaned_data['username']
		if username == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
			except CustomUser.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)

	def clean_email(self):
		email = self.cleaned_data['email']
		if email != "":		
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
			except CustomUser.DoesNotExist:
				return email
			raise forms.ValidationError('Email is already in use.')
		else:
			email = None
			return email

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		print('first_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			self.cleaned_data['first_name'] = data
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		print('last_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data

	def clean_roles(self):
		data = self.cleaned_data['roles']
		print('roles', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])		
		return data

class Create_Any_User_Form(UserCreationForm):
	roles=forms.ModelMultipleChoiceField(
		label="Roles:",
		required=False,
		queryset=Role.objects.all(),
		widget=forms.CheckboxSelectMultiple(
									choices=Role.objects.all(),
									attrs={'class': "registration_radio"})
	)
	username = forms.CharField(
		max_length=255,
		required=False,		
		label="Username:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
									})
	)

	first_name = forms.CharField(
		max_length=255,
		required=False,
		label="First Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)
	last_name = forms.CharField(
		max_length=255,
		required=False,
		label="Last Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)

	password1 = forms.CharField(
		max_length=255,
		required=False,
		label="Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)
	password2 = forms.CharField(
		max_length=255,
		required=False,
		label="Confirm Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)

	programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

	email = forms.CharField(
		max_length=80,
		required=False,
		label="Email:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								})
	)

	user_view=forms.ModelChoiceField(
		label="User View:",
		required=False,
		queryset = User_View.objects.all(),
		widget=forms.RadioSelect(choices=User_View.objects.all(),
		attrs={'class': "registration_radio",})
	)

	access_site_admin = forms.CharField(
		label="Access Site Admin:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	password_change_required = forms.CharField(
		label="Password Change Required:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	# def __init__(self, *args, **kwargs):
	# 	super(Create_Staff_User_Form, self).__init__(*args, **kwargs)

	class Meta:
		model = CustomUser
		fields = (
					'username',
					'first_name',
					'last_name',
					'email',
					'roles',
					'user_view',
					'access_site_admin',
					'programs',
					'is_approved',
					'is_active',
					'avatar_img',
					'profile_img',					
					'password1',
					'password2',
					'password_change_required',

					# 'password',
					# 'last_login',
					# 'groups',
					# 'user_permissions',										
					# 'is_admin',					
					# 'is_staff',
					# 'is_superuser',					
					
										
					)

	def clean_username(self):
		username = self.cleaned_data['username']
		if username == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
			except CustomUser.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)

	def clean_email(self):
		email = self.cleaned_data['email']
		if email != "":		
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
			except CustomUser.DoesNotExist:
				return email
			raise forms.ValidationError('Email is already in use.')
		else:
			email = None
			return email

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		print('first_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			self.cleaned_data['first_name'] = data
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		print('last_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data

	def clean_programs(self):
		data = self.cleaned_data['programs']
		print('programs', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_roles(self):
		data = self.cleaned_data['roles']
		print('roles', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])		
		return data

class Create_Staff_User_Form(UserCreationForm):
	roles=forms.ModelMultipleChoiceField(
		label="Roles:",
		required=False,
		queryset=create_staff_roles_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=create_staff_roles_choices(),
									attrs={'class': "registration_radio"})
	)
	username = forms.CharField(
		max_length=255,
		required=False,		
		label="Suggested Username:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
									})
	)

	first_name = forms.CharField(
		max_length=255,
		required=False,
		label="First Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)
	last_name = forms.CharField(
		max_length=255,
		required=False,
		label="Last Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)

	password1 = forms.CharField(
		max_length=255,
		required=False,
		label="Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)
	password2 = forms.CharField(
		max_length=255,
		required=False,
		label="Confirm Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)

	programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

	email = forms.CharField(
		max_length=80,
		required=False,
		label="Email:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								})
	)

	user_view=forms.ModelChoiceField(
		label="User View:",
		required=False,
		queryset = User_View.objects.all().exclude(name="Student View").exclude(name="Reader Only View"),
		widget=forms.RadioSelect(choices=User_View.objects.all().exclude(name="Student View").exclude(name="Reader Only View"),
		attrs={'class': "registration_radio",})
	)

	access_site_admin = forms.CharField(
		label="Access Site Admin:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	password_change_required = forms.CharField(
		label="Password Change Required:",
		required=False,
		initial=True,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	def __init__(self, *args, **kwargs):
		super(Create_Staff_User_Form, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs['readonly'] = True 
		self.fields['last_name'].widget.attrs['readonly'] = True 
		self.fields['email'].widget.attrs['readonly'] = True    

	class Meta:
		model = CustomUser
		fields = (
					'username',
					'first_name',
					'last_name',
					'email',
					'roles',
					'user_view',
					'access_site_admin',
					'programs',
					'is_approved',
					'is_active',
					'avatar_img',
					'profile_img',
					
					'password1',
					'password2',
					'password_change_required',

					# 'password',
					# 'last_login',
					# 'groups',
					# 'user_permissions',										
					# 'is_admin',					
					# 'is_staff',
					# 'is_superuser',					
					
										
					)

	def clean_username(self):
		username = self.cleaned_data['username']
		if username == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
			except CustomUser.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		print('first_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			self.cleaned_data['first_name'] = data
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		print('last_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_programs(self):
		data = self.cleaned_data['programs']
		print('programs', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_roles(self):
		data = self.cleaned_data['roles']
		print('roles', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data

class Create_Volunteer_User_Form(UserCreationForm):
	roles=forms.ModelMultipleChoiceField(
		label="Roles:",
		required=False,
		queryset=create_volunteer_roles_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=create_volunteer_roles_choices(),
									attrs={'class': "registration_radio"})
	)
	username = forms.CharField(
		max_length=255,
		required=False,		
		label="Suggested Username:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
									})
	)

	first_name = forms.CharField(
		max_length=255,
		required=False,
		label="First Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)
	last_name = forms.CharField(
		max_length=255,
		required=False,
		label="Last Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)

	password1 = forms.CharField(
		max_length=255,
		required=False,
		label="Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)
	password2 = forms.CharField(
		max_length=255,
		required=False,
		label="Confirm Password:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)

	programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

	email = forms.CharField(
		max_length=80,
		required=False,
		label="Email:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								})
	)

	user_view=forms.ModelChoiceField(
		label="User View:",
		required=False,
		queryset = User_View.objects.all().exclude(name="Student View"),
		widget=forms.RadioSelect(choices=User_View.objects.all().exclude(name="Student View"),
		attrs={'class': "registration_radio",})
	)

	access_site_admin = forms.CharField(
		label="Access Site Admin:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	password_change_required = forms.CharField(
		label="Password Change Required:",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	def __init__(self, *args, **kwargs):
		super(Create_Volunteer_User_Form, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs['readonly'] = True 
		self.fields['last_name'].widget.attrs['readonly'] = True 
		self.fields['email'].widget.attrs['readonly'] = True    

	class Meta:
		model = CustomUser
		fields = (
					'username',
					'first_name',
					'last_name',
					'email',
					'roles',
					'user_view',
					'access_site_admin',
					'programs',
					'is_approved',
					'is_active',
					'avatar_img',
					'profile_img',
					
					'password1',
					'password2',

					# 'password',
					# 'last_login',
					# 'groups',
					# 'user_permissions',										
					# 'is_admin',					
					# 'is_staff',
					# 'is_superuser',					
					'password_change_required',
										
					)

		# fields = ('username', )

	def clean_username(self):
		username = self.cleaned_data['username']
		if username == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
			except CustomUser.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		print('first_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			self.cleaned_data['first_name'] = data
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		print('last_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_programs(self):
		data = self.cleaned_data['programs']
		print('programs', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_roles(self):
		data = self.cleaned_data['roles']
		print('roles', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data


class Student_Registration_Note_Form(forms.ModelForm):
	content = forms.CharField(
		max_length=2000,
		required=True,
		label="Note/Comment (max_length = 2000 characters)",
		widget=forms.Textarea(attrs={'class': 'form-control',
								'rows': 5})
	)
	class Meta:
		model = Student_Registration_Note
		fields = ('registration', 'name', 'content', 'created_user')

class Volunteer_Registration_Note_Form(forms.ModelForm):
	content = forms.CharField(
		max_length=2000,
		required=True,
		label="Note/Comment (max_length = 2000 characters)",
		widget=forms.Textarea(attrs={'class': 'form-control',
								'rows': 5})
	)
	class Meta:
		model = Volunteer_Registration_Note
		fields = ('registration', 'name', 'content', 'created_user')

class Staff_Registration_Note_Form(forms.ModelForm):
	content = forms.CharField(
		max_length=2000,
		required=True,
		label="Note/Comment (max_length = 2000 characters)",
		widget=forms.Textarea(attrs={'class': 'form-control',
								'rows': 5})
	)
	class Meta:
		model = Staff_Registration_Note
		fields = ('registration', 'name', 'content', 'created_user')


class Create_Student_User_Form(UserCreationForm):
	roles=forms.ModelMultipleChoiceField(
		label="Roles",
		required=False,
		queryset=Role.objects.filter(name="Student"),
		widget=forms.CheckboxSelectMultiple(
									choices=Role.objects.filter(name="Student"),
									attrs={'class': "registration_radio"})
	)
	username = forms.CharField(
		max_length=255,
		required=False,		
		label="Suggested Username",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
									})
	)

	first_name = forms.CharField(
		max_length=255,
		required=False,
		label="First Name",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)
	last_name = forms.CharField(
		max_length=255,
		required=False,
		label="Last Name",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)

	password1 = forms.CharField(
		max_length=255,
		required=False,
		label="Password",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',})
	)
	password2 = forms.CharField(
		max_length=255,
		required=False,
		label="Confirm Password",
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex', })
	)

	programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

	def __init__(self, *args, **kwargs):
		super(Create_Student_User_Form, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs['readonly'] = True 
		self.fields['last_name'].widget.attrs['readonly'] = True   

	class Meta:
		model = CustomUser
		fields = (
					'username',
					'first_name',
					'last_name',
					'roles',
					'programs',
					'is_approved',
					'is_active',
					'avatar_img',
					'profile_img',
					'user_view',
					'password1',
					'password2',

					# 'password',
					# 'last_login',
					# 'groups',
					# 'user_permissions',				
					# 'email',					
					# 'is_admin',					
					# 'is_staff',
					# 'is_superuser',					
					# 'password_change_required',
					# 'access_site_admin',
					
					)
		# fields = ('username', )

	def clean_username(self):
		username = self.cleaned_data['username']
		if username == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			try:
				existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
			except CustomUser.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		print('first_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		else:
			self.cleaned_data['first_name'] = data
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		print('last_name', data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_programs(self):
		data = self.cleaned_data['programs']
		print('programs', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data
	def clean_roles(self):
		data = self.cleaned_data['roles']
		print('roles', data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
			])
		return data

def tech_screening_choices():
	choices = [("Not Attempted","Not Attempted"),
				("Failed","Failed"),
				("Passed","Passed")]
	return choices

class Student_Status_Form(forms.ModelForm):
	tech_screening = forms.CharField(
		label="Tech Screening",
		widget=forms.RadioSelect(choices=tech_screening_choices(),
		attrs={'class': "registration_radio"})
	)

	responsive = forms.CharField(
		label="Responsive",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	confirm = forms.CharField(
		label="Confirm",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)



	approved_to_match = forms.CharField(
		label="Approved To Match",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)
	waitlist = forms.CharField(
		label="Waitlist",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)
	waitlist_reason = forms.CharField(
		max_length=2000,
		required=False,
		label="Reason Waitlist",
		widget=forms.Textarea(attrs={'class': 'form-control',
								'rows': 2})
	)

	class Meta:
		model = Student_Registration_Status
		fields = (	
					'registration',

					'responsive',
					'tech_screening',
					'approved_to_match',					
					'confirm',

										
					'approved_by',
					'date_approved',
					'last_updated_by',
					'waitlist',
					'waitlist_by',
					'date_waitlist',
					'waitlist_reason',
					)
		

	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()

class Parent_Registration_Display_Form(forms.ModelForm):
	class Meta:
		model = Parent_Registration
		fields = (
					# 'registration_language',
					# 'parent_first_name',
					# 'parent_last_name',
					# 'country',
					# 'address',
					# 'city',
					# 'state',
					# 'zip_code',
					# 'email',
					# 'phone',
					# 'county',
					# 'preferred_contact_language',----------
					# 'device_in_touch',----------
					# 'other_device_in_touch',--------
					# 'internet',
					# 'computer',
					# 'session_choices',
					# 'flexible_schedule',
					# 'parent_available',------------
					# 'parent_can_help',
					# 'help_name',
					# 'help_phone',
					# 'help_relationship',
					# 'additional_info',
					# 'consent_liability_initials',
					# 'media_release_initials',
					# 'messaging_apps',---------
					# 'other_message_app',---------
					# 'full_name_signature',---------
					)

class Student_Registration_Display_Form(forms.ModelForm):
	class Meta:
		model = Student_Registration
		
		fields = (		
				# 'program_semester',
				# 'registration_language',
				# 'parent',
				# 'child_first_name',
				# 'child_last_name',
				# 'dob',
				# 'gender',
				# 'ethnicity',
				# 'current_grade',
				# 'school',
				# 'other_school',
				# 'prior_participation',
				# 'primary_language',
				# 'other_primary_language',
				# 'secondary_language',
				# 'other_secondary_language',
				# 'reading_level',
				# 'relationship_to_child',
				# 'child_comment',
				# 'session_device',
				# 'other_session_device',
				# 'cropped_profile_image',
				# 'profile_image',
				# 'characteristics',
				)

class Volunteer_Status_Form(forms.ModelForm):
	tech_screening = forms.CharField(
		label="Tech Screening",
		widget=forms.RadioSelect(choices=tech_screening_choices(),
		attrs={'class': "registration_radio"})
	)

	video_uploaded = forms.CharField(
		label="Video Uploaded",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	video_reviewed = forms.CharField(
		label="Video Reviewed",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	live_screening_passed = forms.CharField(
		label="Live Screening Passed",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	online_training_completed = forms.CharField(
		label="Online Training Completed",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	orientation = forms.CharField(
		label="Orientation",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	reference_check = forms.CharField(
		label="References Checked",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	approved_to_match = forms.CharField(
		label="Approved To Match",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)

	approved_to_match = forms.CharField(
		label="Approved To Match",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)
	denied = forms.CharField(
		label="Application Denied",
		required=False,
		widget=forms.CheckboxInput(
		attrs={'class': "registration_radio",})
	)
	denied_reason = forms.CharField(
		max_length=2000,
		required=False,
		label="Reason Denied",
		widget=forms.Textarea(attrs={'class': 'form-control',
								'rows': 2})
	)

	class Meta:
		model = Volunteer_Registration_Status
		fields = (
				'approved_to_match',
				'registration',
				'tech_screening',
				'video_uploaded',
				'video_reviewed',
				'live_screening_passed',
				'online_training_completed',				
				'orientation',
				'reference_check',				
				'approved_by',
				'last_updated_by',
				'date_approved',
				'denied',
				'denied_by',
				'date_denied',
				'denied_reason',
				)

	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()

class Staff_Registration_Display_Form(forms.ModelForm):
	class Meta:
		model = Staff_Registration
		fields =(
				# 'dob',
				# 'first_name',
				# 'last_name',
				# 'email',
				# 'phone',
				# 'country',
				# 'city',
				# 'state',
				# 'gender',
				# 'in_school',
				# 'current_education_level',
				# 'current_education_class',
				# 'current_school',
				# 'highest_education_level',
				# 'fluent_spanish',
				# 'computer',
				# 'device_type',
				# 'cropped_profile_image',
				# 'profile_image',
				# 'user',
				)

class Volunteer_Registration_Display_Form(forms.ModelForm):
	class Meta:
		model = Volunteer_Registration
		fields = (	
					# 'program',
					# 'program_semester',
					# 'volunteer_type',
					# 'dob',
					# 'parent_name',
					# 'parent_email',
					# 'first_name',
					# 'last_name',
					# 'country',
					# 'address',
					# 'city',
					# 'state',
					# 'zip_code',
					# 'email',
					# 'phone',
					# 'gender',
					# 'ethnicity',
					# 'in_school',
					# 'current_education_level',
					# 'current_education_class',
					# 'current_school',
					# 'highest_education_level',
					# 'previously_paired',
					# 'student_name',
					# 'teamleader_name',
					# 'returning_referred',
					# 'meeting_times',
					# 'session_choices',
					# 'fluent_spanish',
					# 'opportunity_source',
					# 'social_media_source',
					# 'person_referral',
					# 'computer',
					# 'device_type',
					# 'children_experience',
					# 'reason',
					# 'other_reasons',
					# 'reason_not_listed',
					# 'volunteer_other_areas',
					# 'additional_interests',
					# 'ref_name_1',
					# 'ref_email_1',
					# 'ref_phone_1',
					# 'ref_relationship_1',
					# 'ref_name_2',
					# 'ref_email_2',
					# 'ref_phone_2',
					# 'ref_relationship_2',
					# 'agree_requirements_initials',
					# 'statements_true_initials',
					# 'remove_volunteers_initials',
					# 'cropped_profile_image',
					# 'profile_image',
					# 'web_source',
					# 'sponsor_child',
					# 'convicted',
					# 'convicted_text',
					# 'charges_pending',
					# 'charges_pending_text',
					# 'refused_participation',
					# 'refused_participation_text',
					# 'full_name_signature',
					# 'county'
					)