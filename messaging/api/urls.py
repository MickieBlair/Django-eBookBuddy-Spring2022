from django.urls import path
from messaging.api.views import(
	api_incoming,
)

app_name = 'messaging'

urlpatterns = [
	path('incoming', api_incoming, name="incoming"),
]