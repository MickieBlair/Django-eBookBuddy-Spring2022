from django.contrib import admin
from registration.models import Volunteer_Registration
from registration.models import Student_Registration
from registration.models import Volunteer_Registration_IP_Info, Parent_Registration_IP_Info
from registration.models import Parent_Registration
from registration.models import Registration_Error
from registration.models import Volunteer_Video
from registration.models import Volunteer_Registration_Status
from registration.models import Volunteer_Registration_Note
from registration.models import Student_Registration_Status
from registration.models import Student_Registration_Note
from registration.models import Parent_Registration_Note
from registration.models import Staff_Registration, Staff_Registration_IP_Info, Staff_Registration_Note



class Staff_Registration_Admin(admin.ModelAdmin):
	list_display = ('id','date_submitted', 'user', 'first_name', 'last_name', 'fluent_spanish')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['date_submitted', 'fluent_spanish', ]
	search_fields = ('first_name', 'last_name')

	class Meta:
		model = Staff_Registration

admin.site.register(Staff_Registration, Staff_Registration_Admin)

class Staff_Registration_IP_Info_Admin(admin.ModelAdmin):
	list_display = ('registration', 'ws_connected', 'ip', 'ip_valid', 'country','city', 'date_created',)
	readonly_fields=('date_created',)
	filter_horizontal = ()
	list_filter = ['ws_connected','ip_valid', 'date_created', ]
	search_fields = ('registration__first_name', 'registration__last_name')

	class Meta:
		model = Staff_Registration_IP_Info

admin.site.register(Staff_Registration_IP_Info, Staff_Registration_IP_Info_Admin)

class Staff_Registration_Note_Admin(admin.ModelAdmin):
	list_display = ('registration','name', 'created_user', 'date_created')
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = ['date_created', 'created_user', 'registration',]

	class Meta:
		model = Staff_Registration_Note

admin.site.register(Staff_Registration_Note, Staff_Registration_Note_Admin)

class Parent_Registration_Note_Admin(admin.ModelAdmin):
	list_display = ('registration','name', 'created_user', 'date_created')
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = ['date_created', 'created_user', 'registration',]

	class Meta:
		model = Parent_Registration_Note

admin.site.register(Parent_Registration_Note, Parent_Registration_Note_Admin)

class Student_Registration_Note_Admin(admin.ModelAdmin):
	list_display = ('registration','name', 'created_user', 'date_created')
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = ['date_created', 'created_user', 'registration',]

	class Meta:
		model = Student_Registration_Note

admin.site.register(Student_Registration_Note, Student_Registration_Note_Admin)

class Student_Registration_Status_Admin(admin.ModelAdmin):
	list_display = ( 'registration', 'tech_screening', 'approved_to_match', 'approved_by', 'last_updated_by','last_updated',)
	search_fields = ()
	readonly_fields=('approved_by', 'last_updated_by', 'date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['approved_by', 'last_updated_by', ]

	class Meta:
		model = Student_Registration_Status

	def save_model(self, request, obj, form, change):
		if obj.approved_to_match:
			obj.approved_by = request.user
		obj.last_updated_by = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Student_Registration_Status, Student_Registration_Status_Admin)

class Volunteer_Registration_Note_Admin(admin.ModelAdmin):
	list_display = ('registration','name', 'created_user', 'date_created')
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = ['date_created', 'created_user', 'registration',]

	class Meta:
		model = Volunteer_Registration_Note

admin.site.register(Volunteer_Registration_Note, Volunteer_Registration_Note_Admin)


class Volunteer_Registration_Status_Admin(admin.ModelAdmin):
	list_display = ( 'registration', 'tech_screening','approved_to_match', 'approved_by', 'last_updated_by','last_updated',)
	search_fields = ()
	readonly_fields=('approved_by', 'last_updated_by', 'date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['approved_by', 'last_updated_by', ]

	class Meta:
		model = Volunteer_Registration_Status

	def save_model(self, request, obj, form, change):
		if obj.approved_to_match:
			obj.approved_by = request.user
		obj.last_updated_by = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Volunteer_Registration_Status, Volunteer_Registration_Status_Admin)

class Volunteer_Video_Admin(admin.ModelAdmin):
	list_display = ('email','date_created', 'registration',)
	readonly_fields=('date_created', )
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Volunteer_Video

admin.site.register(Volunteer_Video, Volunteer_Video_Admin)

class Registration_Error_Admin(admin.ModelAdmin):
	list_display = ('created','file', 'function_name', 'location_in_function',
					'occurred_for_user', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Registration_Error

admin.site.register(Registration_Error, Registration_Error_Admin)

class Student_Registration_Admin(admin.ModelAdmin):
	list_display = ('id', 'date_created', 'user', 'flagged', 'child_first_name', 'child_last_name', 'parent')
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = []
	search_fields = ('child_first_name', 'child_last_name',)

	class Meta:
		model = Student_Registration

admin.site.register(Student_Registration, Student_Registration_Admin)

class Parent_Registration_Admin(admin.ModelAdmin):
	list_display = ('id', 'date_created', 'user', 'flagged','parent_first_name', 'parent_last_name', 'total_children')
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = []
	search_fields = ('parent_first_name', 'parent_last_name',)

	class Meta:
		model = Parent_Registration

	def total_children(self, obj):
		count = Student_Registration.objects.filter(parent=obj).count()
		return count

admin.site.register(Parent_Registration, Parent_Registration_Admin)



class Volunteer_Registration_Admin(admin.ModelAdmin):
	list_display = ('id','date_submitted', 'user', 'flagged', 'program', 'volunteer_type', 'first_name', 'last_name',)
	readonly_fields=()
	filter_horizontal = ('meeting_times','session_choices',)
	list_filter = ['date_submitted', 'program', 'volunteer_type',]
	search_fields = ('first_name', 'last_name')

	class Meta:
		model = Volunteer_Registration

admin.site.register(Volunteer_Registration, Volunteer_Registration_Admin)

class Volunteer_Registration_IP_Info_Admin(admin.ModelAdmin):
	list_display = ('registration', 'ws_connected', 'ip', 'ip_valid', 'country','city', 'date_created',)
	readonly_fields=('date_created',)
	filter_horizontal = ()
	list_filter = ['ws_connected','ip_valid', 'date_created', ]
	search_fields = ('registration__first_name', 'registration__last_name')

	class Meta:
		model = Volunteer_Registration_IP_Info

admin.site.register(Volunteer_Registration_IP_Info, Volunteer_Registration_IP_Info_Admin)

class Parent_Registration_IP_Info_Admin(admin.ModelAdmin):
	list_display = ('registration', 'ws_connected', 'ip', 'ip_valid', 'country','city', 'date_created',)
	readonly_fields=('date_created',)
	filter_horizontal = ()
	list_filter = ['ws_connected','ip_valid', 'date_created', ]
	search_fields = ('registration__first_name', 'registration__last_name')

	class Meta:
		model = Parent_Registration_IP_Info

admin.site.register(Parent_Registration_IP_Info, Parent_Registration_IP_Info_Admin)

