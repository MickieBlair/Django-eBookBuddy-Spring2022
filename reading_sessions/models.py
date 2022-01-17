from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import datetime

from users.models import CustomUser, Role
from matches.models import Match_Type, Scheduled_Match, Temporary_Match
from matches.models import Match_Note, Match_Status_Option
from matches.models import Match_Attendance_Record
from buddy_program_data.models import Room, Daily_Session

def localtime_now_date():
	date_now = timezone.localtime(timezone.now()).date()
	return date_now

def localtime_now():
	date_now = timezone.localtime(timezone.now())
	return date_now
 
# Create your models here.
class User_Session_Status(models.Model):
	user = models.OneToOneField(CustomUser, related_name="session_status", on_delete=models.CASCADE)
	manual_redirect_on = models.BooleanField(default=False)
	has_redirect = models.BooleanField(default=False, verbose_name="Redirect")
	all_connected = models.BooleanField(default=False)
	online_jitsi = models.BooleanField(default=False)
	online_ws = models.BooleanField(default=False)
	on_landing_page = models.BooleanField(default=False)

	needs_new_buddy = models.BooleanField(default=False, verbose_name="Needs New Buddy")
	needs_session_match = models.BooleanField(verbose_name="Needs Match", default=False)

	current_active_match_type = models.ForeignKey(Match_Type, on_delete=models.SET_NULL,
					related_name='current_type_active', null=True, blank=True,
					verbose_name = "Type Active")

	buddies = models.ManyToManyField(CustomUser, related_name="all_buddies", blank=True,)
	
	active_buddy = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
									related_name='active_buddy', null=True, blank=True)


	active_scheduled_match = models.ForeignKey(Scheduled_Match, on_delete=models.SET_NULL,
					related_name="sch_match", null=True, blank=True)

	scheduled_matches = models.ManyToManyField(Scheduled_Match,	related_name="sch_matches",
											 blank=True)


	temp_match = models.ForeignKey(Temporary_Match, on_delete=models.SET_NULL,
					related_name="temp_match", null=True, blank=True)
	

	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_location', null=True, blank=True)

	room_jitsi = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_from_jitsi', null=True, blank=True)


	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")


	# def student_adjust_for_temp_match(self, temp_match, student_scheduled_match):
	# 	match_type = Match_Type.objects.get(name="Temporary - In Session")
	# 	self.needs_new_buddy = False
	# 	self.needs_session_match = False
	# 	self.current_active_match_type = match_type
	# 	self.temp_match = temp_match
	# 	self.save()

	class Meta:
		ordering = ['user']
		verbose_name = 'User Session Status'
		verbose_name_plural = 'User Session Statuses'

	def __str__(self):
		return self.user.full_name()  + ": User Session Status"

def pre_save_user_session_status_receiver(sender, instance, **kwargs):
	pass
	# print("\n\n\n\n\nSAVING", instance.user, instance.manual_redirect_on)

pre_save.connect(pre_save_user_session_status_receiver, sender=User_Session_Status)



