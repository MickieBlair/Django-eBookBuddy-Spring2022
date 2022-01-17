from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role
from .models import CustomUser
from .models import Program
from .models import User_View
from .models import User_Note
from .models import Login_Logout_Log, User_Session
from .models import Session_Log

# Register your models here. ,

class Session_Log_Admin(admin.ModelAdmin):
	list_display = ('id','user_session', 'log',)
	search_fields = ('user_session__user__username',
					 'user_session__user__first_name',
					 'user_session__user__last_name')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ( 'user_session__user', )

	class Meta:
		model = Session_Log

admin.site.register(Session_Log, Session_Log_Admin)

class User_Session_Admin(admin.ModelAdmin):
	list_display = ('user', 'session',)
	search_fields = ('user__username', 'user__first_name', 'user__last_name')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ( 'user', )

	class Meta:
		model = User_Session

admin.site.register(User_Session, User_Session_Admin)

class Login_Logout_Log_Admin(admin.ModelAdmin):
	list_display = ('user', 'login_time', 'logout_time', 'session_key', 'host')
	search_fields = ('user__username', 'user__first_name', 'user__last_name')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ('login_time', 'user', )

	class Meta:
		model = Login_Logout_Log

admin.site.register(Login_Logout_Log, Login_Logout_Log_Admin)

class User_Note_Admin(admin.ModelAdmin):
	list_display = ('about_user', 'note', 'note_by', 'date_created')
	search_fields = ('note',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ('date_created', 'note_by', )

	class Meta:
		model = User_Note

admin.site.register(User_Note, User_Note_Admin)



class User_View_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()


	class Meta:
		model = User_View

admin.site.register(User_View, User_View_Admin)

class Role_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Role

admin.site.register(Role, Role_Admin)

class Program_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Program

admin.site.register(Program, Program_Admin)


class CustomUser_Admin(UserAdmin):
	list_display = ('id', 'username','full_name','user_view', 'password_change_required', 'program_list', 'is_approved',
					'roles_list', 'email', 'is_admin','is_staff')
	search_fields = ('id', 'email', 'username', 'role__name', 'first_name', 'last_name',)
	readonly_fields=('id', 'date_joined', 'last_updated')

	filter_horizontal = ('programs', 'roles',)
	list_filter = ('roles','is_approved',)
	fieldsets = ()

	class Meta:
		model = CustomUser

	def full_name(self, obj):		
		return obj.full_name()
		

	def program_list(self, obj):
		program_list = ""
		if obj.programs.all().count() == 0:
			program_list = "None"
			return program_list
		else:
			return ", ".join([
			program.name for program in obj.programs.all()
			])

	

	def roles_list(self, obj):
		return ", ".join([
			role.name for role in obj.roles.all()
			])
	roles_list.short_description = "Roles"
	program_list.short_description = "Programs"
	

admin.site.register(CustomUser, CustomUser_Admin)