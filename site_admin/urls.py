from django.urls import path

from site_admin.views import (
	site_admin_home_view,

	#registrations
	registrations_staff_view,
	registrations_volunteers_view,
	volunteer_status_application_view,
	registrations_students_view,
	student_status_application_view,
	download_volunteer_registrations_csv,
	download_student_registrations_csv,
	staff_status_application_view,
	server_times_view,
	send_volunteer_user_info_view,
	registrations_parents_view,

	#users
	create_any_user_view,
	registration_create_student_user_view,
	registration_create_volunteer_user_view,
	registration_create_staff_user_view,
	display_users_view,
	edit_user_view,

	#superuser
	display_login_logout_logs_view,

	send_parent_email,
	whatsapp_email,
	video_reminder_view,

	#teams
	create_user_team_info_view,
	mega_teams_view,
	edit_mega_teams_view,
	edit_team_view,

)

from matches.views import (
    create_scheduled_match_view,
    edit_scheduled_match_view,
    display_scheduled_matches_view,
    display_temporary_matches_view,
    display_match_sessions_view,
    deactivate_scheduled_match_view,
    display_match_notes_view,
)

app_name = 'site_admin'

urlpatterns = [
	path('home/', site_admin_home_view, name="admin_home"),

	#registrations
	path('registrations/parents/<search_title>', registrations_parents_view, name="registrations_parents"),
	path('registrations/parents/email_link/<registration_id>', send_parent_email, name="email_parent"),
	path('registrations/parents/whatsapp_email/<registration_id>', whatsapp_email, name="whatsapp_email"),

	path('registrations/volunteers/review/<registration_id>', volunteer_status_application_view, name="volunteer_review"),
	path('registrations/volunteers/download', download_volunteer_registrations_csv, name="download_registrations_volunteers"),
	path('registrations/volunteers/<search_title>', registrations_volunteers_view, name="registrations_volunteers"),
	path('registrations/volunteers/email_server_times/<registration_id>', server_times_view, name="server_times"),
	path('registrations/volunteers/user_info/<registration_id>', send_volunteer_user_info_view, name="user_info"),
	path('registrations/volunteers/video_reminder/<registration_id>', video_reminder_view, name="video_reminder"),

	path('registrations/students/review/<registration_id>', student_status_application_view, name="student_review"),
	path('registrations/students/download', download_student_registrations_csv, name="download_registrations_studentss"),
	path('registrations/students/<search_title>', registrations_students_view, name="registrations_students"),
	
	path('registrations/staff/review/<registration_id>', staff_status_application_view, name="staff_review"),
	path('registrations/staff/<search_title>', registrations_staff_view, name="registrations_staff"),
	
	#users
	
	path('users/view/<role>/', display_users_view, name="view_users"),
	path('users/team/create/<user_id>/', create_user_team_info_view, name="team_info"),
	path('users/update/<user_id>/', edit_user_view, name="edit_user"),
	path('users/create/student/<registration_id>/', registration_create_student_user_view, name="create_student"),
	path('users/create/volunteer/<registration_id>/', registration_create_volunteer_user_view, name="create_volunteer"),
	path('users/create/staff/<registration_id>/', registration_create_staff_user_view, name="create_staff"),
	path('users/create/', create_any_user_view, name="create_user"),

	#user_info
	path('user_info/sessions/<search_title>', display_login_logout_logs_view, name="login_logout"),
	

	#matches
	path('match/notes/<match_id>/', display_match_notes_view, name="match_notes"),
	path('match/sessions/<match_id>/', display_match_sessions_view, name="match_sessions"),
	path('matches/create_match/', create_scheduled_match_view, name="create_match"),
	path('matches/edit_match/<match_id>/', edit_scheduled_match_view, name="edit_match"),
    path('matches/scheduled/<match_type>/', display_scheduled_matches_view, name="view_scheduled"),
    path('matches/temporary/<match_type>/', display_temporary_matches_view, name="view_temporary"),
    path('matches/set_inactive/<match_id>/', deactivate_scheduled_match_view, name="set_inactive"),

    #teams    
    path('teams/mega_teams/', mega_teams_view, name="mega_teams"),
    path('teams/mega_team/edit/<mega_id>/', edit_mega_teams_view, name="edit_mega"),
    path('teams/team/edit/<team_id>/', edit_team_view, name="edit_team"),
    


]