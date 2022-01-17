from django.urls import path

from registration.views import (
    volunteer_registration_view,
    pre_registration_student_view,
    parent_registration_view,
    confirm_parent_registration_view,
    student_registration_view,
    confirm_student_registration_view,
    confirm_volunteer_registration_view,
    closed_volunteer_registration_view,
    closed_student_registration_view,
    confirm_video_volunteer_registration_view,
    video_volunteer_registration_view,
    registration_email_check,
    staff_registration_view,
    confirm_staff_registration_view,
    volunteer_testing_times_view,

)

app_name = 'registration'

urlpatterns = [
    path('registration_email_check/', registration_email_check, name="registration_email_check"),
    path('volunteer/closed/', closed_volunteer_registration_view, name="close_volunteer"),
    path('volunteer/testing/', volunteer_testing_times_view, name="testing_times_vol"),
    path('volunteer/video/upload/', video_volunteer_registration_view, name="upload_vol_video"),
    path('volunteer/video/submitted/<registration_id>', confirm_video_volunteer_registration_view, name="volunteer_video_confirmation"),
    path('volunteer/', volunteer_registration_view, name="volunteer_registration"),
    path('student/closed/', closed_student_registration_view, name="close_student"),
    path('student/pre_registration/', pre_registration_student_view, name="pre_registration"),
    path('program/<form_language>', parent_registration_view, name="parent_registration"),
    path('program/submitted/<form_language>/<registration_id>', confirm_parent_registration_view, name="parent_confirmation"),
    path('student/<form_language>/<parent_id>/', student_registration_view, name="student_registration"),
    path('volunteer/submitted/<registration_id>', confirm_volunteer_registration_view, name="volunteer_confirmation"),
    path('student/submitted/<form_language>/<parent_id>/', confirm_student_registration_view, name="student_confirmation"),
    path('staff/submitted/<registration_id>', confirm_staff_registration_view, name="staff_confirmation"),
    path('staff/', staff_registration_view, name="staff_registration"),
]


