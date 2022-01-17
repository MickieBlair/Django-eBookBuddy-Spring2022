from django.contrib import admin
from .models import Program_Status, Program_Form, Answer_Type, Question
from .models import Program_Semester, Gender, Ethnicity, Day
from .models import Current_Education_Level, Current_Education_Class
from .models import Team_Meeting_Time, Session_Meeting_Option
from .models import Session_Day_Option, Session_Time_Option
from .models import Opportunity_Source, Social_Media_Source, Web_Source
from .models import Device_Type, Volunteer_Opportunity, Volunteer_Reason
from .models import Form_Message, Application_Recipient, Language
from .models import Grade, School, Message_App, Reading_Description
from .models import Parent_Additional_Information, Student_Characteristic
from .models import Room_Type, Room, Response_Flag
from .models import Server_Time, Server_Schedule
from .models import Reading_Session_Day_Time, Day_With_Daily_Session
from .models import Daily_Session
from .models import Mega_Team, Team, Team_Meeting
from .models import Day_With_Team_Meeting, Day_With_Orientation_Meeting

class Day_With_Orientation_Meeting_Admin(admin.ModelAdmin):
	list_display = ('date', 'time_start', 'time_end')
	readonly_fields=()
	filter_horizontal = ('allowed_participants',)
	list_filter = [ 'date', ]
	search_fields = ()

	class Meta:
		model = Day_With_Orientation_Meeting

admin.site.register(Day_With_Orientation_Meeting, Day_With_Orientation_Meeting_Admin)

class Day_With_Team_Meeting_Admin(admin.ModelAdmin):
	list_display = ('semester', 'date', 'day', 'server_on', 'server_off', 'count' )
	readonly_fields=()
	filter_horizontal = ('day_meetings', )
	list_filter = [ 'day', ]
	search_fields = ()

	class Meta:
		model = Day_With_Team_Meeting

admin.site.register(Day_With_Team_Meeting, Day_With_Team_Meeting_Admin)

class Team_Meeting_Admin(admin.ModelAdmin):
	list_display = ('team', 'day', 'time_start', 'time_end')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['team', 'day', ]
	search_fields = ('team__name',)

	class Meta:
		model = Team_Meeting

admin.site.register(Team_Meeting, Team_Meeting_Admin)

class Mega_Team_Admin(admin.ModelAdmin):
	list_display = ('name', 'coordinator','date_created', 'last_updated',)
	search_fields = ()
	readonly_fields=('date_created', 'last_updated',)
	filter_horizontal = ('team_leaders', 'volunteers')
	list_filter = ('coordinator', )
	fieldsets = ()

	class Meta:
		model = Mega_Team

admin.site.register(Mega_Team, Mega_Team_Admin)

class Team_Admin(admin.ModelAdmin):
	list_display = ('name', 'mega', 'leader','meeting_day_time', 'room', 'date_created', 'last_updated',)
	search_fields = ()
	readonly_fields=('date_created', 'last_updated',)
	filter_horizontal = ('volunteers',)
	list_filter = ('mega', 'leader', )
	fieldsets = ()

	class Meta:
		model = Team

admin.site.register(Team, Team_Admin)

class Daily_Session_Admin(admin.ModelAdmin):
	list_display = ('date', 'day_time','session_start_date_time',
					'session_end_date_time', 'student_entry_allowed_start',
					'student_entry_allowed_end', 'week', 'session_complete', 'semester',)
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['date', 'day_time', ]

	class Meta:
		model = Day_With_Daily_Session

admin.site.register(Daily_Session, Daily_Session_Admin)

class Day_With_Daily_Session_Admin(admin.ModelAdmin):
	list_display = ('date', 'day','week', 'semester',)
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['date', 'day', ]

	class Meta:
		model = Day_With_Daily_Session

admin.site.register(Day_With_Daily_Session, Day_With_Daily_Session_Admin)

class Reading_Session_Day_Time_Admin(admin.ModelAdmin):
	list_display = ('day', 'time_start', 'time_end', 'session_slot', 'active',)
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active', 'day', ]

	class Meta:
		model = Reading_Session_Day_Time

admin.site.register(Reading_Session_Day_Time, Reading_Session_Day_Time_Admin)

