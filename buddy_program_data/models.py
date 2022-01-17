from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from users.models import Program
from users.models import CustomUser
import datetime
import calendar
from django.apps import apps



    

REQUIRED_CHOICES = [("Yes","Yes"),("No","No"),("Depends","Depends on App Factors")]

def format_time_str(time):
	str_time = time.strftime("%I:%M %p") 
	first = str_time.split(":")[0].replace("0","")
	second = str_time.split(":")[1]
	time_string = first + ":" + second

	return time_string

class School(models.Model):
	name = models.CharField(max_length=150, null=False, blank=False)
	display_in_list = models.BooleanField(default=False)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'School'
		verbose_name_plural = 'School'

	def __str__(self):
		return self.name

class Grade(models.Model):
	eng_name = models.CharField(max_length=150, null=False, blank=False)
	span_name = models.CharField(max_length=150, null=True, blank=True)
	abbr = models.CharField(max_length=3, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Grade'
		verbose_name_plural = 'Grades'

	def __str__(self):
		return self.eng_name

class Language(models.Model):
	eng_name = models.CharField(max_length=150, null=False, blank=False)
	span_name = models.CharField(max_length=150, null=False, blank=False)
	iso = models.CharField(max_length=2, null=True, blank=True)
	active=models.BooleanField(default=True)
	display_form_language = models.BooleanField(default=False)
	display_primary = models.BooleanField(default=False)
	display_secondary = models.BooleanField(default=False)
	order= models.IntegerField(default=0, null=True, blank=True)

	class Meta:
		ordering = ['order']
		verbose_name = 'Language'
		verbose_name_plural = 'Languages'

	def __str__(self):
		return self.eng_name


class Answer_Type(models.Model):
	name = models.CharField(max_length=150, null=False, blank=False)

	class Meta:
		ordering = ['name']
		verbose_name = 'Answer Type'
		verbose_name_plural = 'Answer Types'

	def __str__(self):
		return self.name

class Program_Form(models.Model):
	name = models.CharField(max_length=150, null=False, blank=False)

	class Meta:
		ordering = ['name']
		verbose_name = 'Program Form'
		verbose_name_plural = 'Program Forms'

	def __str__(self):
		return self.name

class Question(models.Model):
	for_form= models.ForeignKey(Program_Form, on_delete=models.CASCADE,
								related_name='form_question', null=True, blank=True,)
	question_number = models.CharField(max_length=10, null=True, blank=True)
	required = models.CharField(max_length=30, choices=REQUIRED_CHOICES, null=True, blank=True)
	eng_text = models.TextField(max_length=1500, null=False, blank=False)
	span_text = models.TextField(max_length=1500, null=True, blank=True)
	field_name = models.CharField(max_length=150, null=False, blank=False)
	answer_type = models.ForeignKey(Answer_Type, on_delete=models.CASCADE,
								related_name='question_type', null=False, blank=False,)
	class Meta:
		ordering = ['for_form__name']
		verbose_name = 'Question'
		verbose_name_plural = 'Questions'


	def __str__(self):
		return self.for_form.name + "-" + self.field_name

class Response_Flag(models.Model):
	on_question = models.ForeignKey(Question, on_delete=models.CASCADE,
								related_name='question_flag', null=True, blank=True,)
	flag_condition = models.CharField(max_length=255, null=True, blank=True)
	action = models.CharField(max_length=255, null=True, blank=True)
	comment = models.TextField(max_length=2000, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Response Flag'
		verbose_name_plural = 'Response Flags'

	def __str__(self):
		return str(self.on_question) + " Flag"



class Program_Status(models.Model):
	program = models.OneToOneField(Program, related_name="program_status", on_delete=models.CASCADE)
	updating = models.BooleanField(default=False)
	# accepting_students = models.BooleanField(default=False)
	# accepting_volunteers = models.BooleanField(default=False)

	class Meta:
		ordering = ['id']
		verbose_name = 'Program Status'
		verbose_name_plural = 'Program Status'

	def __str__(self):
		return self.program.name + " Status"

class Form_Message(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False)	
	for_form= models.ForeignKey(Program_Form, on_delete=models.CASCADE,
								related_name='form_message', null=True, blank=True,)
	active = models.BooleanField(default=True)
	created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='created', null=False, blank=False,)
	message_content = models.TextField(max_length=5000, null=True, blank=True)
	span_content = models.TextField(max_length=5000, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")	
	last_updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='updated', null=True, blank=True,)
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Form Message'
		verbose_name_plural = 'Form Messages'

	def __str__(self):
		return self.name

class Day(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span_name = models.CharField(max_length=100, null=False, blank=True) 
	number = models.IntegerField(null=True, blank=True)
	short_name = models.CharField(max_length=3, null=True, blank=True)
	letter = models.CharField(max_length=3, null=True, blank=True)
	active=models.BooleanField(default=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Day'
		verbose_name_plural = 'Days'

	def __str__(self):
		return self.name

class Reading_Session_Day_Time(models.Model):	
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False)
	time_start = models.TimeField(null=False, blank=False)
	time_end = models.TimeField(null=False, blank=False)
	session_slot = models.CharField(max_length=1, null=False, blank=False)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ['day__number', 'session_slot']
		verbose_name = 'Session Day/Time'
		verbose_name_plural = 'Session Days/Times'

	def get_short_name(self):
		return self.day.short_name + "-" + self.session_slot

	def get_name_start(self):
		str_time = self.time_start.strftime("%I:%M%p")
		return self.day.short_name + "-" + str_time

	def get_times(self):
		string_for_return = ""
		str_time_start = self.time_start.strftime("%I:%M-%p")
		
		split_start = str_time_start.split(':')
		hour= split_start[0].replace("0", '')
		string_for_return = string_for_return + hour
		next_split = split_start[1].split("-")
		if next_split[0] == "00":
			minute=""
			string_for_return = string_for_return + minute
		else:
			minute = next_split[0]
			string_for_return = string_for_return +":" + minute

		string_for_return = string_for_return + next_split[1].lower() + " - "

		str_time_end = self.time_end.strftime("%I:%M-%p")

		split_end = str_time_end.split(':')
		hour= split_end[0].replace("0", '')
		string_for_return = string_for_return + hour
		next_split = split_end[1].split("-")
		if next_split[0] == "00":
			minute=""
			string_for_return = string_for_return + minute
		else:
			minute = next_split[0]
			string_for_return = string_for_return +":" + minute

		string_for_return = string_for_return + next_split[1].lower()




		return string_for_return

	def get_name_time(self):
		str_time = self.time_start.strftime("%I:%M %p")
		return self.day.short_name + "-" + self.session_slot + "-" + str_time

	def get_slot_session_times(self):
		str_time_start = self.time_start.strftime("%I:%M %p")
		str_time_end = self.time_end.strftime("%I:%M %p")
		return self.session_slot + ": " + str_time_start + " - " + str_time_end

	def __str__(self):
		return self.day.name + " - " + self.session_slot


class Program_Semester(models.Model):
	program = models.ForeignKey(Program, related_name="program_semester", on_delete=models.CASCADE)
	name = models.CharField(max_length=150, null=True, blank=True)
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)
	active_semester = models.BooleanField(default=False)
	accepting_students = models.BooleanField(default=False)
	accepting_volunteers = models.BooleanField(default=False)
	days = models.ManyToManyField(Day, related_name="days_in_session", blank=True,)
	day_time_slots = models.ManyToManyField(Reading_Session_Day_Time, related_name="semester_day_time", blank=True,)
	slug = models.SlugField(null=True, blank=True, unique=True, max_length=255,)
	full_dates = models.CharField(max_length=100, null=True, blank=True,)

	class Meta:
		ordering = ['id']
		verbose_name = 'Program Semester'
		verbose_name_plural = 'Program Semesters'

	def slugify_name(self):
		slug = slugify(self.program.name)
		return slug

	def format_start_date(self):
		date_str = self.start_date.strftime("%Y-%m-%d")
		return date_str

	def string_for_return(self):
		if self.start_date:
			date_str = self.start_date.strftime("%m/%d/%Y")
			string_for_return = self.program.name + " - " + self.name + " - Start Date: " + date_str
		else:
			string_for_return = self.program.name + " - " + self.name 
		return string_for_return


	def __str__(self):
		return self.string_for_return()

	def save(self, *args, **kwargs):
		if self.active_semester:
			qs = type(self).objects.filter(active_semester=True, program=self.program)
			if self.pk:
				qs = qs.exclude(pk=self.pk)
			qs.update(active_semester=False)

		super(Program_Semester, self).save(*args, **kwargs)

@receiver(pre_save, sender=Program_Semester)
def auto_populate_full_description(sender, instance=None, created=False, **kwargs):
	start_date = instance.start_date.strftime("%B %d, %Y")
	end_date = instance.end_date.strftime("%B %d, %Y")
	instance.full_dates = start_date + ' - ' + end_date
	instance.slug = slugify(instance.name)

@receiver(post_save, sender=Program_Semester)
def days_with_daily_session(sender, instance=None, created=False, **kwargs):
	start_date =instance.start_date
	end_date = instance.end_date
	delta = datetime.timedelta(days=1)
	week = 1
	
	while start_date <= end_date:	
		start_day = start_date.weekday()
		if start_day == 6:
			week = week + 1

		start_day_of_week = calendar.day_name[start_day]
		day = Day.objects.get(name=start_day_of_week)

		if day in instance.days.all():	
			for slot in instance.day_time_slots.all():
				if slot.day == day:
					daily_session, created = Daily_Session.objects.get_or_create(
						date = start_date,
						semester = instance,
						day_time = slot,
						week = week
						)

		start_date += delta

class Daily_Session(models.Model):
	date = models.DateField(verbose_name="Date", null=True, blank=True)
	semester =  models.ForeignKey(Program_Semester, on_delete=models.CASCADE, related_name='daily_sessions', null=True, blank=True)
	day_time = models.ForeignKey(Reading_Session_Day_Time, related_name="session_day_time",
								 on_delete=models.CASCADE ,null=True, blank=True)
	slug = models.SlugField(blank=True, max_length=255,)
	
	week = models.IntegerField(null=True, blank=True)	
	name = models.CharField(max_length=255, null=True, blank=True)
	archive_session = models.BooleanField(default=False, verbose_name="Archived")
	session_start_date_time = models.DateTimeField(verbose_name="Start Date/Time", blank=True, null=True)
	session_end_date_time = models.DateTimeField(verbose_name="End Date/Time", blank=True, null=True)
	student_entry_allowed_start = models.DateTimeField(verbose_name="Student In", blank=True, null=True)
	student_entry_allowed_end = models.DateTimeField(verbose_name="Student End", blank=True, null=True)	
	session_complete = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def active_scheduled_matches_in_session(self):
		matches = self.scheduled_matches_in_session.filter(active=True)
		return matches

	def active_temporary_matches_in_session(self):
		matches = self.temp_session.filter(active=True)
		return matches

	class Meta:
		ordering = ['date', 'day_time']
		verbose_name = 'Session'
		verbose_name_plural = 'Sessions'

	def __str__(self):
		return self.name

	# def todays_sessions(date):
	# 	sessions = Daily_Session.objects.filter(date=date).order_by('session_start_date_time')
	# 	return sessions

	# def short_name(self):
	# 	str_for_return = str(self.day_time.get_slot_session_times())
	# 	return str_for_return

	# def date_session_slot(self):
	# 	str_for_return = self.date.strftime("%B %d, %Y") + ' - ' +self.day_time.session_slot
	# 	return str_for_return 

	# def short_date_day_session_slot(self):
	# 	str_for_return = self.date.strftime("%b %d") +' - '+ self.day_time.day.short_name +' - ' +self.day_time.session_slot
	# 	return str_for_return 

	# def month_day_session_slot(self):
	# 	str_for_return = self.date.strftime("%b %d") + ' - ' +self.day_time.session_slot
	# 	return str_for_return  


	# def all_attendance_records(self):
	# 	# session = Daily_Session.objects.get(pk=self.id)
	# 	records = self.match_attendance_session.all()
	# 	# print("\nRecords", self, records)
	# 	return records

	# def scheduled_attendance_records(self):
	# 	# session = Daily_Session.objects.get(pk=self.id)
	# 	records = self.match_attendance_session.filter(match_type__name="Scheduled")
	# 	# print("\nRecords", self, records)
	# 	return records

	# def temporary_attendance_records(self):
	# 	# session = Daily_Session.objects.get(pk=self.id)
	# 	records = self.match_attendance_session.filter(match_type__name="Temporary")
	# 	# print("\nRecords", self, records)
	# 	return records

	# def all_match_statuses(self):
	# 	print("\nall_match_statuses", self)
	# 	print("Scheduled Matches")
	# 	matches = self.scheduled_matches_in_session.filter(active=True)
	# 	# session = Daily_Session.objects.get(pk=self.id)
	# 	records = self.match_status_session.all()
	# 	# print("\nRecords", self, records)
	# 	return matches

	# def successful_sch_matches(self):
	# 	successful = self.match_attendance_session.filter(match_type__name="Scheduled",
	# 		match_successful=True)
	# 	return successful

	# def number_successful_matches(self):
	# 	successful = self.match_attendance_session.filter(match_successful=True).count()
	# 	return successful

	# def percent_successful_sch_matches(self):
	# 	all_scheduled_complete = self.match_attendance_session.filter(match_type__name="Scheduled",
	# 							match_successful=True).count()
	# 	all_scheduled = self.match_attendance_session.filter(match_type__name="Scheduled").count()
	# 	print("All scheduled Count", all_scheduled)

		
	# 	# print("count_of_all", count_of_all)
	# 	if all_scheduled != 0:
	# 		# print("not zero")
	# 		# print("query",self.session_attendance_record.filter(match_successful=True))
	# 		successful = all_scheduled_complete
	# 		percent_i = (successful/all_scheduled) * 100
	# 		percent = round(percent_i, 2)
	# 		str_for_return = str(percent) + " %"
	# 	else:
	# 		# print("zero")
	# 		str_for_return = "No Matches"
	# 	# print("str_for_return", str_for_return)
	# 	return str_for_return

	

	
def pre_save_daily_session_receiver(sender, instance, *args, **kwargs):
	instance.name =  instance.date.strftime("%B %d, %Y") + " - " + instance.day_time.day.name + " " + instance.day_time.session_slot
	instance.slug = slugify(instance.name)

	start_date_time = datetime.datetime(instance.date.year,
										 instance.date.month,
										 instance.date.day,
										 instance.day_time.time_start.hour,
										 instance.day_time.time_start.minute,
										 instance.day_time.time_start.second)

	end_date_time = datetime.datetime(instance.date.year,
									 instance.date.month,
									 instance.date.day,
									 instance.day_time.time_end.hour,
									 instance.day_time.time_end.minute,
									 instance.day_time.time_end.second)

	instance.session_start_date_time = start_date_time
	instance.session_end_date_time = end_date_time

	five_minutes = datetime.timedelta(minutes=5)


	stu_entry_start = start_date_time - five_minutes
	stu_entry_end = end_date_time + five_minutes

	instance.student_entry_allowed_start = str(stu_entry_start)
	instance.student_entry_allowed_end = str(stu_entry_end)


pre_save.connect(pre_save_daily_session_receiver, sender=Daily_Session)

def post_save_daily_session_receiver(sender, instance, *args, **kwargs):
	# print("Post Save")
	if not instance.archive_session:
		day_with_session, created = Day_With_Daily_Session.objects.get_or_create(date = instance.date,
																		day = instance.day_time.day, 
																		semester = instance.semester,
																		week=instance.week)
		day_with_session.add_session(instance)
	else:
		day_with_session, created = Day_With_Daily_Session.objects.get_or_create(date = instance.date,
																		day = instance.day_time.day, 
																		semester = instance.semester,
																		week=instance.week)
		day_with_session.remove_session(instance)


post_save.connect(post_save_daily_session_receiver, sender=Daily_Session)



class Day_With_Daily_Session(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False) 
	semester =  models.ForeignKey(Program_Semester, on_delete=models.CASCADE, related_name='semester_day', null=True, blank=True)
	day_sessions = models.ManyToManyField(Daily_Session,
									 related_name="day_sessions",
									 blank=True,)
	week = models.IntegerField(null=True, blank=True)
	count = models.IntegerField(default = 0)
	all_complete = models.BooleanField(default=False)
	total_matches = models.IntegerField(default=0)
	total_active_scheduled = models.IntegerField(default=0)
	total_temporary = models.IntegerField(default=0)
	total_complete_scheduled_matches = models.IntegerField(default=0)
	percent_successful = models.DecimalField(default=0, max_digits=5, decimal_places=2)
	total_complete_reading_count = models.IntegerField(default=0)

	def add_session(self, session):
		self.day_sessions.add(session)
		self.count = self.day_sessions.all().count()
		self.save()

	def remove_session(self, session):
		self.day_sessions.remove(session)
		self.count = self.day_sessions.all().count()
		self.save()

	# def set_final_stats(self):
	# 	self.all_complete = True
	# 	self.total_matches = self.total_matches_day()
	# 	self.total_active_scheduled = self.active_scheduled_matches_in_day()
	# 	self.total_temporary = self.temporary_matches_in_day()
	# 	self.total_complete_scheduled_matches = self.total_complete_scheduled_matches_func()
	# 	self.total_complete_reading_count = self.total_complete_reading()
		
	# 	if self.total_active_scheduled != 0:
	# 		percent_i = (self.total_complete_scheduled_matches/self.total_active_scheduled) * 100
	# 		self.percent_successful = percent_i


	# 	self.save()

	# def total_matches_day(self):
	# 	count = 0
	# 	for session in self.day_sessions.all():
	# 		matches = session.all_attendance_records()
	# 		matches_count = matches.count()
	# 		count = count+ matches_count

	# 	return count

	# def active_scheduled_matches_in_day(self):  
	# 	count= 0
	# 	for session in self.day_sessions.all():
	# 		matches = session.scheduled_attendance_records()
	# 		matches_count = matches.count()
	# 		count = count+ matches_count
	# 	# print("final count", count)
	# 	return count

	# def temporary_matches_in_day(self):  
	# 	count= 0
	# 	for session in self.day_sessions.all():
	# 		matches = session.temporary_attendance_records()
	# 		matches_count = matches.count()
	# 		count = count+ matches_count
	# 	# print("final count", count)
	# 	return count 

	# def total_complete_scheduled_matches_func(self):
	# 	count= 0
	# 	for session in self.day_sessions.all():
	# 		matches = session.successful_sch_matches()
	# 		matches_count = matches.count()
	# 		count = count+ matches_count
	# 	# print("total_complete_scheduled_matches final count", count)
	# 	return count 

	# def total_complete_reading(self):
	# 	count= 0
	# 	for session in self.day_sessions.all():
	# 		ses_count = session.number_successful_matches()
	# 		count = count + ses_count
	# 	# print("total_complete_reading final count", count)
	# 	return count 


	# def percent_successful_matches_str(self):
	# 	if self.total_active_scheduled != 0:
	# 		str_for_return = str(self.percent_successful) + " %"
	# 	else:  
	# 		str_for_return = "Not Calculated"
			
	# 	return str_for_return

	# def short_day_name(self):
	# 	str_for_return= ""
	# 	str_for_return = self.day.short_name + " - " + str(self.date.month) +"/" + str(self.date.day)
		
	# 	return str_for_return 

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Daily Sessions'
		verbose_name_plural = 'Days With Daily Sessions'

	def __str__(self):
		return self.day.name + " - " + str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)


