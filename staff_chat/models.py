from django.db import models
from users.models import CustomUser, Role, User_View
from buddy_program_data.models import Room
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete

# Create your models here.
class Staff_Chat_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Staff Chat Error'
		verbose_name_plural = 'Staff Chat Errors'

	def __str__(self):
		return self.file


class Staff_Chat_Room(models.Model):
	# Room title
	title = models.CharField(max_length=255, unique=True, blank=False,)
	slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
	date_created = models.DateField(auto_now_add=True, verbose_name="date created")

	# all users who are authenticated and viewing the chat
	users = models.ManyToManyField(CustomUser,
									blank=True,)

	def __str__(self):
		return self.title


	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		# print("Connecting User in Models.PY")
		is_user_added = False
		try:
			if not user in self.users.all():
				self.users.add(user)
				self.save()
				is_user_added = True
			elif user in self.users.all():
				is_user_added = True
		except Exception as e:
			Staff_Chat_Error.objects.create(file="websockets Staff Chat models.py ",
						function_name=socket_info['connect_user(self, user)'],
						location_in_function=socket_info['connect user'],
						occurred_for_user=user.username,
						error_text=str(e))		
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		try:
			if user in self.users.all():
				self.users.remove(user)
				self.save()
				is_user_removed = True
		except Exception as e:
			Staff_Chat_Error.objects.create(file="websockets Staff Chat models.py ",
						function_name=socket_info['disconnect_user(self, user)'],
						location_in_function=socket_info['disconnect user'],
						occurred_for_user=user.username,
						error_text=str(e))	
		
		
		return is_user_removed 

	class Meta:
		verbose_name = 'Staff Chat Room'
		verbose_name_plural = 'Staff Chat Rooms'


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "Staff_Chat_Room-%s" % self.id

def post_save_create_staff_unread_receiver(sender, instance, *args, **kwargs):
	staff_view = User_View.objects.get(name="Staff View")
	all_staff = staff_view.user_view.filter(is_approved=True)
	for member in all_staff:
		staff_unread, created = Staff_Room_Unread_Chat_Message.objects.get_or_create(user=member)
		if created:
			staff_unread.room = instance 
			staff_unread.unread_count = 0  
			staff_unread.save()

post_save.connect(post_save_create_staff_unread_receiver, sender=Staff_Chat_Room)

class Staff_Chat_Room_Message_Manager(models.Manager):
	def by_room(self, room):
		qs = Staff_Room_Chat_Message.objects.filter(room=room).order_by("-timestamp")
		return qs

class Staff_Room_Chat_Message(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	room = models.ForeignKey(Staff_Chat_Room, on_delete=models.CASCADE,)
	meeting_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='staff_messages', null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	content = models.TextField(unique=False, blank=False,)

	objects = Staff_Chat_Room_Message_Manager()

	def __str__(self):
		return self.content

	class Meta:
		verbose_name = 'Staff Chat Room Message'
		verbose_name_plural = 'Staff Chat Room Messages'



class Staff_Room_Unread_Chat_Message(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="unread_staff")
	room = models.ForeignKey(Staff_Chat_Room, on_delete=models.CASCADE,
												 null=True, blank=True,
												 related_name="room_unread_staff")
	unread_count = models.IntegerField(verbose_name="Unread Count", default=0)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		return self.user.username + " Unread Count"

	def add_one(self):
		self.unread_count = self.unread_count + 1
		self.save()

	def reset_count(self): 
		self.unread_count = 0
		self.save()

	class Meta:
		verbose_name = 'Staff Chat Uread Message'
		verbose_name_plural = 'Staff Chat Unread Messages'