class Server_Schedule_Admin(admin.ModelAdmin):
	list_display = ('name', 'active', 'offset', 'times_list')
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Server_Schedule

	def times_list(self, obj):
		return ", ".join([
			time.name for time in obj.schedule.all()
			])

admin.site.register(Server_Schedule, Server_Schedule_Admin)

class Server_Time_Admin(admin.ModelAdmin):
	list_display = ('server_schedule', 'name', 'day', 'start_time', 'end_time',
					 'date', 'date_created', 'last_updated')
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['day', ]

	class Meta:
		model = Server_Time

admin.site.register(Server_Time, Server_Time_Admin)

class Response_Flag_Admin(admin.ModelAdmin):
	list_display = ('on_question', 'flag_condition', 'active')
	search_fields = ('flag_condition', 'comment', )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active', 'on_question']

	class Meta:
		model = Response_Flag

admin.site.register(Response_Flag, Response_Flag_Admin)

class Room_Admin(admin.ModelAdmin):
	list_display = ('name', 'number', 'room_type', 'slug','show_in_session_list', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active', 'show_in_session_list']

	class Meta:
		model = Room

admin.site.register(Room, Room_Admin)

class Room_Type_Admin(admin.ModelAdmin):
	list_display = ('name', 'letter', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Room_Type

admin.site.register(Room_Type, Room_Type_Admin)


class Student_Characteristic_Admin(admin.ModelAdmin):
	list_display = ('name', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Student_Characteristic

admin.site.register(Student_Characteristic, Student_Characteristic_Admin)

class Reading_Description_Admin(admin.ModelAdmin):
	list_display = ('name', 'eng_text','span_text', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Reading_Description

admin.site.register(Reading_Description, Reading_Description_Admin)

class Message_App_Admin(admin.ModelAdmin):
	list_display = ('name', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Message_App

admin.site.register(Message_App, Message_App_Admin)

class Parent_Additional_Information_Admin(admin.ModelAdmin):
	list_display = ('name', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Parent_Additional_Information

admin.site.register(Parent_Additional_Information, Parent_Additional_Information_Admin)

class School_Admin(admin.ModelAdmin):
	list_display = ('name', 'display_in_list', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = School

admin.site.register(School, School_Admin)

class Grade_Admin(admin.ModelAdmin):
	list_display = ('abbr', 'eng_name', 'span_name', 'active')
	search_fields = ( )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Grade

admin.site.register(Grade, Grade_Admin)

class Language_Admin(admin.ModelAdmin):
	list_display = ( 'iso', 'eng_name', 'span_name','active')
	search_fields = ( )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Language

admin.site.register(Language, Language_Admin)

class Form_Message_Admin(admin.ModelAdmin):
	list_display = ( 'name', 'active', 'for_form', 'created_by','date_created', 'last_updated_by', 'last_updated')
	search_fields = ( 'name', 'for_form__name', 'message_content')
	readonly_fields=('last_updated_by', 'date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['active', 'for_form', ]

	class Meta:
		model = Form_Message

	def save_model(self, request, obj, form, change):
		obj.last_updated_by = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Form_Message, Form_Message_Admin)

class Application_Recipient_Admin(admin.ModelAdmin):
	list_display = ( 'recipient', 'active', 'receive_student', 'receive_vol','date_created', 'last_updated')
	search_fields = ( )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['recipient', 'active',]

	class Meta:
		model = Application_Recipient

admin.site.register(Application_Recipient, Application_Recipient_Admin)

class Volunteer_Reason_Admin(admin.ModelAdmin):
	list_display = ('name', 'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Volunteer_Reason

admin.site.register(Volunteer_Reason, Volunteer_Reason_Admin)

class Volunteer_Opportunity_Admin(admin.ModelAdmin):
	list_display = ('name',  'active')
	search_fields = ('name',  'active')
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Volunteer_Opportunity

admin.site.register(Volunteer_Opportunity, Volunteer_Opportunity_Admin)

class Device_Type_Admin(admin.ModelAdmin):
	list_display = ('name',  'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Device_Type

admin.site.register(Device_Type, Device_Type_Admin)

class Opportunity_Source_Admin(admin.ModelAdmin):
	list_display = ('name',  'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Opportunity_Source

admin.site.register(Opportunity_Source, Opportunity_Source_Admin)

class Social_Media_Source_Admin(admin.ModelAdmin):
	list_display = ('name',  'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Social_Media_Source

admin.site.register(Social_Media_Source, Social_Media_Source_Admin)

class Web_Source_Admin(admin.ModelAdmin):
	list_display = ('name',  'active')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Web_Source

admin.site.register(Web_Source, Web_Source_Admin)

class Session_Meeting_Option_Admin(admin.ModelAdmin):
	list_display = ( 'active', 'day_option', 'time_option', 'sessions', 'slot_letter')
	search_fields = ( )
	readonly_fields=()
	filter_horizontal = ('session_day_times', )
	list_filter = ['active',]

	class Meta:
		model = Session_Meeting_Option

	def sessions(self, obj):
		return ", ".join([
			slot.get_short_name() for slot in obj.session_day_times.all()
			])

admin.site.register(Session_Meeting_Option, Session_Meeting_Option_Admin)

class Session_Time_Option_Admin(admin.ModelAdmin):
	list_display = ( 'active', 'start_time', 'end_time', 'timezone')
	search_fields = ( )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['active',]

	class Meta:
		model = Session_Time_Option

admin.site.register(Session_Time_Option, Session_Time_Option_Admin)

class Session_Day_Option_Admin(admin.ModelAdmin):
	list_display = ( 'name', 'active',)
	search_fields = ('name', )
	readonly_fields=()
	filter_horizontal = ('days',)
	list_filter = []

	class Meta:
		model = Session_Day_Option

admin.site.register(Session_Day_Option, Session_Day_Option_Admin)

class Program_Form_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Program_Form

admin.site.register(Program_Form, Program_Form_Admin)

class Answer_Type_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Answer_Type

admin.site.register(Answer_Type, Answer_Type_Admin)

class Question_Admin(admin.ModelAdmin):
	list_display = ( 'for_form', 'field_name','question_number', 'required', 'answer_type',)
	search_fields = ('field_name', 'eng_text', 'span_text')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = [ 'for_form', 'field_name', 'answer_type']

	class Meta:
		model = Question

admin.site.register(Question, Question_Admin)


class Program_Status_Admin(admin.ModelAdmin):
	list_display = ('program','updating',  )
	search_fields = ('program__name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Program_Status

admin.site.register(Program_Status, Program_Status_Admin)

class Program_Semester_Admin(admin.ModelAdmin):
	list_display = ('program', 'name', 'active_semester', 'start_date', 'end_date',
					'accepting_students','accepting_volunteers')
	search_fields = ('program__name', 'name')
	readonly_fields=()
	filter_horizontal = ('days', 'day_time_slots')
	list_filter = ['program',]

	class Meta:
		model = Program_Semester

admin.site.register(Program_Semester, Program_Semester_Admin)

class Gender_Admin(admin.ModelAdmin):
	list_display = ('letter', 'name', 'for_users', 'eng_gender', 'span_gender')
	search_fields = ('eng_gender', 'span_gender', )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Gender

admin.site.register(Gender, Gender_Admin)

class Ethnicity_Admin(admin.ModelAdmin):
	list_display = ('eng_option', 'span_option')
	search_fields = ('eng_option', 'span_option', )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Ethnicity

admin.site.register(Ethnicity, Ethnicity_Admin)

class Current_Education_Level_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Current_Education_Level

admin.site.register(Current_Education_Level, Current_Education_Level_Admin)

class Current_Education_Class_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Current_Education_Class

admin.site.register(Current_Education_Class, Current_Education_Class_Admin)

class Day_Admin(admin.ModelAdmin):
	list_display = ('number', 'name','letter',  'span_name', 'short_name' )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Day

admin.site.register(Day, Day_Admin)

class Team_Meeting_Time_Admin(admin.ModelAdmin):
	list_display = ('meeting_day', 'meeting_time', 'timezone', 'active')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['meeting_day',]

	class Meta:
		model = Team_Meeting_Time

admin.site.register(Team_Meeting_Time, Team_Meeting_Time_Admin)