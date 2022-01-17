from django import forms
import re
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from localflavor.us.forms import USStateField
from localflavor.us.forms import USStateSelect
from localflavor.us.us_states import STATE_CHOICES
from django_countries import countries
from cropperjs.models import CropperImageField
from registration.models import Volunteer_Registration
from registration.models import Volunteer_Video
from registration.models import Parent_Registration
from registration.models import Staff_Registration

from registration.models import Student_Registration
from buddy_program_data.models import Question, Gender, Ethnicity, Grade
from buddy_program_data.models import Program_Semester, School
from buddy_program_data.models import Current_Education_Level
from buddy_program_data.models import Current_Education_Class
from buddy_program_data.models import Team_Meeting_Time, Session_Meeting_Option
from buddy_program_data.models import Opportunity_Source, Social_Media_Source
from buddy_program_data.models import Device_Type, Volunteer_Opportunity
from buddy_program_data.models import Volunteer_Reason, Web_Source, Language
from buddy_program_data.models import Message_App, Parent_Additional_Information
from buddy_program_data.models import Reading_Description, Student_Characteristic
from users.models import Program

from django.forms import ModelForm

from django.utils import timezone
from datetime import datetime, timedelta, date

def eng_label(fieldname, for_form):
	label = Question.objects.get(for_form__name=for_form, field_name=fieldname)
	# print("eng_text", label.eng_text)
	return label.eng_text

def span_label(fieldname, for_form):
	label = Question.objects.get(for_form__name=for_form, field_name=fieldname)
	return label.span_text

class Volunteer_Testing_Form(forms.Form):
	email = forms.CharField(
		max_length=80,
		required=False,
		label="Please enter the email associated with your volunteer registration.",
	
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('email')",
								})
	)
	
	registration=forms.ModelChoiceField(
		label="Registration",
		required=False,
		queryset = Volunteer_Registration.objects.all(),
		widget=forms.Select(choices=Volunteer_Registration.objects.all(),
		attrs={'class': "form_control_modified",
			'onclick': "clear_input_errors('registration')"})
	)

	class Meta:
		fields = ('email', 'registration')

	def clean(self):
		print("\n\n\nEnd Cleaning",)
		cleaned_data = super().clean()
		email = cleaned_data.get("email")
		if email != "":	
			if Volunteer_Registration.objects.filter(email=email).exists():
				if Volunteer_Registration.objects.filter(email=email).count() == 1:
					cleaned_data['registration'] = Volunteer_Registration.objects.get(email=email)
				else:
					cleaned_data['registration'] = Volunteer_Registration.objects.filter(email=email).first()
			else:
				cleaned_data['email'] = ""
				self.add_error('email', ValidationError(_('Volunteer Registration associated with the email was not found.'), code=''))			
		else:
			self.add_error('email', ValidationError(_('This field is required'), code='too_young'))							

		return cleaned_data

def file_size(value): # add this to some file where you can import it from
    limit = 859832320
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 1000 MB.')

def eng_label(fieldname, for_form):
	label = Question.objects.get(for_form__name=for_form, field_name=fieldname)
	# print("eng_text", label.eng_text)
	return label.eng_text

def span_label(fieldname, for_form):
	label = Question.objects.get(for_form__name=for_form, field_name=fieldname)
	return label.span_text

def country_choices(role):
	country_choices = list(countries)
	indices = [i for i, tupl in enumerate(country_choices) if tupl[0] == "US"][0]
	country_choices.pop(indices)
	country_choices.insert(0, ('', label_select(role)))
	country_choices.insert(1, ('US', "United States of America"))
	return country_choices

def state_choices(role):
	state_choices = list(STATE_CHOICES)	
	state_choices.insert(0, ('', label_select(role)))	
	state_choices.insert(1, ('', "Outside the US"))
	return state_choices

def label_select(role):
	if role =="Volunteer":
		label = "(Select One)"
	elif role == "Student":
		label = "(Select One)"
	elif role == "Parent":
		label = "(Select One)"
	
	return label

def gender_choices(role):
	genders = Gender.objects.filter(active=True)
	return genders

def yes_no_choices_eng_only():
	choices = [("Yes",'Yes'),("No",'No')]
	return choices

def device_type_choices(role):
	choices = Device_Type.objects.filter(active=True, for_users=role)
	return choices

