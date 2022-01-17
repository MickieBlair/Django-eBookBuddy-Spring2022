from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.apps import apps
from users.models import CustomUser
from buddy_program_data.models import Reading_Session_Day_Time, Program_Semester
from buddy_program_data.models import Session_Meeting_Option, Daily_Session



class Student_Match_Profile(models.Model):
	semester = models.ForeignKey(Program_Semester, related_name="student_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	user = models.OneToOneField(CustomUser, related_name="student_match_profile",
									on_delete=models.CASCADE)
	match_needed = models.BooleanField(default=True)
	buddy = models.ForeignKey(CustomUser, related_name="stu_reader",
								 on_delete=models.CASCADE, null=True, blank=True)
	scheduled_slots = models.ManyToManyField(Reading_Session_Day_Time,
											 related_name="student_scheduled", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user__username']
		verbose_name = 'Student Match Profile'
		verbose_name_plural = 'Student Match Profiles'

	def __str__(self):
		return "Student: " + self.user.username


class Reader_Match_Profile(models.Model):
	semester = models.ForeignKey(Program_Semester, related_name="reader_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	user = models.OneToOneField(CustomUser, related_name="reader_match_profile",
									on_delete=models.CASCADE)
	match_count = models.IntegerField(default=0)
	buddies = models.ManyToManyField(CustomUser, related_name="reader_stu",
								  blank=True)
	open_slots = models.ManyToManyField(Reading_Session_Day_Time,
											 related_name="open", blank=True,)
	scheduled_slots = models.ManyToManyField(Reading_Session_Day_Time,
											 related_name="scheduled", blank=True,)
	open_slot_count = models.IntegerField(default=0, verbose_name="Open Count")
	scheduled_slot_count = models.IntegerField(default=0, verbose_name="Scheduled Count")

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def get_buddies_string(self):
		if self.buddies.all().count() > 0:
			return ", ".join([
				user.username for user in self.buddies.all()
				])
		else:
			return "None"

	def add_open_slots(self, slots):
		for slot in slots:
			self.open_slots.add(slot)

		self.open_slot_count = self.open_slots.count()
		self.save()

	def calculate_stats(self):
		self.open_slot_count = self.open_slots.count()
		self.scheduled_slot_count = self.scheduled_slots.count()		
		self.save()


	class Meta:
		ordering = ['user__username']
		verbose_name = 'Reader Match Profile'
		verbose_name_plural = 'Reader Match Profiles'

	def __str__(self):
		return "Reader: " + self.user.username

class Match_Type(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=255, unique=True)
	class Meta:
		verbose_name = 'Match Type'
		verbose_name_plural = 'Match Types'

	def __str__(self):
		return self.name


class Match_Note(models.Model):	
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
								related_name='note_type', null=True, blank=True,)
	name = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(max_length=2000, null=True, blank=True)
	created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='created_match_notes', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Match Note'
		verbose_name_plural = 'Match Notes'

	def __str__(self):
		return str(self.name)		

