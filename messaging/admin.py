from django.contrib import admin
from messaging.models import Incoming_Message

# Register your models here.
class Incoming_Message_Admin(admin.ModelAdmin):
	list_display = ('name', 'created',)
	search_fields = ('name',)
	readonly_fields=('created', 'id')
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Incoming_Message

admin.site.register(Incoming_Message, Incoming_Message_Admin)