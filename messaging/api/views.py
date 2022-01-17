from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response

from messaging.models import Incoming_Message
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse

import json

@api_view(['POST', ])
@csrf_exempt
def api_incoming(request):
	if request.method == 'POST':
		data = request.data
		print("data", data)
		Incoming_Message.objects.create(
			name='Incoming',
			text=data,
			)


		return Response(data="OK", status=status.HTTP_200_OK)

