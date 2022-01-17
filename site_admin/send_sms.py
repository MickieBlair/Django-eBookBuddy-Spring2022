# Download the helper library from https://www.twilio.com/docs/python/install
from django.conf import settings
from twilio.rest import Client

ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
FROM_NUMBER = settings.TWILIO_SMS_NUMBER

def send_text_message(to_number, body):
     client = Client(ACCOUNT_SID, AUTH_TOKEN)
     message = client.messages.create(
          to=to_number,
          from_=FROM_NUMBER,
          body=body)

     print(message.sid)

# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+14703033217", 
#     from_=from_number,
#     body="Hello from Python!")

# print(message.sid)








