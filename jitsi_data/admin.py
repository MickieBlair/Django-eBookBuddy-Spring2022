from django.contrib import admin
from jitsi_data.models import Jitsi_User_Event
from jitsi_data.models import Jitsi_User_Status
from jitsi_data.models import Jitsi_Data_Websocket_Error
from jitsi_data.models import Jitsi_Room_Occupant, Jitsi_Room

class Jitsi_Room_Admin(admin.ModelAdmin):
	list_display = ('instance_created', 'room_name', 'room', 'event_name', 'created_at',
					'destroyed_at', )
	search_fields = ('name',)
	readonly_fields=('instance_created', 'id')
	filter_horizontal = ()
	list_filter = ['instance_created', 'room_name',  'room' ]

	class Meta:
		model = Jitsi_Room

admin.site.register(Jitsi_Room, Jitsi_Room_Admin)

class Jitsi_Room_Occupant_Admin(admin.ModelAdmin):
	list_display = ('instance_created', 'jitsi_room', 'name', 'user', 'jitsi_id', 'joined_at',
					'left_at', 'total_time')
	search_fields = ('name',)
	readonly_fields=('instance_created', 'id')
	filter_horizontal = ()
	list_filter = ['instance_created', 'name',  'user' ]

	class Meta:
		model = Jitsi_Room_Occupant

admin.site.register(Jitsi_Room_Occupant, Jitsi_Room_Occupant_Admin)

class Jitsi_User_Event_Admin(admin.ModelAdmin):
	list_display = ('user', 'room', 'occupant_name', 'in_room', 'total_time', 'event_name',)
	search_fields = ('occupant_name',)
	readonly_fields=('instance_created','instance_updated', 'id')
	filter_horizontal = ()
	list_filter = ['in_room', 'instance_created', 'occupant_name','instance_updated', 'event_name', 'user']

	class Meta:
		model = Jitsi_User_Event

admin.site.register(Jitsi_User_Event, Jitsi_User_Event_Admin)

class Jitsi_User_Status_Admin(admin.ModelAdmin):
	list_display = ('user', 'online', 'date_created', 'last_updated' )
	search_fields = ('user__username', 'user__first_name', 'user__last_name')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['online','last_updated', 'date_created', 'user']

	class Meta:
		model = Jitsi_User_Status

admin.site.register(Jitsi_User_Status, Jitsi_User_Status_Admin)

class Jitsi_Data_Websocket_Error_Admin(admin.ModelAdmin):
	list_display = ('created','file', 'function_name', 'location_in_function',
					'occurred_for_user', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Jitsi_Data_Websocket_Error

admin.site.register(Jitsi_Data_Websocket_Error, Jitsi_Data_Websocket_Error_Admin)
