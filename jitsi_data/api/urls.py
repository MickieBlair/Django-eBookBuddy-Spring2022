from django.urls import path
from jitsi_data.api.views import(
	api_jitsi_user_status_view,
	api_create_jitsi_event_view,
	api_occupant_joined_view,
	api_occupant_left_view,
	api_room_created_view,
	api_room_destroyed_view,

	

)

app_name = 'jitsi_data'

urlpatterns = [
	path('<display_name>/', api_jitsi_user_status_view, name="display_name"),
	path('create_event', api_create_jitsi_event_view, name="create_event"),
	path('meeting_events/occupant/joined', api_occupant_joined_view, name="occupant_joined"),
	path('meeting_events/occupant/left', api_occupant_left_view, name="occupant_left"),
	path('meeting_events/room/created', api_room_created_view, name="room_created"),
	path('meeting_events/room/destroyed', api_room_destroyed_view, name="room_destroyed"),
]