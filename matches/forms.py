from django import forms
from matches.models import Temporary_Match, Match_Note
from matches.models import Scheduled_Match
from matches.models import Match_Type
from buddy_program_data.models import Program_Semester, Session_Meeting_Option
from matches.models import Reader_Match_Profile, Student_Match_Profile

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, Role

def open_slot_readers_users():
	semester = Program_Semester.objects.get(active_semester = True)
	qs = Reader_Match_Profile.objects.filter(semester=semester, open_slot_count__gt=0).order_by('user__username')
	return qs

def students_without_match():
	semester = Program_Semester.objects.get(active_semester = True)
	qs = Student_Match_Profile.objects.filter(semester=semester,
											match_needed=True).order_by('user__username')
	return qs

class Create_Scheduled_Match_Form(forms.ModelForm):
	day_times = forms.ModelChoiceField(
		label="Day Times",
		required=False,
		queryset=Session_Meeting_Option.objects.filter(active=True),
		widget=forms.RadioSelect(choices=Session_Meeting_Option.objects.filter(active=True),
		attrs={'class': "registration_radio"})
	)

	student = forms.ModelChoiceField(
		label="Student",
		required=False,
		queryset=students_without_match(),
		widget=forms.RadioSelect(choices=students_without_match(),
		attrs={'class': "registration_radio"})
	)

	reader = forms.ModelChoiceField(
		label="Reader",
		required=False,
		queryset=open_slot_readers_users(),
		widget=forms.RadioSelect(choices=open_slot_readers_users(),
		attrs={'class': "registration_radio"})
	)


	class Meta:
		model = Scheduled_Match
		fields = (
				'semester',
				'match_type',
				'active',
				'sessions_scheduled',
				'student',
				'reader',				
				'day_times',
				
				)

	def clean_semester(self):
		data = self.cleaned_data['semester']
		if not data:
			raise ValidationError([
				ValidationError(_('Semester is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_active(self):
		data = self.cleaned_data['active']
		if not data:
			raise ValidationError([
				ValidationError(_('Active is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_student(self):
		data = self.cleaned_data['student']
		if not data:
			raise ValidationError([
				ValidationError(_('A Student is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		else:
			data = data.user		
		return data

	def clean_reader(self):
		data = self.cleaned_data['reader']
		if not data:
			raise ValidationError([
				ValidationError(_('A Reader is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		else:
			data = data.user
		return data

	def clean_day_times(self):
		data = self.cleaned_data['day_times']
		if not data:
			raise ValidationError([
				ValidationError(_('A Meeting Time is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean(self):
		print("\n\n\nEnd Cleaning")
		cleaned_data = super().clean()
		day_times = cleaned_data.get("day_times")
		reader = cleaned_data.get("reader")
		print("Cleaned Data", cleaned_data)
		if reader:
			reader_available_slots = reader.reader_match_profile.open_slots

			reader_taken = False
			# print("day_times", day_times)
			if day_times:
				for slot in day_times.session_day_times.all():
					# print(slot)
					if slot not in reader_available_slots.all():
						reader_taken = True

			if reader_taken:
				self.add_error('day_times', ValidationError(_('Reader is Not Available for this Meeting Choice'), code='required'))
				

			print("Reader Taken", reader_taken)




class Edit_Scheduled_Match_Form(forms.ModelForm):
	# student = forms.ModelChoiceField(
	# 	label="Student",
	# 	required=False,
	# 	queryset=students_without_match(),
	# 	widget=forms.RadioSelect(choices=students_without_match(),
	# 	attrs={'class': "registration_radio"})
	# )

	# reader = forms.ModelChoiceField(
	# 	label="Reader",
	# 	required=False,
	# 	queryset=open_slot_readers_users(),
	# 	widget=forms.RadioSelect(choices=open_slot_readers_users(),
	# 	attrs={'class': "registration_radio"})
	# )

	day_times = forms.ModelChoiceField(
		label="Day Times",
		required=False,
		queryset=Session_Meeting_Option.objects.filter(active=True),
		widget=forms.RadioSelect(choices=Session_Meeting_Option.objects.filter(active=True),
		attrs={'class': "registration_radio"})
	)

	new_day_times = forms.ModelChoiceField(
		label="New Day Times",
		required=False,
		queryset=Session_Meeting_Option.objects.filter(active=True),
		widget=forms.RadioSelect(choices=Session_Meeting_Option.objects.filter(active=True),
		attrs={'class': "registration_radio"})
	)

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance', None)

		super(Edit_Scheduled_Match_Form, self).__init__(*args, **kwargs)

		if instance:
			self.initial['semester'] = instance.semester
			self.initial['match_type'] = instance.match_type
			self.initial['student'] = instance.student
			self.initial['reader'] = instance.reader
			self.initial['day_times'] = instance.day_times

	class Meta:
		model = Scheduled_Match
		fields = (
				'semester',
				'match_type',
				'active',
				'sessions_scheduled',
				'student',
				'reader',				
				'day_times',
				'new_day_times',
				
				)

	# def clean_new_day_times(self):
	# 	data = self.cleaned_data['new_day_times']
	# 	if not data:
	# 		raise ValidationError([
	# 			ValidationError(_('A New Meeting Time is Required'), code='error1'),
	# 			# ValidationError(_('Este campo es obligatorio'), code='error2'),
	# 		])
	# 	return data

	def clean_semester(self):
		data = self.cleaned_data['semester']
		if not data:
			raise ValidationError([
				ValidationError(_('Semester is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_active(self):
		data = self.cleaned_data['active']
		if not data:
			raise ValidationError([
				ValidationError(_('Active is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean_student(self):
		data = self.cleaned_data['student']
		print("Clean Student", data)
		if not data:
			raise ValidationError([
				ValidationError(_('A Student is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])		
		return data

	def clean_reader(self):
		data = self.cleaned_data['reader']
		print("Clean Reader", data)
		if not data:
			raise ValidationError([
				ValidationError(_('A Reader is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		
		return data

	def clean_day_times(self):
		data = self.cleaned_data['day_times']
		if not data:
			raise ValidationError([
				ValidationError(_('A Meeting Time is required'), code='error1'),
				# ValidationError(_('Este campo es obligatorio'), code='error2'),
			])
		return data

	def clean(self):
		print("\nEnd Cleaning")
		cleaned_data = super().clean()
		day_times = cleaned_data.get("day_times")
		new_day_times = cleaned_data.get("new_day_times")
		reader = cleaned_data.get("reader")
		print("new_day_times", new_day_times)
		if not new_day_times:
			cleaned_data['day_times'] = day_times
			self.add_error('new_day_times', ValidationError(_('A New Meeting Time is Required'), code='required'))


		if reader:
			reader_available_slots = reader.reader_match_profile.open_slots
			reader_scheduled_slots = reader.reader_match_profile.scheduled_slots
			current_match_slots = day_times.session_day_times.all()

			slots_with_this_match_slots_removed = []
			new_taken = False
			if new_day_times:				
				for slot in new_day_times.session_day_times.all():
					if slot not in reader_available_slots.all():
						if slot not in current_match_slots:
							print("In a different Match")
							new_taken = True
			# else:
			# 	cleaned_data['day_times'] = new_day_times


			if new_taken:
				self.add_error('new_day_times', ValidationError(_('Reader is Not Available for this Meeting Choice'), code='required'))
			else:
				cleaned_data['day_times'] = new_day_times

			print("\n\n\nNew Reader Taken", new_taken)



class Create_Temporary_Match_Form(forms.ModelForm):
	class Meta:
		model = Temporary_Match
		fields = ('__all__')

class Edit_Temporary_Match_Form(forms.ModelForm):
	class Meta:
		model = Temporary_Match
		fields = ('__all__')