class Staff_Registration_Form(ModelForm):
	first_name = forms.CharField(
		max_length=150,
		required=False,
		label="First Name:",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('first_name')"})
	)

	last_name = forms.CharField(
		max_length=150,
		required=False,
		label="Last Name",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('last_name')"})
	)

	city = forms.CharField(
		max_length=150,
		required=False,
		label="City",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('city')"})
	)	

	country=forms.CharField(
		label="Country",
		required=False,
		widget=forms.Select(
			choices=country_choices('Volunteer'),
			attrs={'class': 'form_control_modified',
				'onclick': "clear_input_errors('country')"}
		)
	)

	

	state=forms.CharField(
		label="State",
		required=False,
		widget=forms.Select(
			choices=state_choices('Volunteer'),
			attrs={'class': 'form_control_modified',
					'onclick': "clear_input_errors('state')"}
		)
	)

	email = forms.CharField(
		max_length=80,
		required=False,
		label="Email",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('email')",
								'onblur':"email_blur('blur',this);return false;",})
	)

	phone = forms.CharField(
		max_length=150,
		required=False,
		label="Phone",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('phone')"})
	)

	dob = forms.DateField(
		label="Date Of Birth",
		required=False,
		widget=forms.DateInput(attrs={'type': 'date', 'class': 'form_control_modified_min_height',
								'max':"9999-12-31",
								'onclick': "clear_input_errors('dob')",								
								}),
	)

	gender=forms.ModelChoiceField(
		label=eng_label('gender', 'Volunteer Registration'),
		help_text=span_label('gender', 'Volunteer Registration'),
		required=False,
		queryset = gender_choices('Volunteer'),
		widget=forms.RadioSelect(choices=gender_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('gender')"})
	)

	in_school=forms.CharField(
		label=eng_label('in_school', 'Volunteer Registration'),
		help_text=span_label('in_school', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('in_school')"})
	)

	current_education_level=forms.ModelChoiceField(
		label=eng_label('current_education_level', 'Volunteer Registration'),
		help_text=span_label('current_education_level', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Level.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('current_education_level')"})
	)

	current_education_class=forms.ModelChoiceField(
		label=eng_label('current_education_class', 'Volunteer Registration'),
		help_text=span_label('current_education_class', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Class.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('current_education_class')"})
	)

	current_school = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('current_school', 'Volunteer Registration'),
		help_text=span_label('current_school', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('current_school')"})
	)

	highest_education_level=forms.ModelChoiceField(
		label=eng_label('highest_education_level', 'Volunteer Registration'),
		help_text=span_label('highest_education_level', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Level.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('highest_education_level')"})
	)


	fluent_spanish=forms.CharField(
		label=eng_label('fluent_spanish', 'Volunteer Registration'),
		help_text=span_label('fluent_spanish', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('fluent_spanish')"})
	)


	computer=forms.CharField(
		label=eng_label('computer', 'Volunteer Registration'),
		help_text=span_label('computer', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('computer')"})
	)

	device_type=forms.ModelChoiceField(
		label=eng_label('device_type', 'Volunteer Registration'),
		help_text=span_label('device_type', 'Volunteer Registration'),
		required=False,
		queryset = device_type_choices('Volunteer'),
		widget=forms.RadioSelect(choices=device_type_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('device_type')"})
	)


	profile_image = forms.ImageField(
		required=False,
		label=eng_label('profile_image', 'Volunteer Registration'),
		help_text=span_label('profile_image', 'Volunteer Registration'),
		widget=forms.ClearableFileInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('profile_image')",
								'onchange':"readURL(this)"}))

	

	class Meta:
		model = Staff_Registration
		# fields=('__all__')
		fields = (	
					'first_name',
					'last_name',					
					'email',
					'phone',
					'country',
					'city',
					'state',
					'gender',
					'dob',
					'in_school',
					'current_education_level',
					'current_education_class',
					'current_school',
					'highest_education_level',
					'fluent_spanish',
					'computer',
					'device_type',
					# 'cropped_profile_image',
					'profile_image',
					# 'user' ,
					)

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
       
                       
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
       
                       
		return data

	def clean_email(self):
		data = self.cleaned_data['email']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		else:
			invalid_email = False
			try:
				invalid_email = validate_email(data)

			except Exception as e:
				print("invalid_email EMAIL", invalid_email)
				raise ValidationError([
					ValidationError(_('Please enter a valid email'), code='error1'),
					# ValidationError(_('Por favor introduzca una dirección de correo electrónico válida'), code='error2'),
				])

			print("invalid_email EMAIL", invalid_email)

			if not invalid_email:
				if Volunteer_Registration.objects.filter(email = data).exists():
					raise ValidationError([
						ValidationError(_('The email is already in our system. The application cannot be submitted'), code='error1'),
						# ValidationError(_('Por favor introduzca una dirección de correo electrónico válida'), code='error2'),
					])
			
		return data

	def clean_phone(self):
		data = self.cleaned_data['phone']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_dob(self):
		data = self.cleaned_data['dob']
		# print("DOB", data)
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_gender(self):
		# print("Cleaning GENDER")
		data = self.cleaned_data['gender']

		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data


	def clean_in_school(self):
		data = self.cleaned_data['in_school']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data


	def clean_fluent_spanish(self):
		data = self.cleaned_data['fluent_spanish']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_computer(self):
		data = self.cleaned_data['computer']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_profile_image(self):
		data = self.cleaned_data['profile_image']
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data
		

	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()
		in_school = cleaned_data.get("in_school")
		computer = cleaned_data.get("computer")
		profile_image = cleaned_data.get("profile_image")
		country = cleaned_data.get('country')
		city = cleaned_data.get('city')
		state = cleaned_data.get('state')

		if country:
			print("COUNTRY", country)
			if country == "US":
				if city == "":
					self.add_error('city', ValidationError(_('This field is required'), code='required'))
				if not state:
					self.add_error('state', ValidationError(_('This field is required'), code='required'))			
		else:
			self.add_error('country', ValidationError(_('This field is required'), code='required'))							
		
		if in_school:
			# print("In SCHOOL", in_school)
			if in_school == "Yes":
				current_education_level = cleaned_data.get("current_education_level")
				current_education_class = cleaned_data.get("current_education_class")
				current_school = cleaned_data.get("current_school")

				if not current_education_level:
					self.add_error('current_education_level', ValidationError(_('This field is required'), code='too_young'))							

				if not current_education_class:
					self.add_error('current_education_class', ValidationError(_('This field is required'), code='too_young'))							

				if not current_school:
					self.add_error('current_school', ValidationError(_('This field is required'), code='too_young'))							


			elif in_school == "No":
				highest_education_level = cleaned_data.get("highest_education_level")
				if not highest_education_level:
					self.add_error('highest_education_level', ValidationError(_('This field is required'), code='too_young'))							

		if computer:
			if computer == "Yes":
				device_type = cleaned_data.get("device_type")
				if not device_type:
					self.add_error('device_type', ValidationError(_('This field is required'), code='required'))



class Volunteer_Video_Form(ModelForm):
	email = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('email', 'Volunteer Video'),
		help_text=span_label('email', 'Volunteer Video'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('email')",
								'onblur':"email_video_blur('blur',this);return false;"})
	)

	videofile = forms.FileField(
		validators=[file_size],
		required=False,
		label=eng_label('videofile', 'Volunteer Video'),
		help_text=span_label('videofile', 'Volunteer Video'),
		widget=forms.ClearableFileInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('videofile')",
								}))

	class Meta:
		model = Volunteer_Video
		fields = ('email','videofile', 'registration')

	def clean(self):
		print("\n\n\nEnd Cleaning",)
		cleaned_data = super().clean()
		email = cleaned_data.get("email")
		registration = cleaned_data.get("registration")
		videofile = cleaned_data.get("videofile")
		if email != "":	
			if Volunteer_Registration.objects.filter(email=email).exists():
				if Volunteer_Registration.objects.filter(email=email).count() == 1:
					cleaned_data['registration'] = Volunteer_Registration.objects.get(email=email)
				else:
					cleaned_data['registration'] = Volunteer_Registration.objects.filter(email=email).first()			
		
		return cleaned_data

def characteristics_choices():
	choices = Student_Characteristic.objects.filter(active = True).order_by('id')
	return choices

def reading_desc_choices():
	choices = Reading_Description.objects.filter(active = True).order_by('id')
	return choices

def primary_language_choices():
	choices = Language.objects.filter(display_primary = True)
	return choices

def secondary_language_choices():
	choices = Language.objects.filter(display_secondary = True)
	return choices

def student_school_choices():
	choices = School.objects.filter(active=True, display_in_list=True)
	return choices


def additional_info_choices():
	choices = Parent_Additional_Information.objects.filter(active=True)
	return choices

def session_time_choices():
	times = Session_Meeting_Option.objects.filter(active=True)
	return times



def validate_zip_code(value):
	match = (re.match(r'^\d{5}(?:[-\s]\d{4})?$',value)  )
	# print("Zip CODE", match)
	if match:
		return True
	else:
		return False

def message_app_choices():
	choices = Message_App.objects.filter(active=True)
	return choices





def get_language_choices():
	languages = Language.objects.all()	
	return languages








class Student_Registration_Form(ModelForm):
	registration_language=forms.ModelChoiceField(
		# label=eng_label('language', 'Student Pre-Registration'),
		# help_text=span_label('language', 'Student Pre-Registration'),
		required=False,
		queryset = get_language_choices(),
		widget=forms.RadioSelect(choices=get_language_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('registration_language')"})
	)

	child_first_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('child_first_name', 'Student Registration'),
		help_text=span_label('child_first_name', 'Student Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('child_first_name')"})
	)

	child_last_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('child_last_name', 'Student Registration'),
		help_text=span_label('child_last_name', 'Student Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('child_last_name')"})
	)

	dob = forms.DateField(
		label=eng_label('dob', 'Student Registration'),
		help_text=span_label('dob', 'Student Registration'),
		required=False,
		widget=forms.DateInput(attrs={'type': 'date', 'class': 'form_control_modified_min_height',
								'max':"9999-12-31",
								'onclick': "clear_input_errors('dob')",								
								}),
	)

	gender=forms.ModelChoiceField(
		label=eng_label('gender', 'Student Registration'),
		help_text=span_label('gender', 'Student Registration'),
		required=False,
		queryset = gender_choices('Student'),
		widget=forms.RadioSelect(choices=gender_choices('Student'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('gender')"})
	)

	ethnicity=forms.ModelChoiceField(
		label=eng_label('ethnicity', 'Student Registration'),
		help_text=span_label('ethnicity', 'Student Registration'),
		required=False,
		empty_label=label_select('Student'),
		queryset = Ethnicity.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('ethnicity')"})
	)

	current_grade=forms.ModelChoiceField(
		label=eng_label('current_grade', 'Student Registration'),
		help_text=span_label('current_grade', 'Student Registration'),
		required=False,
		queryset = Grade.objects.all(),
		widget=forms.RadioSelect(choices=Grade.objects.all(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('current_grade')"})
	)

	school=forms.ModelChoiceField(
		label=eng_label('school', 'Student Registration'),
		help_text=span_label('school', 'Student Registration'),
		required=False, 
		queryset = student_school_choices(),
		widget=forms.RadioSelect(choices=student_school_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('school')"})
	)

	other_school = forms.CharField(
		max_length=255,
		required=False,
		label="",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('other_school')"})
	) 

	prior_participation=forms.CharField(
		label=eng_label('prior_participation', 'Student Registration'),
		help_text=span_label('prior_participation', 'Student Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('prior_participation')"})
	)

	primary_language=forms.ModelChoiceField(
		label=eng_label('primary_language', 'Student Registration'),
		help_text=span_label('primary_language', 'Student Registration'),
		required=False,
		queryset = primary_language_choices(),
		widget=forms.RadioSelect(choices=primary_language_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('primary_language')"})
	)

	other_primary_language = forms.CharField(
		max_length=255,
		required=False,
		label="",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('other_primary_language')"})
	) 

	secondary_language=forms.ModelChoiceField(
		label=eng_label('secondary_language', 'Student Registration'),
		help_text=span_label('secondary_language', 'Student Registration'),
		required=False,
		queryset = secondary_language_choices(),
		widget=forms.RadioSelect(choices=secondary_language_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('secondary_language')"})
	)

	other_secondary_language = forms.CharField(
		max_length=255,
		required=False,
		label="",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('other_secondary_language')"})
	) 

	reading_level=forms.ModelChoiceField(
		label=eng_label('reading_level', 'Student Registration'),
		help_text=span_label('reading_level', 'Student Registration'),
		required=False,
		queryset = reading_desc_choices(),
		widget=forms.RadioSelect(choices=reading_desc_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('reading_level')"})
	)

	relationship_to_child = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('relationship_to_child', 'Student Registration'),
		help_text=span_label('relationship_to_child', 'Student Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('relationship_to_child')"})
	)

	session_device=forms.ModelChoiceField(
		label=eng_label('session_device', 'Student Registration'),
		help_text=span_label('session_device', 'Student Registration'),
		required=False,
		queryset = device_type_choices('Student'),
		widget=forms.RadioSelect(choices=device_type_choices('Student'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('session_device')"})
	)

	other_session_device = forms.CharField(
		max_length=255,
		required=False,
		label="",
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('session_device')"})
	) 

	characteristics=forms.ModelMultipleChoiceField(
		label=eng_label('characteristics', 'Student Registration'),
		help_text=span_label('characteristics', 'Student Registration'),
		required=False,
		queryset=characteristics_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=characteristics_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('characteristics')"})
	)

	child_comment = forms.CharField(
		max_length=3000,
		required=False,
		label=eng_label('child_comment', 'Student Registration'),
		help_text=span_label('child_comment', 'Student Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('child_comment')",
								'rows': 5})
	)

	profile_image = forms.ImageField(
		required=False,
		label=eng_label('profile_image', 'Student Registration'),
		help_text=span_label('profile_image', 'Student Registration'),
		widget=forms.ClearableFileInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('profile_image')",
								'onchange':"readURL(this)"}))


	class Meta:
		model = Student_Registration
		fields = ('program_semester', 'registration_language',
				'parent', 'child_first_name', 'child_last_name', 'dob',
				'gender', 'ethnicity', 'current_grade',
				'school', 'other_school',
				'prior_participation',
				'primary_language', 'other_primary_language',
				'secondary_language', 'other_secondary_language',
				'reading_level', 'relationship_to_child',
				'session_device', 'other_session_device',
				'characteristics',
				'child_comment', 
				'profile_image'
				)

	def clean(self):
		print("\n\n\nEnd Cleaning",)
		cleaned_data = super().clean()
		registration_language = cleaned_data.get("registration_language")
		profile_image = cleaned_data.get("profile_image")
		child_first_name = cleaned_data.get("child_first_name")
		child_last_name = cleaned_data.get("child_last_name")
		dob = cleaned_data.get("dob")
		gender = cleaned_data.get("gender")
		ethnicity = cleaned_data.get("ethnicity")
		current_grade = cleaned_data.get('current_grade')
		school = cleaned_data.get('school')
		other_school = cleaned_data.get('other_school')
		prior_participation = cleaned_data.get('prior_participation')
		primary_language = cleaned_data.get('primary_language')
		secondary_language = cleaned_data.get('secondary_language')
		other_primary_language = cleaned_data.get('other_primary_language')
		other_secondary_language = cleaned_data.get('other_secondary_language')
		reading_level = cleaned_data.get('reading_level')
		relationship_to_child = cleaned_data.get('relationship_to_child')
		session_device = cleaned_data.get('session_device')
		other_session_device = cleaned_data.get('other_session_device')
		characteristics = cleaned_data.get('characteristics')
		child_comment = cleaned_data.get('child_comment')
		print("Profile Image", profile_image)


		if registration_language:
			if registration_language.iso == "en":
				required_error_text = 'This field is required'
			elif registration_language.iso == "es":
				required_error_text = 'Este campo es obligatorio'

		if child_first_name == "":
			self.add_error('child_first_name', ValidationError(_(required_error_text), code='required'))

		if child_last_name == "":
			self.add_error('child_last_name', ValidationError(_(required_error_text), code='required'))

		if not dob:
			self.add_error('dob', ValidationError(_(required_error_text), code='required'))
		
		if not gender:
			self.add_error('gender', ValidationError(_(required_error_text), code='required'))

		if not ethnicity:
			self.add_error('ethnicity', ValidationError(_(required_error_text), code='required'))

		if not current_grade:
			self.add_error('current_grade', ValidationError(_(required_error_text), code='required'))

		if not school:
			self.add_error('school', ValidationError(_(required_error_text), code='required'))
		else:
			if school.name == "Other (Please Specify)":
				if other_school == "":
					self.add_error('other_school', ValidationError(_(required_error_text), code='required'))

		if prior_participation == "":
			self.add_error('prior_participation', ValidationError(_(required_error_text), code='required'))

		if not primary_language:
			self.add_error('primary_language', ValidationError(_(required_error_text), code='required'))
		else:
			if primary_language.eng_name == "Other (Please Specify)":
				if other_primary_language == "":
					self.add_error('other_primary_language', ValidationError(_(required_error_text), code='required'))

		if not secondary_language:
			self.add_error('secondary_language', ValidationError(_(required_error_text), code='required'))
		else:
			if secondary_language.eng_name == "Other (Please Specify)":
				if other_secondary_language == "":
					self.add_error('other_secondary_language', ValidationError(_(required_error_text), code='required'))

		if not reading_level:
			self.add_error('reading_level', ValidationError(_(required_error_text), code='required'))

		if relationship_to_child == "":
			self.add_error('relationship_to_child', ValidationError(_(required_error_text), code='required'))

		if not session_device:
			self.add_error('session_device', ValidationError(_(required_error_text), code='required'))
		else:
			if session_device.name == "Other (Please Specify)":
				if other_session_device == "":
					self.add_error('other_session_device', ValidationError(_(required_error_text), code='required'))

		if not profile_image:
			self.add_error('profile_image', ValidationError(_(required_error_text), code='required'))

		if characteristics.count() == 0:
			self.add_error('characteristics', ValidationError(_(required_error_text), code='required'))

		if child_comment == "":
			self.add_error('child_comment', ValidationError(_(required_error_text), code='required'))

class Pre_Registration_Form(forms.Form):

	language=forms.ModelChoiceField(
		label=eng_label('language', 'Student Pre-Registration'),
		help_text=span_label('language', 'Student Pre-Registration'),
		required=False,
		queryset = get_language_choices(),
		widget=forms.RadioSelect(choices=get_language_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('language')"})
	)

	class Meta:
		fields = ('language',)

class Parent_Registration_Form(ModelForm):

	registration_language=forms.ModelChoiceField(
		# label=eng_label('language', 'Student Pre-Registration'),
		# help_text=span_label('language', 'Student Pre-Registration'),
		required=False,
		queryset = get_language_choices(),
		widget=forms.RadioSelect(choices=get_language_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('registration_language')"})
	)

	parent_first_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('parent_first_name', 'Parent Registration'),
		help_text=span_label('parent_first_name', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('parent_first_name')"})
	)

	parent_last_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('parent_last_name', 'Parent Registration'),
		help_text=span_label('parent_last_name', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('parent_last_name')"})
	)

	email = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('email', 'Parent Registration'),
		help_text=span_label('email', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('email')",
								'onblur':"email_blur('blur',this);return false;",})
	)

	phone = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('phone', 'Parent Registration'),
		help_text=span_label('phone', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('phone')"})
	) 

	country=forms.CharField(
		label=eng_label('country', 'Parent Registration'),
		# initial = "US",
		help_text=span_label('country', 'Parent Registration'),
		required=False,
		widget=forms.Select(
			choices=country_choices('Parent'),
			attrs={'class': 'form_control_modified',
				'onclick': "clear_input_errors('country')"}
		)
	)

	address = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('address', 'Parent Registration'),
		help_text=span_label('address', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('address')"})
	)

	city = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('city', 'Parent Registration'),
		help_text=span_label('city', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('city')"})
	)

	state=forms.CharField(
		label=eng_label('state', 'Parent Registration'),
		help_text=span_label('state', 'Parent Registration'),
		required=False,
		widget=forms.Select(
			choices=state_choices('Parent'),
			attrs={'class': 'form_control_modified',
					'onclick': "clear_input_errors('state')"}
		)
	)

	zip_code = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('zip_code', 'Parent Registration'),
		help_text=span_label('zip_code', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('zip_code')"})
	)

	county = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('county', 'Parent Registration'),
		help_text=span_label('county', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('county')"})
	)

	internet=forms.CharField(
		label=eng_label('internet', 'Parent Registration'),
		help_text=span_label('internet', 'Parent Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('internet')"})
	)

	computer=forms.CharField(
		label=eng_label('computer', 'Parent Registration'),
		help_text=span_label('computer', 'Parent Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('computer')"})
	)


	session_choices=forms.ModelMultipleChoiceField(
		label=eng_label('session_choices', 'Parent Registration'),
		help_text=span_label('session_choices', 'Parent Registration'),
		required=False,
		queryset=session_time_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=session_time_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('session_choices')"})
	)

	flexible_schedule=forms.CharField(
		label=eng_label('flexible_schedule', 'Parent Registration'),
		help_text=span_label('flexible_schedule', 'Parent Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('flexible_schedule')"})
	)


	parent_can_help=forms.CharField(
		label=eng_label('parent_can_help', 'Parent Registration'),
		help_text=span_label('parent_can_help', 'Parent Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('parent_can_help')"})
	)

	help_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('help_name', 'Parent Registration'),
		help_text=span_label('help_name', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('help_name')"})
	)

	help_phone = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('help_phone', 'Parent Registration'),
		help_text=span_label('help_phone', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('help_phone')"})
	)

	help_relationship = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('help_relationship', 'Parent Registration'),
		help_text=span_label('help_relationship', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('help_relationship')"})
	)

	additional_info=forms.ModelMultipleChoiceField(
		label=eng_label('additional_info', 'Parent Registration'),
		help_text=span_label('additional_info', 'Parent Registration'),
		required=False,
		queryset=additional_info_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=additional_info_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('additional_info')"})
	)

	consent_liability_initials = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('consent_liability_initials', 'Parent Registration'),
		help_text=span_label('consent_liability_initials', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('consent_liability_initials')"})
	)

	media_release_initials = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('media_release_initials', 'Parent Registration'),
		help_text=span_label('media_release_initials', 'Parent Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('statements_true_initials')"})
	)  


	class Meta:
		model = Parent_Registration
		fields = ('registration_language','parent_first_name', 'parent_last_name', 'email', 'phone',
				'country', 'address', 'city', 'state', 'zip_code', 'county',
				'internet', 'computer',
				'session_choices', 'flexible_schedule',
				  'parent_can_help',
				'help_name','help_phone', 'help_relationship',
				'additional_info',
				'consent_liability_initials', 'media_release_initials',
				  )

	def clean(self):
		print("\n\n\nEnd Cleaning",)
		cleaned_data = super().clean()
		registration_language = cleaned_data.get("registration_language")
		parent_first_name = cleaned_data.get("parent_first_name")
		parent_last_name = cleaned_data.get("parent_last_name")
		email = cleaned_data.get("email")
		phone = cleaned_data.get("phone")
		country = cleaned_data.get('country')
		address = cleaned_data.get('address')
		city = cleaned_data.get('city')
		state = cleaned_data.get('state')
		zip_code = cleaned_data.get('zip_code')
		county = cleaned_data.get('county')
		internet = cleaned_data.get('internet')
		computer = cleaned_data.get('computer')
		session_choices = cleaned_data.get('session_choices')
		flexible_schedule = cleaned_data.get('flexible_schedule')
		parent_can_help = cleaned_data.get('parent_can_help')
		help_name = cleaned_data.get('help_name')
		help_phone = cleaned_data.get('help_phone')
		help_relationship = cleaned_data.get('help_relationship')
		consent_liability_initials = cleaned_data.get('consent_liability_initials')
		media_release_initials = cleaned_data.get('media_release_initials')

		if registration_language:
			if registration_language.iso == "en":
				required_error_text = 'This field is required'
				invalid_zip = "Please enter a valid zip code (55555 or 55555-5555)"
				invalid_email = "Enter a valid email"
				already_exists = "An application with the email already exists.  The application can not be submitted."
			elif registration_language.iso == "es":
				required_error_text = 'Este campo es obligatorio'
				invalid_zip = "Ingrese un código postal válido (55555 o 55555-5555)"
				invalid_email = "Introduzca un correo electrónico válido"
				already_exists = "Ya existe una aplicación con el correo electrónico. No se puede enviar la solicitud."
				

		if parent_first_name == "":
			self.add_error('parent_first_name', ValidationError(_(required_error_text), code='required'))

		if parent_last_name == "":
			self.add_error('parent_last_name', ValidationError(_(required_error_text), code='required'))

		if email == "":
			self.add_error('email', ValidationError(_(required_error_text), code='required'))

		else:
			try:
				invalid_email = validate_email(email)

			except Exception as e:
				print("invalid_email EMAIL", invalid_email)
				self.add_error('email', ValidationError(_(invalid_email), code='required'))				

			print("invalid_email EMAIL", invalid_email)

			if not invalid_email:
				if Parent_Registration.objects.filter(email = email).exists():
					self.add_error('email', ValidationError(_(already_exists), code='required'))	

		if phone == "":
			self.add_error('phone', ValidationError(_(required_error_text), code='required'))

		if country:
			if country == "US":
				print("US")
				if address == "":
					self.add_error('address', ValidationError(_(required_error_text), code='required'))
				if city == "":
					self.add_error('city', ValidationError(_(required_error_text), code='required'))
				if not state:
					self.add_error('state', ValidationError(_(required_error_text), code='required'))
				
				if zip_code == "":
					self.add_error('zip_code', ValidationError(_(required_error_text), code='required'))
				else:
					valid = validate_zip_code(zip_code)
					if not valid:
						self.add_error('zip_code', ValidationError(_(invalid_zip), code='required'))

				if county == "":
					self.add_error('county', ValidationError(_(required_error_text), code='required'))
		else:
			self.add_error('country', ValidationError(_(required_error_text), code='required'))	

		if internet == "":
			self.add_error('internet', ValidationError(_(required_error_text), code='required'))

		if computer == "":
			self.add_error('computer', ValidationError(_(required_error_text), code='required'))

		if session_choices.count() == 0:
			self.add_error('session_choices', ValidationError(_(required_error_text), code='required'))

		# if messaging_apps.count() == 0:
		# 	self.add_error('messaging_apps', ValidationError(_(required_error_text), code='required'))

		if flexible_schedule == "":
			self.add_error('flexible_schedule', ValidationError(_(required_error_text), code='required'))

		if parent_can_help == "":
			self.add_error('parent_can_help', ValidationError(_(required_error_text), code='required'))
		else:
			if parent_can_help == "No":
				if help_name == "":
					self.add_error('help_name', ValidationError(_(required_error_text), code='required'))
				if help_phone == "":
					self.add_error('help_phone', ValidationError(_(required_error_text), code='required'))
				if help_relationship == "":
					self.add_error('help_relationship', ValidationError(_(required_error_text), code='required'))



		if consent_liability_initials == "":
			self.add_error('consent_liability_initials', ValidationError(_(required_error_text), code='required'))

		if media_release_initials == "":
			self.add_error('media_release_initials', ValidationError(_(required_error_text), code='required'))
		

def team_meeting_times():
	team_times = Team_Meeting_Time.objects.filter(active=True)
	return team_times



def volunteer_opportunity_choices():
	choices = Volunteer_Opportunity.objects.filter(active=True)
	return choices

def volunteer_other_reasons():
	choices = Volunteer_Reason.objects.filter(active=True)
	return choices



def get_start_date_program(program):
	start = program.program_semester.start_date
	return start

def get_today_local():
	today = timezone.localtime(timezone.now()).date() 
	return today

def age_at_start(program_semester, role, born):

	start_date = program_semester.start_date
	try:
		birthday = born.replace(year = start_date.year) 

	except ValueError:
		birthday = born.replace(year = start_date.year,
				month = born.month + 1, day = 1) 

	if birthday > start_date:
		return start_date.year - born.year - 1
	else:
		return start_date.year - born.year 


def years_for_range(role):
	today = get_today_local()

	if role == "Volunteer":
		start = today.year - 80
		end = today.year - 13
	elif role == "Student":
		start = today.year - 14
		end = today.year - 4
	years =range(start, end)
	return years

def calculateAge(born):
	today = get_today_local()
	try:
		birthday = born.replace(year = today.year) 

	except ValueError:
		birthday = born.replace(year = today.year,
				month = born.month + 1, day = 1) 

	if birthday > today:
		return today.year - born.year - 1
	else:
		return today.year - born.year 

def volunteer_type_choices():
	choices = [("New",'New Volunteer'),("Returning",'Returning Volunteer')]
	return choices

def yes_no_choices_eng_only():
	choices = [("Yes",'Yes'),("No",'No')]
	return choices

def social_media_choices(role):
	choices = Social_Media_Source.objects.filter(active=True)
	return choices

def web_source_choices(role):
	choices = Web_Source.objects.filter(active=True)
	return choices

def opportunity_source_choices(role):
	choices = Opportunity_Source.objects.filter(active=True)
	return choices	

def empty_label_field(fieldname, role):
	label = Question.objects.get(field_name=fieldname)
	if role =="Volunteer":
		empty_text = "(Select " + label.eng_text + ")"
	elif role == "Student":
		empty_text = "(Select " + label.eng_text + " / " + label.span_text + ")"
	return empty_text


class Volunteer_Registration_Form(ModelForm):
	# program=forms.ModelChoiceField(
	# 	label=eng_label('program', 'Volunteer Registration'),
	# 	help_text=span_label('program', 'Volunteer Registration'),
	# 	required=False,
	# 	# initial=1,
	# 	empty_label=label_select('Volunteer'),
	# 	queryset = Program.objects.all(),
	# 	widget=forms.Select(attrs={'class': "form_control_modified",
	# 								'onclick': "clear_input_errors('program')"})
	# )

	program_semester=forms.ModelChoiceField(
		label=eng_label('program_semester', 'Volunteer Registration'),
		help_text=span_label('program_semester', 'Volunteer Registration'),
		required=False,
		# initial=1,
		empty_label=label_select('Volunteer'),
		queryset = Program_Semester.objects.filter(active_semester=True),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('program_semester')"})
	)

	volunteer_type=forms.CharField(
		label=eng_label('volunteer_type', 'Volunteer Registration'),
		help_text=span_label('volunteer_type', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=volunteer_type_choices(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('volunteer_type')"})
	)

	first_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('first_name', 'Volunteer Registration'),
		help_text=span_label('first_name', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('first_name')"})
	)

	last_name = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('last_name', 'Volunteer Registration'),
		help_text=span_label('last_name', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('last_name')"})
	)

	address = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('address', 'Volunteer Registration'),
		help_text=span_label('address', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('address')"})
	)

	city = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('city', 'Volunteer Registration'),
		help_text=span_label('city', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('city')"})
	)

	

	country=forms.CharField(
		label=eng_label('country', 'Volunteer Registration'),
		help_text=span_label('country', 'Volunteer Registration'),
		required=False,
		widget=forms.Select(
			choices=country_choices('Volunteer'),
			attrs={'class': 'form_control_modified',
				'onclick': "clear_input_errors('country')"}
		)
	)

	

	state=forms.CharField(
		label=eng_label('state', 'Volunteer Registration'),
		help_text=span_label('state', 'Volunteer Registration'),
		required=False,
		widget=forms.Select(
			choices=state_choices('Volunteer'),
			attrs={'class': 'form_control_modified',
					'onclick': "clear_input_errors('state')"}
		)
	)

	zip_code = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('zip_code', 'Volunteer Registration'),
		help_text=span_label('zip_code', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('zip_code')"})
	)

	email = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('email', 'Volunteer Registration'),
		help_text=span_label('email', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('email')",
								'onblur':"email_blur('blur',this);return false;",})
	)

	phone = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('phone', 'Volunteer Registration'),
		help_text=span_label('phone', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('phone')"})
	)

	dob = forms.DateField(
		label=eng_label('dob', 'Volunteer Registration'),
		help_text=span_label('dob', 'Volunteer Registration'),
		required=False,
		widget=forms.DateInput(attrs={'type': 'date', 'class': 'form_control_modified_min_height',
								'max':"9999-12-31",
								'onclick': "clear_input_errors('dob')",
								'onblur':"elog('blur',this);return false;",
								# 'oninput': "elog('input',this);return false;",
								# 'onchange':"elog('change',this);return false;",								
								# 'onfocus':"elog('focus',this);return false;",
								# 'onkeyup':"elog('keyup-'+event.keyCode,this);return false;",
								# 'onkeypress':"elog('keypress-'+event.keyCode,this);if(event.keyCode==13){this.onchange();return false;}"
								}),
	)

	parent_name = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('parent_name', 'Volunteer Registration'),
		help_text=span_label('parent_name', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('parent_name')"})
	)

	parent_email = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('parent_email', 'Volunteer Registration'),
		help_text=span_label('parent_email', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('parent_email')"})
	)


	gender=forms.ModelChoiceField(
		label=eng_label('gender', 'Volunteer Registration'),
		help_text=span_label('gender', 'Volunteer Registration'),
		required=False,
		queryset = gender_choices('Volunteer'),
		widget=forms.RadioSelect(choices=gender_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('gender')"})
	)

	ethnicity=forms.ModelChoiceField(
		label=eng_label('ethnicity', 'Volunteer Registration'),
		help_text=span_label('ethnicity', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Ethnicity.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('ethnicity')"})
	)

	in_school=forms.CharField(
		label=eng_label('in_school', 'Volunteer Registration'),
		help_text=span_label('in_school', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('in_school')"})
	)

	current_education_level=forms.ModelChoiceField(
		label=eng_label('current_education_level', 'Volunteer Registration'),
		help_text=span_label('current_education_level', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Level.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('current_education_level')"})
	)

	current_education_class=forms.ModelChoiceField(
		label=eng_label('current_education_class', 'Volunteer Registration'),
		help_text=span_label('current_education_class', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Class.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('current_education_class')"})
	)

	current_school = forms.CharField(
		max_length=150,
		required=False,
		label=eng_label('current_school', 'Volunteer Registration'),
		help_text=span_label('current_school', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('current_school')"})
	)

	highest_education_level=forms.ModelChoiceField(
		label=eng_label('highest_education_level', 'Volunteer Registration'),
		help_text=span_label('highest_education_level', 'Volunteer Registration'),
		required=False,
		empty_label=label_select('Volunteer'),
		queryset = Current_Education_Level.objects.all(),
		widget=forms.Select(attrs={'class': "form_control_modified",
									'onclick': "clear_input_errors('highest_education_level')"})
	)

	previously_paired=forms.CharField(
		label=eng_label('previously_paired', 'Volunteer Registration'),
		help_text=span_label('previously_paired', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('previously_paired')"})
	)

	student_name = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('student_name', 'Volunteer Registration'),
		help_text=span_label('student_name', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('student_name')"})
	)

	teamleader_name = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('teamleader_name', 'Volunteer Registration'),
		help_text=span_label('teamleader_name', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('teamleader_name')"})
	)

	returning_referred = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('returning_referred', 'Volunteer Registration'),
		help_text=span_label('returning_referred', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('returning_referred')"})
	)

	meeting_times=forms.ModelMultipleChoiceField(
		label=eng_label('meeting_times', 'Volunteer Registration'),
		help_text=span_label('meeting_times', 'Volunteer Registration'),
		required=False,
		queryset=team_meeting_times(),
		widget=forms.CheckboxSelectMultiple(
									choices=team_meeting_times(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('meeting_times')"})
	)

	session_choices=forms.ModelMultipleChoiceField(
		label=eng_label('session_choices', 'Volunteer Registration'),
		help_text=span_label('session_choices', 'Volunteer Registration'),
		required=False,
		queryset=session_time_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=session_time_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('session_choices')"})
	)

	fluent_spanish=forms.CharField(
		label=eng_label('fluent_spanish', 'Volunteer Registration'),
		help_text=span_label('fluent_spanish', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
								attrs={'class': "registration_radio",
								'onclick': "clear_input_errors('fluent_spanish')"})
	)

	opportunity_source=forms.ModelChoiceField(
		label=eng_label('opportunity_source', 'Volunteer Registration'),
		help_text=span_label('opportunity_source', 'Volunteer Registration'),
		required=False,
		queryset = opportunity_source_choices('Volunteer'),
		widget=forms.RadioSelect(choices=opportunity_source_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('opportunity_source')"})
	)

	social_media_source=forms.ModelChoiceField(
		label=eng_label('social_media_source', 'Volunteer Registration'),
		help_text=span_label('social_media_source', 'Volunteer Registration'),
		required=False,
		queryset = social_media_choices('Volunteer'),
		widget=forms.RadioSelect(choices=social_media_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('social_media_source')"})
	)


	web_source = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('web_source', 'Volunteer Registration'),
		help_text=span_label('web_source', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('web_source')"})
	)


	person_referral = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('person_referral', 'Volunteer Registration'),
		help_text=span_label('person_referral', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('person_referral')"})
	)

	computer=forms.CharField(
		label=eng_label('computer', 'Volunteer Registration'),
		help_text=span_label('computer', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('computer')"})
	)

	device_type=forms.ModelChoiceField(
		label=eng_label('device_type', 'Volunteer Registration'),
		help_text=span_label('device_type', 'Volunteer Registration'),
		required=False,
		queryset = device_type_choices('Volunteer'),
		widget=forms.RadioSelect(choices=device_type_choices('Volunteer'),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('device_type')"})
	)

	children_experience = forms.CharField(
		max_length=5000,
		required=False,
		label=eng_label('children_experience', 'Volunteer Registration'),
		help_text=span_label('children_experience', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('children_experience')",
								'rows': 5})
	)

	reason = forms.CharField(
		max_length=5000,
		required=False,
		label=eng_label('reason', 'Volunteer Registration'),
		help_text=span_label('reason', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('reason')",
								'rows': 5})
	)

	volunteer_other_areas = forms.CharField(
		label=eng_label('volunteer_other_areas', 'Volunteer Registration'),
		help_text=span_label('volunteer_other_areas', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('volunteer_other_areas')"})
	)

	additional_interests=forms.ModelMultipleChoiceField(
		label=eng_label('additional_interests', 'Volunteer Registration'),
		help_text=span_label('additional_interests', 'Volunteer Registration'),
		required=False,
		queryset=volunteer_opportunity_choices(),
		widget=forms.CheckboxSelectMultiple(
									choices=volunteer_opportunity_choices(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('additional_interests')"})
	)

	ref_name_1 = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('ref_name_1', 'Volunteer Registration'),
		help_text=span_label('ref_name_1', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_name_1')"})
	)

	ref_email_1 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_email_1', 'Volunteer Registration'),
		help_text=span_label('ref_email_1', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_email_1')"})
	)

	ref_phone_1 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_phone_1', 'Volunteer Registration'),
		help_text=span_label('ref_phone_1', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_phone_1')"})
	)

	ref_relationship_1 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_relationship_1', 'Volunteer Registration'),
		help_text=span_label('ref_relationship_1', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_relationship_1')"})
	)

	ref_name_2 = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('ref_name_2', 'Volunteer Registration'),
		help_text=span_label('ref_name_2', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_name_2')"})
	)

	ref_email_2 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_email_2', 'Volunteer Registration'),
		help_text=span_label('ref_email_2', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_email_2')"})
	)

	ref_phone_2 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_phone_2', 'Volunteer Registration'),
		help_text=span_label('ref_phone_2', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_phone_2')"})
	)

	ref_relationship_2 = forms.CharField(
		max_length=80,
		required=False,
		label=eng_label('ref_relationship_2', 'Volunteer Registration'),
		help_text=span_label('ref_relationship_2', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('ref_relationship_2')"})
	)

	# contact_references = forms.CharField(
	# 	label=eng_label('contact_references', 'Volunteer Registration'),
	# 	help_text=span_label('contact_references', 'Volunteer Registration'),
	# 	required=False,
	# 	widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
	# 	attrs={'class': "registration_radio",
	# 		'onclick': "clear_input_errors('contact_references')"})
	# )

	agree_requirements_initials = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('agree_requirements_initials', 'Volunteer Registration'),
		help_text=span_label('agree_requirements_initials', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('agree_requirements_initials')"})
	)

	statements_true_initials = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('statements_true_initials', 'Volunteer Registration'),
		help_text=span_label('statements_true_initials', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('statements_true_initials')"})
	)  

	remove_volunteers_initials = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('remove_volunteers_initials', 'Volunteer Registration'),
		help_text=span_label('remove_volunteers_initials', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified_flex',
								'onclick': "clear_input_errors('remove_volunteers_initials')"})
	)

	other_reasons=forms.ModelMultipleChoiceField(
		label=eng_label('other_reasons', 'Volunteer Registration'),
		help_text=span_label('other_reasons', 'Volunteer Registration'),
		required=False,
		queryset=volunteer_other_reasons(),
		widget=forms.CheckboxSelectMultiple(
									choices=volunteer_other_reasons(),
									attrs={'class': "registration_radio",
									'onclick': "clear_input_errors('other_reasons')"})
	)

	reason_not_listed = forms.CharField(
		max_length=1000,
		required=False,
		label="",
		# label=eng_label('reason_not_listed', 'Volunteer Registration'),
		# help_text=span_label('reason_not_listed', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('reason_not_listed')",
								'rows': 1})
	)

	profile_image = forms.ImageField(
		required=False,
		label=eng_label('profile_image', 'Volunteer Registration'),
		help_text=span_label('profile_image', 'Volunteer Registration'),
		widget=forms.ClearableFileInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('profile_image')",
								'onchange':"readURL(this)"}))

	county = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('county', 'Volunteer Registration'),
		help_text=span_label('county', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('county')"})
	)

	sponsor_child = forms.CharField(
		label=eng_label('sponsor_child', 'Volunteer Registration'),
		help_text=span_label('sponsor_child', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('sponsor_child')"})
	)

	convicted=forms.CharField(
		label=eng_label('convicted', 'Volunteer Registration'),
		help_text=span_label('convicted', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('convicted')"})
	)

	convicted_text = forms.CharField(
		max_length=2000,
		required=False,
		label=eng_label('convicted_text', 'Volunteer Registration'),
		# help_text=span_label('reason_not_listed', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('convicted_text')",
								'rows': 2})
	)

	charges_pending=forms.CharField(
		label=eng_label('charges_pending', 'Volunteer Registration'),
		help_text=span_label('charges_pending', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('charges_pending')"})
	)

	charges_pending_text = forms.CharField(
		max_length=2000,
		required=False,
		label=eng_label('charges_pending_text', 'Volunteer Registration'),
		# help_text=span_label('reason_not_listed', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('charges_pending_text')",
								'rows': 2})
	)

	refused_participation=forms.CharField(
		label=eng_label('refused_participation', 'Volunteer Registration'),
		help_text=span_label('refused_participation', 'Volunteer Registration'),
		required=False,
		widget=forms.RadioSelect(choices=yes_no_choices_eng_only(),
		attrs={'class': "registration_radio",
			'onclick': "clear_input_errors('refused_participation')"})
	)

	refused_participation_text = forms.CharField(
		max_length=2000,
		required=False,
		label=eng_label('refused_participation_text', 'Volunteer Registration'),
		# help_text=span_label('reason_not_listed', 'Volunteer Registration'),
		widget=forms.Textarea(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('refused_participation_text')",
								'rows': 2})
	)

	full_name_signature = forms.CharField(
		max_length=255,
		required=False,
		label=eng_label('full_name_signature', 'Volunteer Registration'),
		help_text=span_label('full_name_signature', 'Volunteer Registration'),
		widget=forms.TextInput(attrs={'class': 'form_control_modified',
								'onclick': "clear_input_errors('full_name_signature')"})
	)


	

	class Meta:
		model = Volunteer_Registration
		fields = ('program_semester', 'volunteer_type', 
			'opportunity_source', 'social_media_source', 'person_referral', 'web_source',
			'teamleader_name','returning_referred', 'previously_paired', 'student_name', 

			'first_name', 'last_name',
			'email', 'phone',
			'dob',
			'country', 'address', 'city', 'state', 'zip_code', 'county',
			'gender',
			 'ethnicity',
			 'in_school', 'current_education_level',
			'current_education_class', 'current_school', 'highest_education_level',
			
			'meeting_times', 'session_choices', 'fluent_spanish',
			'computer', 'device_type', 'children_experience', 'reason',
			'other_reasons', 'reason_not_listed', 'volunteer_other_areas',
			'additional_interests',
			'ref_name_1', 'ref_email_1', 'ref_phone_1', 'ref_relationship_1',
			'ref_name_2', 'ref_email_2', 'ref_phone_2', 'ref_relationship_2',
			# 'contact_references', 
			'sponsor_child',
			'profile_image',
			'parent_name','parent_email', 
			'convicted', 'convicted_text',
			'charges_pending', 'charges_pending_text',
			'refused_participation', 'refused_participation_text',
			'agree_requirements_initials',
			'statements_true_initials',
			'remove_volunteers_initials',

			'full_name_signature',

			
		)

	def clean_refused_participation(self):
		data = self.cleaned_data['refused_participation']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_charges_pending(self):
		data = self.cleaned_data['charges_pending']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_convicted(self):
		data = self.cleaned_data['convicted']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_program_semester(self):
		data = self.cleaned_data['program_semester']
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_volunteer_type(self):
		data = self.cleaned_data['volunteer_type']
		# print("clean volunteer_type", data)
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_first_name(self):
		data = self.cleaned_data['first_name']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_last_name(self):
		data = self.cleaned_data['last_name']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_email(self):
		data = self.cleaned_data['email']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		else:
			invalid_email = False
			try:
				invalid_email = validate_email(data)

			except Exception as e:
				print("invalid_email EMAIL", invalid_email)
				raise ValidationError([
					ValidationError(_('Please enter a valid email'), code='error1'),
					# ValidationError(_('Por favor introduzca una dirección de correo electrónico válida'), code='error2'),
				])

			print("invalid_email EMAIL", invalid_email)

			if not invalid_email:
				if Volunteer_Registration.objects.filter(email = data).exists():
					raise ValidationError([
						ValidationError(_('The email is already in our system. The application cannot be submitted'), code='error1'),
						# ValidationError(_('Por favor introduzca una dirección de correo electrónico válida'), code='error2'),
					])
			
		return data

	def clean_phone(self):
		data = self.cleaned_data['phone']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_dob(self):
		data = self.cleaned_data['dob']
		# print("DOB", data)
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_gender(self):
		# print("Cleaning GENDER")
		data = self.cleaned_data['gender']

		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ethnicity(self):
		data = self.cleaned_data['ethnicity']
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_in_school(self):
		data = self.cleaned_data['in_school']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_meeting_times(self):
		data = self.cleaned_data['meeting_times']
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		
		return data

	def clean_session_choices(self):
		data = self.cleaned_data['session_choices']
		# print("Session Choices", data)
		if data.count() == 0:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		
		return data

	def clean_fluent_spanish(self):
		data = self.cleaned_data['fluent_spanish']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_computer(self):
		data = self.cleaned_data['computer']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_children_experience(self):
		data = self.cleaned_data['children_experience']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_reason(self):
		data = self.cleaned_data['reason']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_volunteer_other_areas(self):
		data = self.cleaned_data['volunteer_other_areas']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_name_1(self):
		data = self.cleaned_data['ref_name_1']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_name_2(self):
		data = self.cleaned_data['ref_name_2']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_email_1(self):
		data = self.cleaned_data['ref_email_1']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_email_2(self):
		data = self.cleaned_data['ref_email_2']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_phone_1(self):
		data = self.cleaned_data['ref_phone_1']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_phone_2(self):
		data = self.cleaned_data['ref_phone_2']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_relationship_1(self):
		data = self.cleaned_data['ref_relationship_1']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_ref_relationship_2(self):
		data = self.cleaned_data['ref_relationship_2']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	# def clean_contact_references(self):
	# 	data = self.cleaned_data['contact_references']
	# 	if data == '':
	# 		raise ValidationError([
	# 			ValidationError(_('This field is required'), code='error1'),
	# 			# ValidationError(_('Este campo es obligatorio'), code='error2'),
	# 		])
	# 	return data

	def clean_agree_requirements_initials(self):
		data = self.cleaned_data['agree_requirements_initials']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_statements_true_initials(self):
		data = self.cleaned_data['statements_true_initials']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_remove_volunteers_initials(self):
		data = self.cleaned_data['remove_volunteers_initials']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_profile_image(self):
		data = self.cleaned_data['profile_image']
		if not data:
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_sponsor_child(self):
		data = self.cleaned_data['sponsor_child']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_full_name_signature(self):
		data = self.cleaned_data['full_name_signature']
		if data == '':
			raise ValidationError([
				ValidationError(_('This field is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

		

	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()
		program_semester = cleaned_data.get("program_semester")
		in_school = cleaned_data.get("in_school")
		volunteer_type = cleaned_data.get("volunteer_type")
		computer = cleaned_data.get("computer")
		volunteer_other_areas = cleaned_data.get("volunteer_other_areas")
		profile_image = cleaned_data.get("profile_image")
		country = cleaned_data.get('country')
		address = cleaned_data.get('address')
		city = cleaned_data.get('city')
		state = cleaned_data.get('state')
		zip_code = cleaned_data.get('zip_code')
		county = cleaned_data.get('county')
		convicted = cleaned_data.get('convicted')
		charges_pending = cleaned_data.get('charges_pending')
		refused_participation = cleaned_data.get('refused_participation')

		if convicted:
			if convicted == "Yes":
				convicted_text = cleaned_data.get('convicted_text')
				if convicted_text == "":
					self.add_error('convicted_text', ValidationError(_('This field is required'), code='required'))
				
		if charges_pending:
			if charges_pending == "Yes":
				charges_pending_text = cleaned_data.get('charges_pending_text')
				if charges_pending_text == "":
					self.add_error('charges_pending_text', ValidationError(_('This field is required'), code='required'))
				

		if refused_participation:
			if refused_participation == "Yes":
				refused_participation_text = cleaned_data.get('refused_participation_text')
				if refused_participation_text == "":
					self.add_error('refused_participation_text', ValidationError(_('This field is required'), code='required'))
				



		if country:
			print("COUNTRY", country)
			if country == "US":
				if address == "":
					self.add_error('address', ValidationError(_('This field is required'), code='required'))
				if city == "":
					self.add_error('city', ValidationError(_('This field is required'), code='required'))
				if not state:
					self.add_error('state', ValidationError(_('This field is required'), code='required'))
				
				if zip_code == "":
					self.add_error('zip_code', ValidationError(_('This field is required'), code='required'))
				else:
					valid = validate_zip_code(zip_code)
					if not valid:
						self.add_error('zip_code', ValidationError(_("Please enter a valid zip code (55555 or 55555-5555)"), code='required'))

				if county == "":
					self.add_error('county', ValidationError(_('This field is required'), code='required'))
		else:
			self.add_error('country', ValidationError(_('This field is required'), code='required'))							



		if program_semester:
			dob = cleaned_data.get("dob")
			if program_semester and dob: 
				age2= age_at_start(program_semester, "Volunteer", dob)
				# print("age2", age2)
				# if age2 < 14:
				# 	raise ValidationError({
				# 		'dob': ValidationError(_('Volunteers must be 14 years old at the start of the session.'), code='too_young'),
				# 		# 'pub_date': ValidationError(_('Invalid date.'), code='invalid'),
				# 	})

				if age2 < 18:
					parent_email = cleaned_data.get("parent_email")
					parent_name = cleaned_data.get("parent_name")

					if parent_name == "":
						self.add_error('parent_name', ValidationError(_('This field is required'), code='too_young'))		

					if parent_email == "":	
						self.add_error('parent_email', ValidationError(_('This field is required'), code='too_young'))	
					else:
						try:
							validate_email(parent_email)
						except Exception as e:
							raise ValidationError([
								ValidationError(_('Please enter a valid email'), code='error1'),
								# ValidationError(_('Por favor introduzca una dirección de correo electrónico válida'), code='error2'),
							])
		if in_school:
			# print("In SCHOOL", in_school)
			if in_school == "Yes":
				current_education_level = cleaned_data.get("current_education_level")
				current_education_class = cleaned_data.get("current_education_class")
				current_school = cleaned_data.get("current_school")

				if not current_education_level:
					self.add_error('current_education_level', ValidationError(_('This field is required'), code='too_young'))							

				if not current_education_class:
					self.add_error('current_education_class', ValidationError(_('This field is required'), code='too_young'))							

				if not current_school:
					self.add_error('current_school', ValidationError(_('This field is required'), code='too_young'))							


			elif in_school == "No":
				highest_education_level = cleaned_data.get("highest_education_level")
				if not highest_education_level:
					self.add_error('highest_education_level', ValidationError(_('This field is required'), code='too_young'))							

		if volunteer_type:
			# print("\n\n\n\nReturning Volunteer", volunteer_type)
			if volunteer_type == "Returning":				
				# print("Yes Returning")
				teamleader_name = cleaned_data.get("teamleader_name")
				if teamleader_name == "":
					self.add_error('teamleader_name', ValidationError(_('This field is required'), code='required'))

				previously_paired = cleaned_data.get("previously_paired")
				if previously_paired == "":
					self.add_error('previously_paired', ValidationError(_('This field is required'), code='required'))


				if previously_paired == "Yes":
					student_name = cleaned_data.get("student_name")
					if student_name == '':
						self.add_error('student_name', ValidationError(_('This field is required'), code='required'))
					# else:
						# print("Has student name")
				# elif previously_paired == "No":
				# 	print("Student name not required")

			elif volunteer_type == "New":
				# print("No New")
				opportunity_source = cleaned_data.get("opportunity_source")
				if not opportunity_source:
					self.add_error('opportunity_source', ValidationError(_('This field is required'), code='required'))
				else:
					# print("opportunity_source", opportunity_source.name)
					if opportunity_source.name == "Social Media":
						social_media_source = cleaned_data.get("social_media_source")
						if not social_media_source:
							self.add_error('social_media_source', ValidationError(_('This field is required'), code='required'))
					elif opportunity_source.name == "Person":
						person_referral = cleaned_data.get("person_referral")
						if person_referral =="":
							self.add_error('person_referral', ValidationError(_('This field is required'), code='required'))		

		if computer:
			if computer == "Yes":
				device_type = cleaned_data.get("device_type")
				if not device_type:
					self.add_error('device_type', ValidationError(_('This field is required'), code='required'))

		if volunteer_other_areas:
			if volunteer_other_areas == "Yes":
				additional_interests = cleaned_data.get("additional_interests")
				if additional_interests.count() == 0:
					self.add_error('additional_interests', ValidationError(_('Please choose at least one, or choose No for the above question.'), code='required'))