class Scheduled_Match(models.Model):
	semester = models.ForeignKey(Program_Semester, related_name="match_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
								related_name='type', null=True, blank=True,)
	student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='match_student', null=False, blank=False,)

	reader = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='match_reader', null=False, blank=False,)
	day_times = models.ForeignKey(Session_Meeting_Option, on_delete=models.CASCADE,
								related_name='scheduled_times', null=False, blank=False,)
	sessions_scheduled = models.ManyToManyField(Daily_Session,
									 related_name="scheduled_matches_in_session",
									 blank=True,)	
	active = models.BooleanField(default=True)
	notes = models.ManyToManyField(Match_Note,
									 related_name="sch_match_notes",
									 blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def remaining_sessions(self):
		time_now = timezone.localtime(timezone.now())
		qs = self.sessions_scheduled.filter(session_start_date_time__gte=time_now)
		return qs

	def successful(self):
		return 0

	def incomplete(self):
		return 0

	def add_note_temporary_match_created(self, created_by, temp_match):
		note_content = "Student: " + temp_match.student.full_name() + " - Reader: " + temp_match.reader.full_name()
		note = Match_Note.objects.create(match_type=self.match_type,
										name="Temporary Match Created",
										content=note_content,
										created_user = created_by
										)
		self.notes.add(note)

	def post_edit_match(self, original_day_times):
		print("\n\n\n\nPOST EDIT CREATE MATCH")

		old_choosen_session = original_day_times
		for old_option in old_choosen_session.session_day_times.all():
			the_old_sessions = old_option.session_day_time.all()
			for old_session in the_old_sessions:
				if old_session.session_start_date_time > timezone.localtime(timezone.now()):
					attendance, created = Match_Attendance_Record.objects.get_or_create(
												session=old_session,
												match_type=self.match_type,
												sch_match = self,
												)
					attendance.delete()
					match_session_status = self.sch_match_status.filter(session=old_session)
					match_session_status.delete()
					self.sessions_scheduled.remove(old_session)
					
		


		#reader
		reader_profile = Reader_Match_Profile.objects.get(semester=self.semester,
															user=self.reader)


		reader_scheduled_matches = Scheduled_Match.objects.filter(
														semester=self.semester,
														active=True,
														reader=self.reader
														)

		reader_profile.match_count = reader_scheduled_matches.count()


		all_slots = Reading_Session_Day_Time.objects.all()

		reader_profile.open_slots.clear()
		reader_profile.scheduled_slots.clear()

		for slot in all_slots:
			reader_profile.open_slots.add(slot)

		for match in reader_scheduled_matches:
			if match == self:
				match_slots = match.day_times
				for slot in match_slots.session_day_times.all():
					reader_profile.open_slots.remove(slot)
					reader_profile.scheduled_slots.add(slot)
					the_sessions = slot.session_day_time.all()
					for session in the_sessions:
						if session.session_start_date_time > timezone.localtime(timezone.now()):
							attendance, created = Match_Attendance_Record.objects.get_or_create(
														session=session,
														match_type=self.match_type,
														sch_match = self,
														)
							self.sessions_scheduled.add(session)							

			else:
				match_slots = match.day_times
				for slot in match_slots.session_day_times.all():
					reader_profile.open_slots.remove(slot)
					reader_profile.scheduled_slots.add(slot)

		reader_profile.calculate_stats() 
		reader_profile.save()

		#student
		student_profile = Student_Match_Profile.objects.get(semester=self.semester,
															user=self.student)
		student_profile.scheduled_slots.clear()

		for slot in match_slots.session_day_times.all():
			student_profile.scheduled_slots.add(slot)



		

	def set_match_inactive(self):

		self.active = False
		self.save()

		choosen_session = self.day_times

		#student
		student_profile = Student_Match_Profile.objects.get(semester=self.semester,
															user=self.student)
		student_profile.match_needed = True
		student_profile.buddy = None
		student_profile.save() 

		for option in choosen_session.session_day_times.all():
				student_profile.scheduled_slots.remove(option)

		student_profile.user.session_status.current_active_match_type = None
		student_profile.user.session_status.active_scheduled_match = None
		student_profile.user.session_status.active_buddy = None
		student_profile.user.session_status.scheduled_matches.clear()
		student_profile.user.session_status.save()

		#reader
		reader_profile = Reader_Match_Profile.objects.get(semester=self.semester,
															user=self.reader)
		reader_profile.buddies.remove(self.student)

		match_count_reader = Scheduled_Match.objects.filter(
												semester=self.semester,
												active=True,
												reader=self.reader
												).count()

		reader_profile.match_count = match_count_reader

		
		for option in choosen_session.session_day_times.all():
				reader_profile.scheduled_slots.remove(option)
				reader_profile.open_slots.add(option)
				the_sessions = option.session_day_time.all()				
				
				for session in the_sessions:
					# print(session)
					if session.session_start_date_time > timezone.localtime(timezone.now()):

						attendance = Match_Attendance_Record.objects.get(
												session=session,
												match_type=self.match_type,
												sch_match = self,
												)
						attendance.delete()

						match_session_status = self.sch_match_status.filter(session=session)
						match_session_status.delete()
						# self.sch_match_status.filter(sch_match=self, session=session).delete()		

						self.sessions_scheduled.remove(session)
					# else:
					# 	print("session already happened")

		reader_profile.calculate_stats()		
		reader_profile.save()

		if match_count_reader == 0:
			reader_profile.user.session_status.current_active_match_type = None
			reader_profile.user.session_status.scheduled_matches.clear()
			reader_profile.user.session_status.buddies.clear()
			reader_profile.user.session_status.save()
		else:
			reader_profile.user.session_status.scheduled_matches.remove(self)
			reader_profile.user.session_status.buddies.remove(self.student)
			reader_profile.user.session_status.save()

		# self.sch_match_status.filter(sch_match=self).delete()	
		

	def post_create_match(self):
		choosen_session = self.day_times
		#student
		student_profile = Student_Match_Profile.objects.get(semester=self.semester,
															user=self.student)
		student_profile.match_needed = False
		student_profile.buddy = self.reader
		student_profile.save() 
		for option in choosen_session.session_day_times.all():
				student_profile.scheduled_slots.add(option)

		student_profile.user.session_status.current_active_match_type = self.match_type
		student_profile.user.session_status.active_scheduled_match = self
		student_profile.user.session_status.active_buddy = self.reader
		student_profile.user.session_status.scheduled_matches.clear()
		student_profile.user.session_status.scheduled_matches.add(self)
		student_profile.user.session_status.save()

		#reader
		reader_profile = Reader_Match_Profile.objects.get(semester=self.semester,
															user=self.reader)
		reader_profile.buddies.add(self.student)

		reader_profile.match_count = Scheduled_Match.objects.filter(
														semester=self.semester,
														active=True,
														reader=self.reader
														).count()

		
		for option in choosen_session.session_day_times.all():
				reader_profile.scheduled_slots.add(option)
				reader_profile.open_slots.remove(option)
				the_sessions = option.session_day_time.all()
				match_status = Match_Status_Option.objects.get(name="Both Missing")
				
				for session in the_sessions:
					# print(session)
					if session.session_start_date_time > timezone.localtime(timezone.now()):
						attendance, created = Match_Attendance_Record.objects.get_or_create(
													session=session,
													match_type=self.match_type,
													sch_match = self,
													status=match_status,
													)						
						self.sessions_scheduled.add(session)
					# else:
					# 	print("session in the past")

		reader_profile.calculate_stats() 
		# profile.match_count =  profile.user.match_reader.count()
		reader_profile.save()

		reader_profile.user.session_status.current_active_match_type = self.match_type
		reader_profile.user.session_status.scheduled_matches.add(self)
		reader_profile.user.session_status.buddies.add(self.student)
		reader_profile.user.session_status.save()
		
		
	def status(self):
		if self.active:
			return "Active"
		else:
			return "Inactive"

	class Meta:
		ordering = ['id']
		verbose_name = 'Scheduled Match'
		verbose_name_plural = 'Scheduled Matches'

	def __str__(self):
		string_for_return = ""
		
		text = ""
		if self.active:
			text = "Active"
		else:
			text = "Inactive"
		string_for_return = string_for_return + text + ":  "
		if self.student:
			string_for_return =string_for_return + "S-" + self.student.username
		else:
			string_for_return = string_for_return + "No Student"

		if self.reader:
			string_for_return = string_for_return + " / R-" + self.reader.username
		else:
			string_for_return = string_for_return + " - No Reader"
		return string_for_return

@receiver(pre_delete, sender=Scheduled_Match)
def sch_match_pre_delete(sender, instance, **kwargs):
	student = instance.student
	reader = instance.reader
	the_slots = instance.day_times
	if student:
		student.student_match_profile.match_needed = True
		student.student_match_profile.buddy = None
		student.student_match_profile.save()
		student.session_status.current_active_match_type = None
		student.session_status.active_scheduled_match = None
		student.session_status.active_buddy = None
		student.session_status.scheduled_matches.clear()
		student.session_status.save()
		for option in the_slots.session_day_times.all():
			student.student_match_profile.scheduled_slots.remove(option)


	if instance.reader:
		reader.session_status.scheduled_matches.remove(instance)
		reader.session_status.buddies.remove(student)
		reader.session_status.save()

		reader.reader_match_profile.buddies.remove(student)

		

		for option in the_slots.session_day_times.all():
			reader.reader_match_profile.scheduled_slots.remove(option)
			reader.reader_match_profile.open_slots.add(option)

	for note in instance.notes.all():
		note.delete()

@receiver(post_delete, sender=Scheduled_Match)
def sch_match_post_delete(sender, instance, **kwargs):
	reader = instance.reader
	if instance.reader:
		reader.reader_match_profile.open_slot_count = reader.reader_match_profile.open_slots.count()
		reader.reader_match_profile.scheduled_slot_count = reader.reader_match_profile.scheduled_slots.count()	
		reader.reader_match_profile.match_count = reader.match_reader.count()
		reader.reader_match_profile.save()

		if reader.reader_match_profile.match_count == 0:
			reader.session_status.current_active_match_type = None
			reader.session_status.scheduled_matches.clear()
			reader.session_status.buddies.clear()
			reader.session_status.save()





class Temporary_Match(models.Model):
	semester = models.ForeignKey(Program_Semester, related_name="temp_semester",
								 on_delete=models.CASCADE, null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
								related_name='temp_type', null=True, blank=True,)
	student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='temp_match_student', null=False, blank=False,)

	reader = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='temp_match_reader', null=False, blank=False,)
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
								related_name='temp_session', null=False, blank=False,)
	active = models.BooleanField(default=True)
	notes = models.ManyToManyField(Match_Note,
									 related_name="temp_match_notes",
									 blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def create_temporary_match(content):
		Match_Session_Status = apps.get_model(app_label='reading_sessions', model_name='Match_Session_Status')
		Redirect = apps.get_model(app_label='reading_sessions', model_name='Redirect')

		temp_match = None
		redirect = None

		print("*******In MODEL Creating a temporary Match", content)
		semester = Program_Semester.objects.get(active_semester = True)
		match_type = Match_Type.objects.get(name="Temporary - In Session")
		student = CustomUser.objects.get(id=content['student_id'])
		reader = CustomUser.objects.get(id=content['reader_id'])
		session = Daily_Session.objects.get(id=content['session_id'])
		sent_by = CustomUser.objects.get(id=content['sent_by'])
		student_previous_temps =Temporary_Match.objects.filter(session=session, student=student)
		for item in student_previous_temps:
			item.active = False
			item.save()
			old_temp_note_stu = Match_Note.objects.create(
													match_type=match_type,
													name="Temporary Match Inactive",
													content="Student Has New Temp Match",
													created_user = sent_by)
			item.notes.add(old_temp_note_stu)

		reader_previous_temps = Temporary_Match.objects.filter(session=session, reader=reader)
		for item in reader_previous_temps:
			item.active = False
			item.save()
			old_temp_note_reader = Match_Note.objects.create(
													match_type=match_type,
													name="Temporary Match Inactive",
													content="Reader Has New Temp Match",
													created_user = sent_by)
			item.notes.add(old_temp_note_reader)

		temp_match = Temporary_Match.objects.create(
						semester = semester,
						match_type = match_type,
						student = student,
						reader=reader,
						session=session,
						active=True,
					)
		temp_note_note = Match_Note.objects.create(
										match_type=match_type,
										name="Temporary Match Created",
										created_user = sent_by)

		temp_match.notes.add(temp_note_note)

		temp_match_session_status, created  = Match_Session_Status.objects.get_or_create(session=session,
																			match_type=match_type,
																			temp_match= temp_match)

		temp_match_attendance, created  = Match_Attendance_Record.objects.get_or_create(session=session,
																			match_type=match_type,
																			temp_match= temp_match)


		# Student Stuff
		#adjust session status for student in temp match
		student.session_status.needs_new_buddy = False
		student.session_status.needs_session_match = False
		student.session_status.current_active_match_type = match_type
		student.session_status.temp_match = temp_match
		student.session_status.save()

		#Reader Stuff
		#adjust session status for reader in temp match
		reader.session_status.needs_new_buddy = False
		reader.session_status.needs_session_match = False
		reader.session_status.current_active_match_type = match_type
		reader.session_status.temp_match = temp_match
		reader.session_status.save()

		if Scheduled_Match.objects.filter(student=student, active=True).exists():
			student_scheduled_match = Scheduled_Match.objects.get(student=student, active=True)
			student_scheduled_match.add_note_temporary_match_created(sent_by, temp_match)
			
			#adjust Match Session Status for prior match
			old_stu_match_session_status, created = Match_Session_Status.objects.get_or_create(
																				session=session,
																				sch_match=student_scheduled_match,
																				)
			
			old_stu_match_session_status.student_reassigned=True
			old_stu_match_session_status.member_reassigned=True
			old_stu_match_session_status.display_student_location=False
			old_stu_match_session_status.save()

			student_scheduled_match_reader = student_scheduled_match.reader
			student_scheduled_match_reader.session_status.needs_new_buddy = True
			student_scheduled_match_reader.session_status.save()

		if Scheduled_Match.objects.filter(reader=reader, sessions_scheduled__in=[session, ],
														active=True).exists():
			print("reader_scheduled_match Exists")
			reader_scheduled_match = Scheduled_Match.objects.get(reader=reader,sessions_scheduled__in=[session,],
																	 active=True)
			print("reader_scheduled_match", reader_scheduled_match)
			reader_scheduled_match.add_note_temporary_match_created(sent_by, temp_match)
			old_reader_match_session_status, created = Match_Session_Status.objects.get_or_create(
																				session=session,
																				sch_match=reader_scheduled_match,
																				)
			old_reader_match_session_status.reader_reassigned=True
			old_reader_match_session_status.member_reassigned=True
			old_reader_match_session_status.display_reader_location=False
			old_reader_match_session_status.save()
			print("old_reader_match_session_status", old_reader_match_session_status.id)
			reader_scheduled_match_student = reader_scheduled_match.student
			reader_scheduled_match_student.session_status.needs_new_buddy = True
			reader_scheduled_match_student.session_status.save()
			


		redirect, created = Redirect.objects.get_or_create(
									user_to_redirect = student,
									)
		redirect.to_user = reader
		redirect.auto_send= True
		redirect.to_room=reader.session_status.room
		redirect.save()


		return temp_match, redirect


		# adjust students match status, create the match status for the temp match
			# temp_match_status = student_scheduled_match.sch_match_status.student_adjust_for_temp_match_creation(temp_match)
			# print(temp_match_status)
			# adjust student user_session_status
			# adjust the match status for that match
			# mark the match attendance record for that scheduled match for this session



		# if Scheduled_Match.objects.filter(reader=reader, active=True).exists():
		# 	reader_matches = Scheduled_Match.objects.filter(reader=reader, active=True)
		# 	for match in reader_matches:
		# 		if session in match.sessions_scheduled.all():
		# 			match.add_note_temporary_match_created(sent_by, temp_match)
		
		

		# redirect_data = RedirectSerializer(instance=redirect).data
		# temp_match_data = TemporaryMatchSerializer(instance=temp_match).data

		# temp_match.set_student_info()
		# temp_match.set_reader_info()

	def set_student_info(self):
		print("Changing All the Student Stuff")

	def set_reader_info(self):
		print("Changing All the Reader Stuff")

	class Meta:
		ordering = ['id']
		verbose_name = 'Temporary Match'
		verbose_name_plural = 'Temporary Matches'

	def __str__(self):
		string_for_return = ""
		text = ""
		if self.active:
			text = "Active"
		else:
			text = "Inactive"
		string_for_return = string_for_return + text + ":  "
		if self.student:
			string_for_return =string_for_return + "S-" + self.student.username
		else:
			string_for_return = string_for_return + "No Student"

		if self.reader:
			string_for_return = string_for_return + " / R-" + self.reader.username
		else:
			string_for_return = string_for_return + " - No Reader"
		return string_for_return
		


@receiver(pre_delete, sender=Temporary_Match)
def temp_match_pre_delete(sender, instance, **kwargs):
	for note in instance.notes.all():
		note.delete()

class Match_Status_Option(models.Model):
	name = models.CharField(max_length=255, unique=True)
	class Meta:
		verbose_name = 'Match Status Option'
		verbose_name_plural = 'Match Status Option'

	def __str__(self):
		return self.name

class Match_Attendance_Record(models.Model):
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
					related_name='match_attendance_session', null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
					related_name='match_attendance_type', null=True, blank=True)

	sch_match = models.ForeignKey(Scheduled_Match, related_name="sch_match_attendance_record",
							on_delete=models.CASCADE,  null=True, blank=True)

	member_reassigned = models.BooleanField(default=False, verbose_name="M-R")

	temp_match = models.ForeignKey(Temporary_Match, related_name="temp_match_attendance_record",
							on_delete=models.CASCADE,  null=True, blank=True)
	

	student_present = models.BooleanField(default=False, verbose_name="S-Present")
	student_time_in = models.TimeField(null=True, blank=True)
	student_time_out = models.TimeField(null=True, blank=True)
	student_reassigned = models.BooleanField(default=False, verbose_name="S-R")
	student_time_in_pending = models.IntegerField(null=True, blank=True, default=0)
	student_time_in_breakout = models.IntegerField(null=True, blank=True, default=0)

	reader_present = models.BooleanField(default=False, verbose_name="R-Present")
	reader_time_in = models.TimeField(null=True, blank=True)
	reader_time_out = models.TimeField(null=True, blank=True)
	reader_reassigned = models.BooleanField(default=False, verbose_name="R-R")
	reader_in_breakout_alone = models.IntegerField(null=True, blank=True, default=0)
	reader_in_breakout_w_student = models.IntegerField(null=True, blank=True, default=0)

	match_complete_at = models.TimeField(null=True, blank=True)
	match_ended_at = models.TimeField(null=True, blank=True)
	duration = models.DurationField(null=True, blank=True)
	match_successful = models.BooleanField(default=False, verbose_name="Success")

	status = models.ForeignKey(Match_Status_Option, related_name="record_status",
									on_delete=models.CASCADE, null=True, blank = True)

	notes = models.ManyToManyField(Match_Note,related_name="match_attendance_notes", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")


	class Meta:
		ordering = ['session__date', 'session__day_time']
		verbose_name = 'Match Attendance Record'
		verbose_name_plural = 'Match Attendance Records'

	def string_for_return(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name + " - " + str(self.sch_match)		
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.match_type.short_name + " - " + str(self.temp_match)	

	def get_type(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.match_type.short_name + ": "

	def get_student(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.student	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.temp_match.student

	def get_reader(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.reader	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.temp_match.reader
				



	def __str__(self):
		return self.string_for_return()


def pre_save_attendance_receiver(sender, instance, *args, **kwargs):
	# print("Pre Save Match Attendance", instance.student_reassigned, instance.reader_reassigned)
	if instance.student_reassigned and instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Both Reassigned")

	elif instance.student_reassigned and not instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Student Reassigned")

	elif not instance.student_reassigned and instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Reader Reassigned")

	else:
		if not instance.member_reassigned:
			if instance.match_successful:
				instance.status = Match_Status_Option.objects.get(name="Success")
			# elif not instance.student_present and not instance.reader_present::
			# 	instance.status = Match_Status_Option.objects.get(name="Both No Show")
			else:
				instance.status = None



pre_save.connect(pre_save_attendance_receiver, sender=Match_Attendance_Record)

def post_save_duration_receiver(sender, instance, *args, **kwargs):
	pass
	# print("Post Save")
	# if instance.duration == None:
	# instance.calculate_duration()

post_save.connect(post_save_duration_receiver, sender=Match_Attendance_Record)