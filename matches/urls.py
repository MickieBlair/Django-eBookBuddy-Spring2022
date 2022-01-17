from django.urls import path

from matches.views import (
    create_scheduled_match_view,
    display_scheduled_matches_view,
    display_temporary_matches_view,
)

app_name = 'matches'

urlpatterns = [
    path('create_match/', create_scheduled_match_view, name="create_match"),
    path('scheduled/<match_type>/', display_scheduled_matches_view, name="view_scheduled"),
    path('temporary/<match_type>/', display_temporary_matches_view, name="view_temporary"),
 
]


