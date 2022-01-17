from django.contrib import admin
from django.db import models
from django.core.paginator import Paginator
from django.core.cache import cache
from staff_chat.models import Staff_Chat_Error
from staff_chat.models import Staff_Chat_Room
from staff_chat.models import Staff_Room_Chat_Message
from staff_chat.models import Staff_Room_Unread_Chat_Message

class Staff_Chat_Error_Admin(admin.ModelAdmin):
	list_display = ('file', 'function_name', 'location_in_function',
					'occurred_for_user','created', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Staff_Chat_Error

admin.site.register(Staff_Chat_Error, Staff_Chat_Error_Admin)

class Staff_Room_Unread_Chat_Message_Admin(admin.ModelAdmin):
	list_display = ['user','room', 'unread_count', 'date_created', "last_updated"]
	search_fields = ['user', ]
	readonly_fields = ['date_created', 'last_updated']
	list_filter = ['user', 'room',]

	class Meta:
		model = Staff_Room_Unread_Chat_Message

admin.site.register(Staff_Room_Unread_Chat_Message, Staff_Room_Unread_Chat_Message_Admin)


class Staff_Chat_Room_Admin(admin.ModelAdmin):
	list_display = ['id','title', 'slug', 'date_created']
	search_fields = ['id', 'title', ]
	readonly_fields = ['id', 'date_created']
	list_filter = ['title', 'date_created',]

	class Meta:
		model = Staff_Chat_Room

admin.site.register(Staff_Chat_Room, Staff_Chat_Room_Admin)

# Resource: http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
class CachingPaginator(Paginator):
	def _get_count(self):

		if not hasattr(self, "_count"):
			self._count = None

		if self._count is None:
			try:
				key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
				self._count = cache.get(key, -1)
				if self._count == -1:
					self._count = super().count
					cache.set(key, self._count, 3600)

			except:
				self._count = len(self.object_list)
		return self._count

	count = property(_get_count)


class Staff_Room_Chat_Message_Admin(admin.ModelAdmin):
	list_filter = ['room', 'meeting_room', 'user', "timestamp"]
	list_display = ['room','meeting_room', 'user', 'content',"timestamp"]
	search_fields = ['room__title', 'user__username','content']
	readonly_fields = ['id',"timestamp"]

	show_full_result_count = False
	paginator = CachingPaginator

	class Meta:
		model = Staff_Room_Chat_Message

admin.site.register(Staff_Room_Chat_Message, Staff_Room_Chat_Message_Admin)