class Gender(models.Model):
	letter = models.CharField(max_length=3, null=True, blank=True, unique=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	eng_gender = models.CharField(max_length=100, null=True, blank=True)
	span_gender = models.CharField(max_length=100, null=True, blank=True)
	for_users = models.CharField(max_length=100, null=True, blank=True)
	active=models.BooleanField(default=True)
	

	class Meta:
		ordering = ['letter']
		verbose_name = 'Gender'
		verbose_name_plural = 'Genders'

	def __str__(self):
		return self.name

class Ethnicity(models.Model):
	eng_option = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span_option = models.CharField(max_length=100, null=True, blank=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Ethnicity'
		verbose_name_plural = 'Ethnicities'

	def __str__(self):
		return self.eng_option

class Current_Education_Level(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span_name = models.CharField(max_length=100, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Current Education Level'
		verbose_name_plural = 'Current Education Levels'

	def __str__(self):
		return self.name

class Current_Education_Class(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span_name = models.CharField(max_length=100, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Current Education Class'
		verbose_name_plural = 'Current Education Classes'

	def __str__(self):
		return self.name



class Team_Meeting_Time(models.Model):
	meeting_day = models.ForeignKey(Day, related_name="team_meeting_day",
							 on_delete=models.CASCADE ,null=True, blank=True)
	meeting_time = models.TimeField(null=True, blank=True)
	timezone = models.CharField(max_length=5, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Team Meeting Time'
		verbose_name_plural = 'Team Meeting Times'

	def string_for_return(self):
		string_for_return = ""
		if self.meeting_day and self.meeting_time and self.timezone:
			time_string = format_time_str(self.meeting_time)
			string_for_return = self.meeting_day.name + ' at ' + time_string + " " + self.timezone
		return string_for_return

	def __str__(self):
		return self.string_for_return()

class Session_Day_Option(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	span_name = models.CharField(max_length=100, null=True, blank=True)
	desc = models.CharField(max_length=100, null=True, blank=True)
	span_desc = models.CharField(max_length=100, null=True, blank=True)
	days = models.ManyToManyField(Day, related_name="session_options",
					blank=True,)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Session Day Option'
		verbose_name_plural = 'Session Day Options'

	def string_for_return(self):
		string_for_return = ""
		if self.name:
			string_for_return = self.name 
		return string_for_return

	def __str__(self):
		return self.string_for_return()

@receiver(pre_save, sender=Session_Day_Option)
def span_name(sender, instance=None, **kwargs):
	if instance.name:
		span_name_str = ""

		if instance.days.all().count() == 2:
			span_name_str = instance.days.all().first().span_name + " & " + instance.days.all().last().span_name

		elif instance.days.all().count() == 3:
			list_day = list(instance.days.all())
			span_name_str = list_day[0].span_name + ", " + list_day[1].span_name + " & " + list_day[2].span_name 
	
		instance.span_name = span_name_str

class Session_Time_Option(models.Model):
	start_time = models.TimeField(null=True, blank=True)
	end_time = models.TimeField(null=True, blank=True)
	timezone = models.CharField(max_length=5, null=True, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Session Time Option'
		verbose_name_plural = 'Session Time Options'

	def time_string(self):
		string_for_return = ""
		if self.start_time and self.end_time and self.timezone:
			start_time_str = format_time_str(self.start_time)
			end_time_str = format_time_str(self.end_time)

			string_for_return = start_time_str + "-" + end_time_str
		return string_for_return

	def string_for_return(self):
		string_for_return = ""
		if self.start_time and self.end_time and self.timezone:
			start_time_str = format_time_str(self.start_time)
			end_time_str = format_time_str(self.end_time)

			string_for_return = start_time_str + " - " + end_time_str + " " + self.timezone
		return string_for_return

	def __str__(self):
		return self.string_for_return()

class Session_Meeting_Option(models.Model):
	day_option = models.ForeignKey(Session_Day_Option, related_name="session_day",
	 							on_delete=models.CASCADE ,null=True, blank=True)
	time_option = models.ForeignKey(Session_Time_Option, related_name="session_time",
	 							on_delete=models.CASCADE ,null=True, blank=True)
	slot_letter = models.CharField(max_length=2, null=True, blank=True,)
	session_day_times = models.ManyToManyField(Reading_Session_Day_Time,
											 related_name="option_sessions", blank=True,)
	active=models.BooleanField(default=True)


	class Meta:
		ordering = ['id']
		verbose_name = 'Session Meeting Option'
		verbose_name_plural = 'Session Meeting Options'

	def short_name(self):
		string_for_return = ""
		for day in self.day_option.days.all():
			string_for_return = string_for_return + day.letter

		string_for_return = string_for_return + "-" + self.slot_letter

		return string_for_return


	def string_for_return(self):
		string_for_return = ""
		if self.day_option and self.time_option:
			string_for_return = str(self.day_option) + ": " + str(self.time_option)
		return string_for_return

	def __str__(self):
		return self.string_for_return()

class Opportunity_Source(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Opportunity Source'
		verbose_name_plural = 'Opportunity Sources'

	def __str__(self):
		return self.name

class Social_Media_Source(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Social Media Source'
		verbose_name_plural = 'Social Media Sources'

	def __str__(self):
		return self.name

class Device_Type(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=False)
	for_users = models.CharField(max_length=100, null=True, blank=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Device Type'
		verbose_name_plural = 'Device Types'

	def __str__(self):
		return self.name


class Volunteer_Opportunity(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False, unique=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Opportunity'
		verbose_name_plural = 'Volunteer Opportunities'

	def __str__(self):
		return self.name

class Volunteer_Reason(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Volunteer Reason'
		verbose_name_plural = 'Volunteer Reasons'

	def __str__(self):
		return self.name

class Application_Recipient(models.Model):
	recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='app_recipient', null=False, blank=False,)
	receive_student = models.BooleanField(verbose_name="Student Registration", default=True)
	receive_vol = models.BooleanField(verbose_name="Volunteer Registration", default=True)
	active = models.BooleanField(default=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Application Recipient'
		verbose_name_plural = 'Application Recipients'

	def __str__(self):
		return self.recipient.username

class Web_Source(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Web Source'
		verbose_name_plural = 'Web Sources'

	def __str__(self):
		return self.name

class Parent_Additional_Information(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	eng_text = models.TextField(max_length=1500, null=True, blank=True)
	span_text = models.TextField(max_length=1500, null=True, blank=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Parent Additional Information'
		verbose_name_plural = 'Parent Additional Information'

	def __str__(self):
		return self.name

class Message_App(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Message App'
		verbose_name_plural = 'Message Apps'

	def __str__(self):
		return self.name

class Reading_Description(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	eng_text = models.CharField(max_length=100, null=True, blank=True,)
	span_text = models.CharField(max_length=100, null=True, blank=True,)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Reading Description'
		verbose_name_plural = 'Reading Descriptions'

	def __str__(self):
		return self.name

class Student_Characteristic (models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	eng_text = models.TextField(max_length=1500, null=True, blank=True)
	span_text = models.TextField(max_length=1500, null=True, blank=True)
	active=models.BooleanField(default=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Student Characteristic'
		verbose_name_plural = 'Student Characteristics'

	def __str__(self):
		return self.name


class Room_Type(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	letter = models.CharField(max_length=1, null=False, blank=True)
	active=models.BooleanField(default=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Room Type'
		verbose_name_plural = 'Room Types'

	def __str__(self):
		return self.name

class Room(models.Model):
	name = models.CharField(max_length=150, blank=False, unique=True)
	number = models.IntegerField(blank=True, null=True)
	room_type = models.ForeignKey(Room_Type, on_delete=models.CASCADE, related_name="type_room",
								 null=True, blank=True, verbose_name="Room Type")
	slug = models.SlugField(blank=True, unique=True, max_length=255,)
	room_url = models.URLField(max_length=500, null=True, blank=True)
	show_in_session_list = models.BooleanField(default=True, verbose_name="show in session")
	active=models.BooleanField(default=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Room'
		verbose_name_plural = 'Rooms'

	def __str__(self):
		return self.name

def pre_save_room_receiver(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.name)
	instance.room_url = settings.BASE_URL + "/sessions/room/" + instance.slug +"/"
pre_save.connect(pre_save_room_receiver, sender=Room)

def post_save_room_receiver(sender, instance, *args, **kwargs):
	try:
		participicants = instance.participants
		print("participants")
	except Exception as e:
		print("Exception Post Save Room", e)
		participicants = apps.get_model(app_label='reading_sessions', model_name='Room_Participants').objects.create(room=instance)

post_save.connect(post_save_room_receiver, sender=Room)


class Server_Schedule(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)	
	active = models.BooleanField(default=False)
	offset = models.IntegerField(null=True, blank=True, help_text="-240 DST, -300 no DST")
	# times = models.ManyToManyField(Server_Time, related_name="server_times", blank=True,)

	def save(self, *args, **kwargs):
		super(Server_Schedule, self).save(*args, **kwargs)
		if self.active:
			qs = type(self).objects.filter(active=True)
			if self.pk:
				qs = qs.exclude(pk=self.pk)
			qs.update(active=False) 		

		super(Server_Schedule, self).save(*args, **kwargs)


	class Meta:
		ordering = ['name']
		verbose_name = 'Server Schedule'
		verbose_name_plural = 'Server Schedules'

	def __str__(self):
		return self.name

class Server_Time(models.Model):
	server_schedule = models.ForeignKey(Server_Schedule, related_name="schedule",
							 on_delete=models.CASCADE ,null=True, blank=True)	
	name = models.CharField(max_length=100, null=False, blank=False,)
	day = models.ForeignKey(Day, related_name="server_on_day",
							 on_delete=models.CASCADE ,null=False, blank=False)	
	date = models.DateField(null=True, blank=True)
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['name']
		verbose_name = 'Server Time'
		verbose_name_plural = 'Server Times'

	def __str__(self):
		return self.name

class Mega_Team(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	coordinator = models.ForeignKey(CustomUser, related_name="mega_coordinator",
					blank=True, null=True, on_delete=models.CASCADE)
	team_leaders = models.ManyToManyField(CustomUser, related_name="mega_team_leaders",
					blank=True,)
	volunteers = models.ManyToManyField(CustomUser, related_name="mega_team_vol",
					blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Mega Team'
		verbose_name_plural = 'Mega Teams'

	def __str__(self):
		return self.name

class Team(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=False)
	mega = models.ForeignKey(Mega_Team, related_name="teams",
					blank=True, null= True, on_delete=models.SET_NULL)
	leader = models.ForeignKey(CustomUser, related_name="team_leader",
					blank=True, null=True, on_delete=models.SET_NULL)
	volunteers = models.ManyToManyField(CustomUser, related_name="team_vols",
					blank=True,)
	room = models.ForeignKey(Room, related_name="team_room",
					blank=True, null= True, on_delete=models.SET_NULL)
	meeting_day = models.ForeignKey(Day, related_name="day_of_week", on_delete=models.CASCADE ,null=True, blank=True)
	meeting_time = models.TimeField(null=True, blank=True)
	meeting_day_time = models.ForeignKey(Team_Meeting_Time, related_name="team_time", on_delete=models.CASCADE ,null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def get_mega_and_team(self):
		str_for_return = self.mega.name + " - " + self.name
		return str_for_return

	class Meta:
		ordering = ['id']
		verbose_name = 'Team'
		verbose_name_plural = 'Teams'

	def __str__(self):
		return self.mega.name + " - " + self.name	

def pre_save_team_receiver(sender, instance, *args, **kwargs):
	if instance.meeting_day_time:
		instance.meeting_day = instance.meeting_day_time.meeting_day
		instance.meeting_time = instance.meeting_day_time.meeting_time
	
pre_save.connect(pre_save_team_receiver, sender=Team)

class Team_Meeting(models.Model):
	date = models.DateField(verbose_name="Date",blank=True, null=True)
	team = models.OneToOneField(Team, related_name="meeting", on_delete=models.CASCADE, blank=True, null=True)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,blank=True, null=True) 
	time_start = models.TimeField(blank=True, null=True)
	time_end = models.TimeField(blank=True, null=True)

	class Meta:
		ordering = ['id',]
		verbose_name = 'Team Meeting'
		verbose_name_plural = 'Team Meetings'

	def __str__(self):
		return str(self.team) + " Meeting"

class Day_With_Team_Meeting(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False) 
	server_on = models.TimeField(blank=True, null=True)
	server_off = models.TimeField(blank=True, null=True)
	semester =  models.ForeignKey(Program_Semester, on_delete=models.CASCADE, related_name='semester_meetings', null=True, blank=True)
	day_meetings = models.ManyToManyField(Team_Meeting,
									 related_name="day_meetings",
									 blank=True,)
	
	count = models.IntegerField(default = 0)

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Team Meeting'
		verbose_name_plural = 'Day With Team Meetings'

	def __str__(self):
		return self.day.name + " - " + str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)

class Day_With_Orientation_Meeting(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	time_start = models.TimeField(blank=True, null=True)
	time_end = models.TimeField(blank=True, null=True)
	allowed_participants = models.ManyToManyField(CustomUser, related_name="orientation_allowed", blank=True)

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Orientation Meeting'
		verbose_name_plural = 'Day With Orientation Meetings'

	def __str__(self):
		return str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)