class Match_Session_Status(models.Model):
	match_status_active = models.BooleanField(default=True, verbose_name="Active")
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
					related_name='match_status_session', null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
					related_name='match_status_type', null=True, blank=True)	
	sch_match = models.ForeignKey(Scheduled_Match,
										related_name="sch_match_status",
										on_delete=models.CASCADE, null=True, blank = True)


	member_reassigned = models.BooleanField(default=False, verbose_name="M-R")
	reader_reassigned = models.BooleanField(default=False, verbose_name="R-R")
	student_reassigned = models.BooleanField(default=False, verbose_name="S-R")

	temp_match = models.ForeignKey(Temporary_Match,
										related_name="temp_match_status",
										on_delete=models.CASCADE, null=True, blank = True)
	
	student_online = models.BooleanField(default=False, verbose_name="S-Online")
	display_student_location = models.BooleanField(default=True)
	reader_online = models.BooleanField(default=False, verbose_name="R-Online")
	display_reader_location = models.BooleanField(default=True)
	both_online = models.BooleanField(default=False, verbose_name="Both Present")
	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='match_location', null=True, blank=True)
	status = models.ForeignKey(Match_Status_Option, related_name="status_option",
									on_delete=models.CASCADE, null=True, blank = True)
	match_status_notes = models.ManyToManyField(Match_Note, related_name="match_status_notes", blank=True,)

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['session__date', 'session__day_time', 'both_online']
		verbose_name = 'Match Session Status'
		verbose_name_plural = 'Match Session Statuses'

	def student_adjust_for_temp_match_creation(self, temp_match):
		self.match_status_active = False
		self.session = self

			


	def get_type(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.match_type.short_name

	def get_student(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.student	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.temp_match.student

	def get_buddy(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.reader	
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.temp_match.reader

	def string_for_return(self):
		# return str(self.id)
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name	+ " - " + str(self.sch_match)		
		else:
			if self.match_type.name == "Temporary - In Session":
				return self.match_type.short_name + " - " + str(self.temp_match)	


	def __str__(self):
		return self.string_for_return()

def pre_save_match_status_receiver(sender, instance, *args, **kwargs):
	print("Saving Match Session Status", instance.id)
	if instance.student_reassigned and instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Both Reassigned")
		instance.display_reader_location = False
		instance.display_student_location = False
		instance.room = None

	elif instance.student_reassigned and not instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Student Reassigned")
		instance.display_student_location = False
		instance.room = None

	elif not instance.student_reassigned and instance.reader_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Reader Reassigned")
		instance.display_reader_location = False
		instance.room = None

	else:
		instance.display_reader_location = True
		instance.display_student_location = True
		if not instance.student_online and not instance.reader_online:
			instance.status = Match_Status_Option.objects.get(name="Both Missing")
			instance.room = None
			instance.both_online = False

		elif instance.student_online and not instance.reader_online:
			instance.status = Match_Status_Option.objects.get(name="Reader Missing")
			instance.room = None
			instance.both_online = False

		elif not instance.student_online and instance.reader_online:
			instance.status = Match_Status_Option.objects.get(name="Student Missing")
			instance.room = None
			instance.both_online = False

		else:
			if instance.student_online and instance.reader_online:
				instance.both_online = True

				if instance.match_type:

					if instance.match_type.name == "Scheduled":
						match = instance.sch_match
						if match.student.session_status.room == match.reader.session_status.room:
							instance.room = match.reader.session_status.room
							instance.status = Match_Status_Option.objects.get(name="In Room")
							instance.display_reader_location = False
							instance.display_student_location = False
						else:
							print("ROOM IS NOT THE SAME")
							instance.status = Match_Status_Option.objects.get(name="Pending Redirect")

					else:
						match = instance.temp_match
						if match.student.session_status.room == match.reader.session_status.room:
							instance.room = match.reader.session_status.room
							instance.status = Match_Status_Option.objects.get(name="In Room")
							instance.display_reader_location = False
							instance.display_student_location = False
						else:
							print("ROOM IS NOT THE SAME")
							instance.status = Match_Status_Option.objects.get(name="Pending Redirect")
			
				else:
					print("no match type")
					


			# print("Do something with the Room for Temp and Scheduled")

pre_save.connect(pre_save_match_status_receiver, sender=Match_Session_Status)

def post_save_match_status_receiver(sender, instance, *args, **kwargs):
	if instance.match_type.name == "Scheduled":
		match_attendance_record, created = Match_Attendance_Record.objects.get_or_create(
										session = instance.session,
										match_type=instance.match_type,
										sch_match=instance.sch_match,
										)
		if not match_attendance_record.student_present and instance.student_online:
			match_attendance_record.student_present = True

		if not match_attendance_record.reader_present and instance.reader_online:
			match_attendance_record.reader_present = True

		if not match_attendance_record.member_reassigned and instance.member_reassigned:
			match_attendance_record.member_reassigned = True

		if not match_attendance_record.student_reassigned and instance.student_reassigned:
			match_attendance_record.student_reassigned = True

		if not match_attendance_record.reader_reassigned and instance.reader_reassigned:
			match_attendance_record.reader_reassigned = True


		if not match_attendance_record.match_successful:
			if not match_attendance_record.member_reassigned:
				if match_attendance_record.student_present and match_attendance_record.reader_present:
					if instance.room:
						match_attendance_record.match_successful= True 
					else:
						match_attendance_record.match_successful = False
				else:
					match_attendance_record.match_successful = False

		match_attendance_record.save()


	elif instance.match_type == "Temporary - In Session":
		match = instance.temp_match


	# if instance.student_reassigned and instance.reader_reassigned:
	# 	instance.status = Match_Status_Option.objects.get(name="Both Reassigned")
	# 	instance.display_reader_location = False
	# 	instance.display_student_location = False
	# 	instance.room = None

	# elif instance.student_reassigned and not instance.reader_reassigned:
	# 	instance.status = Match_Status_Option.objects.get(name="Student Reassigned")
	# 	instance.display_student_location = False
	# 	instance.room = None

	# elif not instance.student_reassigned and instance.reader_reassigned:
	# 	instance.status = Match_Status_Option.objects.get(name="Reader Reassigned")
	# 	instance.display_reader_location = False
	# 	instance.room = None

	# else:
	# 	instance.display_reader_location = True
	# 	instance.display_student_location = True
	# 	print("INSTANCE.ID", instance.id)
	# 	if not instance.student_online and not instance.reader_online:
	# 		instance.status = Match_Status_Option.objects.get(name="Both Missing")
	# 		instance.room = None
	# 		instance.both_online = False

	# 	elif instance.student_online and not instance.reader_online:
	# 		instance.status = Match_Status_Option.objects.get(name="Reader Missing")
	# 		instance.room = None
	# 		instance.both_online = False

	# 	elif not instance.student_online and instance.reader_online:
	# 		instance.status = Match_Status_Option.objects.get(name="Student Missing")
	# 		instance.room = None
	# 		instance.both_online = False

	# 	else:
	# 		if instance.student_online and instance.reader_online:
	# 			instance.both_online = True

	# 			if instance.match_type.name == "Scheduled":
	# 				match = instance.sch_match
	# 				if match.student.session_status.room == match.reader.session_status.room:
	# 					instance.room = match.reader.session_status.room
	# 					instance.status = Match_Status_Option.objects.get(name="In Room")
	# 					instance.display_reader_location = False
	# 					instance.display_student_location = False
	# 				else:
	# 					print("ROOM IS NOT THE SAME")
	# 					instance.status = Match_Status_Option.objects.get(name="Pending Redirect")
		

					


	# 		print("Do something with the Room for Temp and Scheduled")

post_save.connect(post_save_match_status_receiver, sender=Match_Session_Status)


class Redirect(models.Model):
	user_to_redirect = models.OneToOneField(CustomUser,
							related_name='redirect',
							on_delete=models.CASCADE , unique=True)

	to_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='location', null=True, blank=True)

	to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
							related_name='redirect_to', null=True, blank=True)

	redirect_url = models.URLField(max_length=500, null=True, unique=False,
								 blank=True)
	auto_send = models.BooleanField(default=False)

	created_by = models.ForeignKey(CustomUser, related_name='created_by_user',
									on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.user_to_redirect.username

	class Meta:
		verbose_name = 'Redirect'
		verbose_name_plural = 'Redirects'


def pre_save_redirect_receiver(sender, instance, *args, **kwargs):
	instance.user_to_redirect.session_status.has_redirect = True
	instance.user_to_redirect.session_status.save()
	if instance.to_room:
		instance.redirect_url = settings.BASE_URL + "/sessions/room/" + instance.to_room.slug +"/"

pre_save.connect(pre_save_redirect_receiver, sender=Redirect)

def pre_delete_redirect_receiver(sender, instance, *args, **kwargs):
	print("Redirect Being Delete")
	instance.user_to_redirect.session_status.has_redirect = False
	instance.user_to_redirect.session_status.save()

pre_delete.connect(pre_delete_redirect_receiver, sender=Redirect)


class Reading_Session_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Reading Session Error'
		verbose_name_plural = 'Reading Session Errors'

	def __str__(self):
		return self.file


class Help_Request(models.Model):
	from_user = models.ForeignKey(CustomUser,
							related_name='request',
							on_delete=models.CASCADE, unique=False)
	from_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_needing_help', null=True, blank=True, unique=False)
	room_url = models.URLField(max_length=500, null=True, unique=False,
								 blank=True)
	created = models.DateTimeField(auto_now_add=True)
	message = models.TextField(unique=False, blank=False,)
	user_message = models.TextField(unique=False, blank=True,)
	reply = models.TextField(null=True, blank=True,)
	done = models.BooleanField(default=False)
	visited_by = models.ForeignKey(CustomUser,
							related_name='completed_by', null=True, blank=True,
							on_delete=models.CASCADE, unique=False)
	visited_time = models.DateTimeField(verbose_name="visited time", null=True, blank=True,)

	def mark_as_done(self, completed_by):
		print("IN MARK AS DONE", completed_by)
		user = CustomUser.objects.get(id = completed_by)
		print(user)
		self.visited_by = user
		self.done = True
		self.visited_time = timezone.now()
		self.save()
		print("IN MARK AS DONE", self.done)

	def __str__(self):
		return self.from_user.username

	class Meta:
		verbose_name = 'Help Request'
		verbose_name_plural = 'Help Requests'



def pre_save_help_request_receiver(sender, instance, *args, **kwargs):
	if not instance.room_url:
		instance.room_url = settings.BASE_URL + "/sessions/" + instance.from_room.slug +"/"

pre_save.connect(pre_save_help_request_receiver, sender=Help_Request)


class Room_Participants(models.Model):
	room = models.OneToOneField(Room, on_delete=models.CASCADE, 
							related_name='participants', null=True, blank=True)
	jitsi_users = models.ManyToManyField(CustomUser, related_name="users_jitsi", blank=True,)
	jitsi_count = models.IntegerField(default=0, null=True, blank=True)
	ws_users = models.ManyToManyField(CustomUser, related_name="users_ws", blank=True,)
	ws_count = models.IntegerField(default=0, null=True, blank=True)
	occupied_ws = models.BooleanField(default=False)
	occupied_jitsi = models.BooleanField(default=False)

	def __str__(self):
		return self.room.name + " Participants"

	def unoccupied_breakout_first():
		room = Room_Participants.objects.filter(room__name__contains="Breakout",
											 occupied_ws=False,
											 occupied_jitsi=False).first().room
		return room

	def ws_add_user(self, user):
		self.ws_users.add(user)
		self.ws_count = self.ws_users.all().count()
		if self.ws_count == 0:
			self.occupied_ws = False
		else:
			self.occupied_ws = True
		self.save()

	def ws_remove_user(self, user):
		self.ws_users.remove(user)
		self.ws_count = self.ws_users.all().count()
		if self.ws_count == 0:
			self.occupied_ws = False
		else:
			self.occupied_ws = True
		self.save()

	def join_room(self, user):
		print("Joining the room", user)
		self.ws_add_user(user)
		redirect = None
		match_pending_room = Room.objects.get(name="Match Pending")
		student_role = Role.objects.get(name="Student")
		reader_role = Role.objects.get(name="Reader")
		session_status = User_Session_Status.objects.get(user=user)
		session_status.online_ws = True
		if session_status.room != self.room:
			session_status.room = self.room
		session_status.save()

		redirects = Redirect.objects.filter(user_to_redirect = user)
		for item in redirects:
			if item.to_room == self.room:
				item.delete()

		if reader_role in user.roles.all():
			scheduled_students = session_status.buddies.all()
			print("scheduled_students", scheduled_students)
			if scheduled_students.count() == 1:
				scheduled_student = scheduled_students.first()
				print("scheduled_student", scheduled_student)
				scheduled_student_status = User_Session_Status.objects.get(user=scheduled_student)
				match_pending_occupants = Room_Participants.objects.get(room=match_pending_room)
				if scheduled_student in match_pending_occupants.ws_users.all():
					if scheduled_student_status.current_active_match_type.name == "Scheduled":
						print("Here Scheduled", scheduled_student_status.current_active_match_type.name)
						scheduled_student_status.needs_session_match = False
						scheduled_student_status.save()
						scheduled_match = scheduled_student.session_status.active_scheduled_match
						print("scheduled_match", scheduled_match)
						match_statuses = scheduled_match.sch_match_status
						match_status = match_statuses.get(session__date = localtime_now_date())
						match_status.reader_online = True
						match_status.save()

						redirect, created = Redirect.objects.get_or_create(user_to_redirect=scheduled_student)
						redirect.to_room = self.room
						redirect.to_user = user
						redirect.auto_send = False
						redirect.save()
					else:
						session_status.needs_session_match = True
						session_status.save()
				else:
					match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__reader=user)|
											Q(temp_match__reader=user))
					for status in match_statuses:
						status.reader_online = True
						status.save()
					session_status.needs_session_match = True
					session_status.save()

			elif scheduled_students.count() == 0:
				session_status.needs_session_match = True
				session_status.save()
			else:
				print("USER HAS MORE THAN ONE BUDDY")
				sch_student_online = False
				student_in_match = None
				match_pending_occupants = Room_Participants.objects.get(room=match_pending_room)
				for stu in scheduled_students.all():
					scheduled_student_status = User_Session_Status.objects.get(user=stu)
					if scheduled_student_status.current_active_match_type.name == "Scheduled":
						if stu in match_pending_occupants.ws_users.all():
							sch_student_online = True
							student_in_match = stu

				if sch_student_online and student_in_match:
					scheduled_student_status = User_Session_Status.objects.get(user=student_in_match)
					scheduled_student_status.needs_session_match = False
					scheduled_student_status.save()
					redirect, created = Redirect.objects.get_or_create(user_to_redirect=student_in_match)
					redirect.to_room = self.room
					redirect.to_user = user
					redirect.auto_send = False
					redirect.save()
				else:
					session_status.needs_session_match = True
					session_status.save()

				match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__reader=user)|
											Q(temp_match__reader=user))
				for status in match_statuses:
					status.reader_online = True
					status.save()




		elif student_role in user.roles.all():
			if self.room == match_pending_room:
				session_status.needs_session_match = True
				session_status.save()
			else:
				pass
				# need to reset the need session match for the reader in room

			if session_status.current_active_match_type:
				if session_status.current_active_match_type.name == "Scheduled":
					match_statuses = session_status.active_scheduled_match.sch_match_status
					match_status = match_statuses.get(session__date = localtime_now_date())
					match_status.student_online = True
					match_status.save()
				else:
					print("Student entering with this match type", session_status.current_active_match_type.name)
					print("The temp match", session_status.temp_match)
					print("\n\n\n\n Here")
					new_temp_match = session_status.temp_match
					
				
					if new_temp_match:
						print("if new_temp_match", new_temp_match)
						print("\n\n\n\n Here")
						try:
							temp_match_status = Match_Session_Status.objects.get(
							session=new_temp_match.session,
							temp_match=new_temp_match)
							print('Temp Match STatus Id', temp_match_status.id)
							temp_match_status.student_online = True
							if new_temp_match.reader.session_status.online_ws:
								temp_match_status.reader_online = True
							else:
								temp_match_status.reader_online = False
							temp_match_status.save()
						except Exception as e:
							print("Exception no temp match status",e)
						

					else:
						print("else new_temp_match", new_temp_match)
						print("\n\n\n\n Here")
						# temp_match_session_status = session_status.temp_match.temp_match_status.filter(session=new_temp_match.session)
						# print("temp_match_status", temp_match_session_status)
						# temp_match_status = session_status.temp_match.temp_match_status
						




		return redirect

		




	def leave_room(self, user):
		print("Leaving the room", user)
		student_role = Role.objects.get(name="Student")
		reader_role = Role.objects.get(name="Reader")
		match_pending = Room.objects.get(name="Match Pending")
		self.ws_remove_user(user)
		session_status = User_Session_Status.objects.get(user=user)
		session_status.online_ws = False
		session_status.room = None
		session_status.needs_session_match = False
		session_status.save()

		redirects_for_user = Redirect.objects.filter(user_to_redirect= user)
		for redirect in redirects_for_user:
			redirect.delete()
		redirects_to_user = Redirect.objects.filter(to_user=user)
		for redirect in redirects_to_user:
			redirect.delete()

		if self.room != match_pending:
			remaining_students_in_room = self.ws_users.filter(roles__in=[student_role,])
			print("Students", remaining_students_in_room, remaining_students_in_room.count())
			remaining_others_in_room = self.ws_users.all().exclude(roles__in=[student_role,])
			print("Others", remaining_others_in_room, remaining_others_in_room.count())
			if remaining_others_in_room.count() == 0 and remaining_students_in_room.count() > 0:
			# if remaining_participants_in_room.count() != 0:
				for part in remaining_students_in_room:
					if student_role in part.roles.all():
						redirect, created = Redirect.objects.get_or_create(user_to_redirect=part)
						redirect.to_room = match_pending
						redirect.auto_send = True
						redirect.save()

		if student_role in user.roles.all():
			if session_status.current_active_match_type:
				if session_status.current_active_match_type.name == "Scheduled":
					match_statuses = session_status.active_scheduled_match.sch_match_status
					match_status = match_statuses.get(session__date = timezone.localtime(timezone.now()))
					match_status.student_online = False
					match_status.save()

		elif reader_role in user.roles.all():
			match_statuses = Match_Session_Status.objects.filter(Q(session__date=localtime_now_date()),
											Q(sch_match__reader=user)|
											Q(temp_match__reader=user))
			for status in match_statuses:
				status.reader_online = False
				status.save()

	class Meta:
		verbose_name = 'Room Participants'
		verbose_name_plural = 'Room Participants'
