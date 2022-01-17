from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from users.models import CustomUser
from buddy_program_data.models import Room


class Jitsi_Room(models.Model):
	room_name = models.CharField(max_length=255, null=True, blank=True)
	room_jid = models.CharField(max_length=255, null=True, blank=True)
	event_name = models.CharField(max_length=255, null=True, blank=True)
	created_at = models.DateTimeField(null=True, blank=True)
	destroyed_at = models.DateTimeField(null=True, blank=True)
	# all_occupants = models.ManyToManyField(Jitsi_Room_Occupant, related_name="room_participants",
	# 				blank=True,)
	room = models.ForeignKey(Room, on_delete=models.CASCADE,
								related_name='jitsi_room', null=True, blank=True,)
	instance_created = models.DateTimeField(auto_now_add=True, verbose_name="instance created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Jitsi Room'
		verbose_name_plural = 'Jitsi Rooms'

	def __str__(self):
		return self.room_name

def pre_save_jitsi_room_receiver(sender, instance, *args, **kwargs):
	print("Presave room")
	if instance.room_name:
		print("Instance Room Name", instance.room_name)
		if Room.objects.filter(name__iexact = instance.room_name).exists():
			print("Yes exists")
			instance.room = Room.objects.get(name__iexact = instance.room_name)
		else:
			print("Nope")
pre_save.connect(pre_save_jitsi_room_receiver, sender=Jitsi_Room)

class Jitsi_Room_Occupant(models.Model):
	jitsi_room = models.ForeignKey(Jitsi_Room, on_delete=models.CASCADE,
								related_name='jitsi_room', null=True, blank=True,)
	name = models.CharField(max_length=255, null=True, blank=True)
	email = models.CharField(max_length=255, null=True, blank=True)
	jitsi_id = models.CharField(max_length=255, null=True, blank=True)
	occupant_jid = models.CharField(max_length=255, null=True, blank=True)
	joined_at = models.DateTimeField(null=True, blank=True)
	left_at = models.DateTimeField(max_length=255, null=True, blank=True)	
	total_time = models.DurationField(null=True, blank=True)
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='jitsi_user', null=True, blank=True,)
	instance_created = models.DateTimeField(auto_now_add=True, verbose_name="instance created")

	class Meta:
		ordering = ['id']
		verbose_name = 'Jitsi Room Occupant'
		verbose_name_plural = 'Jitsi Room Occupants'

	def fill_in_duration(self):
		self.total_time = self.left_at - self.joined_at
		self.save()

	def __str__(self):
		return self.name		

def pre_save_jitsi_user_receiver(sender, instance, *args, **kwargs):
	if instance.name:
		if CustomUser.objects.filter(username = instance.name).exists():
			instance.user = CustomUser.objects.get(username = instance.name)
	if instance.occupant_jid:
		instance.jitsi_id = instance.occupant_jid.split('/')[1]	
pre_save.connect(pre_save_jitsi_user_receiver, sender=Jitsi_Room_Occupant)


class Jitsi_User_Event(models.Model):
	event_name = models.CharField(max_length=255, null=True, blank=True)
	room_name = models.CharField(max_length=255, null=True, blank=True)
	in_room = models.BooleanField(default=False)	
	room_jid = models.CharField(max_length=255, null=True, blank=True)
	occupant_name = models.CharField(max_length=255, null=True, blank=True)
	occupant_email = models.CharField(max_length=255, null=True, blank=True)
	occupant_id = models.CharField(max_length=255, null=True, blank=True)
	occupant_jid = models.CharField(max_length=255, null=True, blank=True)
	occupant_joined_at = models.DateTimeField(max_length=255, null=True, blank=True)
	occupant_left_at = models.DateTimeField(max_length=255, null=True, blank=True)
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='user_event', null=True, blank=True,)
	room = models.ForeignKey(Room, on_delete=models.CASCADE,
								related_name='user_room', null=True, blank=True,)
	total_time = models.DurationField(null=True, blank=True)
	instance_created = models.DateTimeField(auto_now_add=True, verbose_name="created")
	instance_updated = models.DateTimeField(auto_now=True, verbose_name="updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Jitsi User Event'
		verbose_name_plural = 'Jitsi User Event'

	def __str__(self):
		return self.occupant_name

	def fill_in_duration(self):
		print("Filling in duration", self.occupant_left_at, self.occupant_joined_at)
		self.total_time = self.occupant_left_at - self.occupant_joined_at
		self.save()

def pre_save_jitsi_event_receiver(sender, instance, *args, **kwargs):

	if instance.occupant_name:
		if CustomUser.objects.filter(username__iexact = instance.occupant_name).exists():
			print("YES exists")
			instance.user = CustomUser.objects.get(username__iexact = instance.occupant_name)
			user_status, created = Jitsi_User_Status.objects.get_or_create(user = instance.user)
	if instance.occupant_jid:
		instance.jitsi_id = instance.occupant_jid.split('/')[1]	

	
	if instance.room_name:
		if Room.objects.filter(name__iexact = instance.room_name).exists():
			instance.room = Room.objects.get(name__iexact = instance.room_name)

	print("pre_save_jitsi_event_receiver occupant_left_at", instance.occupant_left_at)
	print("pre_save_jitsi_event_receiver occupant_joined_at", instance.occupant_joined_at)

	if instance.occupant_joined_at and not instance.occupant_left_at :
		instance.in_room = True

	else:
		instance.in_room = False

	print("Pre Save Done instance.in_room", instance.in_room)

pre_save.connect(pre_save_jitsi_event_receiver, sender=Jitsi_User_Event)

class Jitsi_User_Status(models.Model):
	user= models.OneToOneField(CustomUser, on_delete=models.CASCADE,
								related_name='jitsi_status', null=True, blank=True,)
	online = models.BooleanField(default=False)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Jitsi User Status'
		verbose_name_plural = 'Jitsi User Status'

	def __str__(self):
		return str(self.id)

	def get_online_status(self):
		print("Getting Online STATUS")
		statuses = Jitsi_User_Event.objects.filter(user=self.user, in_room=True)
		print("STATUSES", statuses)
		if statuses.count() > 0:
			self.online = True
			self.save()
		else:
			self.online = False
			self.save()

		return self.online



class Jitsi_Data_Websocket_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Jitsi Data Websocket Error'
		verbose_name_plural = 'Jitsi Data Websocket Errors'

	def __str__(self):
		return self.file