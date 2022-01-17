from django.contrib import admin
from reading_sessions.models import User_Session_Status, Match_Status_Option
from reading_sessions.models import Match_Session_Status
from users.models import Role
from reading_sessions.models import Redirect
from reading_sessions.models import Help_Request
from reading_sessions.models import Reading_Session_Error
from reading_sessions.models import Room_Participants

# Register your models here.

class Room_Participants_Admin(admin.ModelAdmin):
	list_display = ('room', 'ws_count', 'occupied_ws', 'jitsi_count', 'occupied_jitsi')
	readonly_fields=()
	filter_horizontal = ('jitsi_users', 'ws_users')
	list_filter = ['occupied_ws', 'occupied_jitsi', 'room', ]

	class Meta:
		model = Room_Participants

admin.site.register(Room_Participants, Room_Participants_Admin)

class Redirect_Admin(admin.ModelAdmin):
	list_display = ('user_to_redirect', 'to_room', 'redirect_url',
					'auto_send','created_by')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['created_by', 'user_to_redirect',]

	class Meta:
		model = Redirect

admin.site.register(Redirect, Redirect_Admin)

class Help_Request_Admin(admin.ModelAdmin):
    list_display = [ 'from_user', 'from_room', 'room_url', 'created' , 'done']
    search_fields = [ ]
    readonly_fields = ['room_url', 'created' ]

    class Meta:
        model = Help_Request

admin.site.register(Help_Request, Help_Request_Admin)  

class Reading_Session_Error_Admin(admin.ModelAdmin):
	list_display = ('created','file', 'function_name', 'location_in_function',
					'occurred_for_user', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Reading_Session_Error

admin.site.register(Reading_Session_Error, Reading_Session_Error_Admin)

class Match_Session_Status_Admin(admin.ModelAdmin):
	list_display = ('id','session', 'type', 'match', 'match_status_active', 'student_online', 'reader_online', 'member_reassigned',
						'reader_reassigned', 'student_reassigned', 'status', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['session__date','session__day_time', 'session','match_type',
				 'match_status_active', 'sch_match', 'temp_match', ]
	search_fields = ('sch_match__student__first_name', 'sch_match__student__last_name',
					'sch_match__reader__first_name', 'sch_match__reader__last_name')
	
	class Meta:
		model = Match_Session_Status

	def type(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.match_type.short_name			
		else:
			if obj.match_type.name == "Temporary - In Session":
				return obj.match_type.short_name

	def match(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.sch_match			
		else:
			if obj.match_type.name == "Temporary - In Session":
				return obj.temp_match

admin.site.register(Match_Session_Status, Match_Session_Status_Admin)


class User_Session_Status_Admin(admin.ModelAdmin):
	list_display = ('id','user', 'full_name','all_connected','online_jitsi','online_ws' ,'room','room_jitsi',
					'current_active_match_type','active_buddy','needs_new_buddy',
					'manual_redirect_on','roles', 
					 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('scheduled_matches', 'buddies')
	list_filter = ['all_connected','online_jitsi','online_ws','on_landing_page','room','manual_redirect_on','needs_new_buddy',
				 'current_active_match_type', 'user__roles',]
	search_fields = ('user__full_name', 'user__username')

	class Meta:
		model = User_Session_Status

	def full_name(self, obj):		
		return obj.user.full_name()

	def roles(self, obj):
		return ", ".join([
			role.name for role in obj.user.roles.all()
			])
	def buddy(self, obj):

		if obj.scheduled_match:

			student_role = Role.objects.get(name = "Student")
			reader_role = Role.objects.get(name = "Reader")
			print(student_role, reader_role)
			if student_role in obj.user.roles.all():
				print("GETTING BUDDY STUDENT")
				return obj.scheduled_match.reader.full_name()
			elif reader_role in obj.user.roles.all():
				print("GETTING BUDDY Reader")
				return obj.scheduled_match.student.full_name()
		else:
			return "None"

admin.site.register(User_Session_Status, User_Session_Status_Admin)