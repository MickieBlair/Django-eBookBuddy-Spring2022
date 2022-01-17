from django.contrib import admin
from matches.models import Student_Match_Profile, Reader_Match_Profile
from matches.models import Scheduled_Match, Match_Note
from matches.models import Temporary_Match, Match_Status_Option
from matches.models import Match_Type, Match_Attendance_Record
from users.models import Role, CustomUser
# Register your models here.

class Match_Attendance_Record_Admin(admin.ModelAdmin):
	list_display = ('id','session', 'type', 'match', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['session__date','session__day_time', 'session','match_type',
				'sch_match', 'temp_match__match_type', 'temp_match', ]
	search_fields = ('sch_match__student__first_name', 'sch_match__student__last_name',
					 'sch_match__reader__first_name', 'sch_match__reader__last_name',
					 'sch_match__reader__username', 'sch_match__student__username',)
	
	class Meta:
		model = Match_Attendance_Record

	def type(self, obj):
		return obj.match_type.short_name			

	def match(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.sch_match			
		else:
			if obj.match_type.name == "Temporary - In Session":
				return obj.temp_match

admin.site.register(Match_Attendance_Record, Match_Attendance_Record_Admin)

class Match_Status_Option_Admin(admin.ModelAdmin):
	list_display = ('name', )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []
	search_fields = ()
	class Meta:
		model = Match_Status_Option

admin.site.register(Match_Status_Option, Match_Status_Option_Admin)

class Match_Type_Admin(admin.ModelAdmin):
	list_display = ('name', 'short_name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Match_Type

admin.site.register(Match_Type, Match_Type_Admin)

class Temporary_Match_Admin(admin.ModelAdmin):
	list_display = ('match_type','session', 'active',  'student', 'reader','semester', 'date_created', 'last_updated',)
	search_fields = ('student__first_name', 'student__last_name', 'student__username',
					'reader__first_name', 'reader__last_name', 'reader__username',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('notes',)
	list_filter = ['active','session', 'student', 'reader', 'semester', ]

	class Meta:
		model = Temporary_Match


	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "student":
			student_role = Role.objects.get(name="Student")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[student_role])

		if db_field.name == "reader":
			reader_role = Role.objects.get(name="Reader")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[reader_role])
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Temporary_Match, Temporary_Match_Admin)

class Match_Note_Admin(admin.ModelAdmin):
	list_display = ('match_type','name', 'created_user', 'date_created')
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = ['match_type', 'date_created', 'created_user',]

	class Meta:
		model = Match_Note

admin.site.register(Match_Note, Match_Note_Admin)

class Scheduled_Match_Admin(admin.ModelAdmin):
	list_display = ('match_type','active', 'student', 'reader','day_times', 'semester', 'date_created', 'last_updated',)
	search_fields = ('student__first_name', 'student__last_name', 'student__username',
					'reader__first_name', 'reader__last_name', 'reader__username',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('sessions_scheduled',)
	list_filter = ['active', 'day_times', 'student', 'reader', 'semester', ]

	class Meta:
		model = Scheduled_Match


	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "student":
			student_role = Role.objects.get(name="Student")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[student_role])

		if db_field.name == "reader":
			reader_role = Role.objects.get(name="Reader")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[reader_role])
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Scheduled_Match, Scheduled_Match_Admin)

class Student_Match_Profile_Admin(admin.ModelAdmin):
	list_display = ('user', 'buddy', 'match_needed','count', 'semester', 'date_created', 'last_updated',)
	search_fields = ()
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('scheduled_slots',)
	list_filter = ['match_needed', 'user', 'semester', ]

	class Meta:
		model = Student_Match_Profile

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "user":
			student_role = Role.objects.get(name="Student")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[student_role])
		if db_field.name == "buddy":
			reader_role = Role.objects.get(name="Reader")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[reader_role])
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def count(self, obj):
		return obj.scheduled_slots.all().count()			
	
admin.site.register(Student_Match_Profile, Student_Match_Profile_Admin)

class Reader_Match_Profile_Admin(admin.ModelAdmin):
	list_display = ('user', 'match_count','matches', 'open_slot_count','scheduled_slot_count', 'semester', 'date_created', 'last_updated',)
	search_fields = ()
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('open_slots','scheduled_slots', 'buddies')
	list_filter = ['match_count', 'user', 'semester', ]

	class Meta:
		model = Reader_Match_Profile

	def matches(self, obj):
		return ", ".join([
			user.username for user in obj.buddies.all()
			])

	def open(self, obj):
		return ", ".join([
			slot.get_short_name() for slot in obj.open_slots.all()
			])

	def scheduled(self, obj):
		return ", ".join([
			slot.get_short_name() for slot in obj.scheduled_slots.all()
			])

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "user":
			reader_role = Role.objects.get(name="Reader")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[reader_role])

		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "buddies":
			student_role = Role.objects.get(name="Student")
			kwargs["queryset"] = CustomUser.objects.filter(roles__in=[student_role])
		return super(Reader_Match_Profile_Admin, self).formfield_for_manytomany(db_field, request, **kwargs)
		


admin.site.register(Reader_Match_Profile, Reader_Match_Profile_Admin)