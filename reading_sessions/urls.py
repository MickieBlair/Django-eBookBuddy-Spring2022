from django.urls import path

from reading_sessions.views import (
    reading_sessions_home,
    room_view,
    session_end_view,
    staff_reset_count,
    initial_entry_view,
    tech_testing_room_view,
    not_found_view,

    #help_requests,
    create_help_request,
    ajax_help_mark_as_done,

    #ajax status
    ajax_check_user_status,

    #ajax private messages
    ajax_get_private_chats,
    ajax_get_private_room,
)

app_name = 'reading_sessions'

urlpatterns = [
    path('home/', reading_sessions_home, name="sessions_home"),
    path('error/', not_found_view, name="not_found"),
    path('initial_entry', initial_entry_view, name="initial_entry"),
    path('volunteer_testing/<registration_id>/', tech_testing_room_view, name="volunteer_testing"),
    path('room/<room_slug>/', room_view, name="room"),
    path('session_end/', session_end_view, name="session_end"),
    path('ajax_staff_reset_count/', staff_reset_count, name="staff_reset_count"),

    #ajax help requests
    path('create_help_request/', create_help_request, name="create_help_request"),    
    path('ajax_help_mark_as_done/', ajax_help_mark_as_done, name="ajax_help_mark_as_done"),  

    #ajax status
    path('ajax_status/', ajax_check_user_status, name="ajax_status"),

    #ajax status
    path('ajax_get_private_chats/', ajax_get_private_chats, name="ajax_get_private_chats"),

    #ajax private chat
    path('ajax_private_chat/', ajax_get_private_room, name='ajax_get_private_room'),

 
]


