from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.authtoken.models import Token
from users import jwt_token
from django.contrib.sessions.models import Session	

# import logging
import datetime

# # for logging - define "error" named logging handler and logger in settings.py
# error_log=logging.getLogger('error')


class Role(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Role'
		verbose_name_plural = 'Roles'

	def __str__(self):
		return self.name

class User_View(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'User View'
		verbose_name_plural = 'User Views'

	def __str__(self):
		return self.name


class Program(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False, unique=True)	
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Program'
		verbose_name_plural = 'Programs'

	def __str__(self):
		return self.name


class CustomAccountManager(BaseUserManager):
	def create_superuser(self, email, username, password, **other_fields):
		other_fields.setdefault('is_staff', True)
		other_fields.setdefault('is_superuser', True)
		other_fields.setdefault('is_active', True)
		other_fields.setdefault('is_approved', True)
		other_fields.setdefault('is_admin', True)
		other_fields.setdefault('is_active', True)


		if other_fields.get('is_staff') is not True:
			raise ValueError('Superuser must be assigned to is_staff=True.')

		if other_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must be assigned to is_superuser=True.')

			

		return self.create_user(email, username, password, **other_fields)

	def create_user(self, email, username, password, **other_fields):

		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		email = self.normalize_email(email)
		user = self.model(email=email, username=username, **other_fields)
		user.set_password(password)
		user.save()
		return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
	first_name = models.CharField(max_length=150, null=False, blank=False)
	last_name = models.CharField(max_length=150, null=False, blank=False)
	username = models.CharField(max_length=150, unique=True)
	email = models.EmailField(verbose_name="email", max_length=80,
							unique=True, null=True, blank=True)
	roles = models.ManyToManyField(Role, related_name='user_roles', blank=True)
	programs = models.ManyToManyField(Program, related_name='user_programs', blank=True)
	is_approved = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser= models.BooleanField(default=False)
	date_joined	= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_updated = models.DateTimeField(verbose_name='last updated', auto_now=True)
	avatar_img = models.ImageField(upload_to='avatars', null=True, blank=True)
	profile_img = models.ImageField(upload_to='profile', null=True, blank=True)
	password_change_required = models.BooleanField(default=False)
	access_site_admin = models.BooleanField(default=False)
	user_view = models.ForeignKey(User_View, on_delete=models.CASCADE,
								related_name='user_view', null=True, blank=True)
	objects = CustomAccountManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

	def __str__(self):
		return self.username

	def view(self):
		reader_view = User_View.objects.get(name="Reader Only View")
		student_view = User_View.objects.get(name="Student View")
		staff_view = User_View.objects.get(name="Staff View")

		if self.user_view == reader_view:
			return "Reader View"
		elif self.user_view == student_view:
			return "Student View"
		elif self.user_view == staff_view:
			return "Staff View"

	def get_token(self):
		reader_role = Role.objects.get(name="Reader")
		student_role = Role.objects.get(name="Student")
		staff_role = Role.objects.get(name="Staff")
		vol_role = Role.objects.get(name="Volunteer")

		username = self.username
		avatar = self.avatar_img

		if staff_role in self.roles.all():			
			email = self.email
			affiliation = "owner"
			session_role = "Staff"
		else:
			affiliation = "moderator"
			if self.email:
				email = self.email
			else:
				email = ""

		if reader_role in self.roles.all():
			session_role = "Reader"
		elif student_role in self.roles.all():
			session_role = "Student"
		elif vol_role in self.roles.all():
			session_role = "Volunteer"

		return jwt_token.generate_token(username, email, affiliation, avatar, session_role)

	def main_role(self):
		reader_role = Role.objects.get(name="Reader")
		student_role = Role.objects.get(name="Student")
		staff_role = Role.objects.get(name="Staff")
		vol_role = Role.objects.get(name="Volunteer")
		if reader_role in self.roles.all():
			return "Reader"
		elif student_role in self.roles.all():
			return "Student"
		elif staff_role in self.roles.all():
			return "Staff"
		elif vol_role in self.roles.all():
			return "Volunteer"

	def has_staff_role(self):
		staff_role = Role.objects.get(name="Staff")
		staff_view = User_View.objects.get(name = "Staff View")
		if staff_role in self.roles.all() or self.user_view == staff_view:
			return True



	def scheduled_matches(self):
		reader_role = Role.objects.get(name="Reader")
		student_role = Role.objects.get(name="Student")
		if reader_role in self.roles.all():
			return self.match_reader.filter(active=True)
		elif student_role in  self.roles.all():
			return self.match_student.filter(active=True).first()

	def program_count(self):
		return self.programs.all().count() 

	def user_programs(self):
		return self.programs.all()

	def full_name(self):
		return self.first_name + " " + self.last_name

	class Meta:
		ordering = ['id']
		verbose_name = 'User'
		verbose_name_plural = 'Users'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)

@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def user_pre_delete(sender, instance, **kwargs):
	registration = None
	try:
		registration = instance.vol_user

	except Exception as e:
		try:
			registration = instance.student_user
		except Exception as e:
			try:
				registration = instance.staff_user
			except Exception as e:
				print("No Registrations") 
	if registration:
		registration.user= None
		registration.save()


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def user_delete(sender, instance, **kwargs):
	if instance.avatar_img:
		instance.avatar_img.delete(False)
	if instance.profile_img:
		instance.profile_img.delete(False)  
	


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def password_change_signal(sender, instance, **kwargs):
	print("LAST LOGIN", instance.last_login)
	print("Changed Required", instance.password_change_required)
	last_login = instance.last_login
	last_updated = instance.last_updated
	now = timezone.localtime(timezone.now())

	if instance.id is None:
		print("New User")		
	else:
		print("old user")
		if last_login:	
			print("User has logged in")
			if instance.password_change_required and last_login:
				print("Yes Required")
				user = instance
				if user:
					new_password = user.password
					print("new_password" , new_password)

				try:
					old_password = CustomUser.objects.get(id=user.id).password
					print("old_password" , old_password)
				
				except CustomUser.DoesNotExist:
					old_password = None
					print("old_password DoesNotExist" , old_password)
					instance.password_change_required = True

				if new_password != old_password:
					print("This is a new password")

					instance.password_change_required = False
				else:
					print("Password is the same")
		else:
			print("User has never logged in")

		
		


class User_Note(models.Model):
	about_user = models.ForeignKey(CustomUser, related_name="note_about",
								 on_delete=models.CASCADE, null=False, blank=False)
	note = models.CharField(max_length=255, null=False, blank=False)
	note_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='account_notes_written', null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")

	class Meta:
		ordering = ['id']
		verbose_name = 'User Note'
		verbose_name_plural = 'User Notes'

	def __str__(self):
		return str(self.note)


class User_Session(models.Model):
	user = models.ForeignKey(CustomUser, related_name="sessions",
								on_delete=models.CASCADE, null=False, blank=False)
	session = models.ForeignKey(Session, on_delete=models.CASCADE,)  

	class Meta:
		ordering = ['id']
		verbose_name = 'User Session'
		verbose_name_plural = 'User Sessions'

	def __str__(self):
		return str(self.user)



class Login_Logout_Log(models.Model):
	user = models.ForeignKey(CustomUser, related_name="log",
								on_delete=models.CASCADE, null=False, blank=False)	
	session_key = models.CharField(max_length=100, blank=False, null=False)
	host = models.CharField(max_length=100, blank=False, null=False)
	login_time = models.DateTimeField(blank=True, null=True)
	logout_time = models.DateTimeField(blank=True, null=True)
	


	class Meta:
		ordering = ['user__username']
		verbose_name = 'Login Logout Log'
		verbose_name_plural = 'Login Logout Logs'

	def __str__(self):
		return str(self.user)


class Session_Log(models.Model):
	user_session = models.ForeignKey(User_Session, related_name="django_session",
								on_delete=models.CASCADE, null=True, blank=True)
	log = models.ForeignKey(Login_Logout_Log, related_name="session_log",
								on_delete=models.CASCADE, null=True, blank=True)	

	completed_by = models.CharField(max_length=150, null=True, blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Session Log'
		verbose_name_plural = 'Session Log'

	def __str__(self):
		return str(self.user_session)

# @receiver(pre_save, sender=Login_Logout_Log)
# def session_associating(sender, instance, **kwargs):
	# print("session_associating")
	# if instance.session_key:
	# 	if User_Session.objects.filter(session__session_key = instance.session_key).exists():
	# 		print("Exists")
	# 		# instance.user_session = User_Session.objects.get(session__session_key= instance.session_key)
	# 	else:
	# 		print("DoesNotExist")

@receiver(user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
	try:
		# obj, created = User_Session.objects.get_or_create(user = user, session_id = request.session.session_key)
		# for_both= Session_Log.objects.create(user_session = obj)
		login_logout_logs = Login_Logout_Log.objects.filter(session_key=request.session.session_key, user=user.id)[:1]
		# print("login_logout_logs",login_logout_logs, type(login_logout_logs))
		# if login_logout_logs.count() > 0:
		# 	for_both.log = login_logout_logs.first()
		# 	for_both.save()

		if not login_logout_logs:
			login_logout_log = Login_Logout_Log(login_time=datetime.datetime.now(),session_key=request.session.session_key, user=user, host=request.META['HTTP_HOST'])
			login_logout_log.save()
			# for_both.log = login_logout_log
			# for_both.save()
	except Exception as e:
		print("log_user_logged_in request: %s, error: %s" % (request, e))
		# log the error
		# error_log.error("log_user_logged_in request: %s, error: %s" % (request, e))

@receiver(user_logged_out)
def log_user_logged_out(sender, user, request, **kwargs):
	try:
		obj, created = User_Session.objects.get_or_create(user = user, session_id = request.session.session_key)
		login_logout_logs = Login_Logout_Log.objects.filter(session_key=request.session.session_key, user=user.id, host=request.META['HTTP_HOST'])
		login_logout_logs.filter(logout_time__isnull=True).update(logout_time=datetime.datetime.now())
		if not login_logout_logs:
			login_logout_log = Login_Logout_Log(logout_time=datetime.datetime.now(), session_key=request.session.session_key, user=user, host=request.META['HTTP_HOST'])
			# login_logout_log.user_session = obj
			login_logout_log.save()
	except Exception as e:
		print("log_user_logged_out request: %s, error: %s" % (request, e))
		#log the error
		# error_log.error("log_user_logged_out request: %s, error: %s" % (request, e))

