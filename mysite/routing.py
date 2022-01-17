from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from django.core.asgi import get_asgi_application

from registration.registration_consumer import RegistrationConsumer
from jitsi_data.consumer_jitsi_data import JitsiDataConsumer
from staff_chat.consumer_staff_chat import StaffChatConsumer
from reading_sessions.consumer_reading_session import ReadingSessionConsumer
from private_chat.consumer_private_chat import PrivateChatConsumer

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('registration/', RegistrationConsumer.as_asgi()),
					path('jitsi_data/', JitsiDataConsumer.as_asgi()),
					path('staff_chat/<room_id>/', StaffChatConsumer.as_asgi()),
					path('status/', ReadingSessionConsumer.as_asgi()),
					path('private_chat/<room_id>/', PrivateChatConsumer.as_asgi()),
					# path('match/<location_id>/', MatchConsumer.as_asgi()),
					# path('jitsi_chat/<room_id>/', PublicChatConsumer.as_asgi()),					
					# 
					# path('echo/', EchoConsumer.as_asgi()),
					
			])
		)
	),
})


