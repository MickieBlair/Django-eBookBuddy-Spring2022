from django.contrib import admin
from django.db import models
from django.core.paginator import Paginator
from django.core.cache import cache
from private_chat.models import Private_Chat_Error
from private_chat.models import Notification
from private_chat.models import PrivateChatRoom
from private_chat.models import PrivateChatMessage
from private_chat.models import UnreadPrivateChatMessages
from private_chat.models import User_Private_Room_List

class Private_Chat_Error_Admin(admin.ModelAdmin):
    list_display = ('file', 'function_name', 'location_in_function',
                    'occurred_for_user','created', 'error_text')
    readonly_fields=('created', )
    filter_horizontal = ()
    list_filter = ['created', 'file', 'function_name',]

    class Meta:
        model = Private_Chat_Error

admin.site.register(Private_Chat_Error, Private_Chat_Error_Admin)

class Notification_Admin(admin.ModelAdmin):
	list_display = ('target', 'from_user', 'verb','timestamp','read','content_type', 'object_id', 'content_object')
	readonly_fields=('timestamp', )
	filter_horizontal = ()
	list_filter = ['target', 'from_user', 'read']

	class Meta:
		model = Notification

admin.site.register(Notification, Notification_Admin)

class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id','user1', 'user2', ]
    search_fields = ['id', 'user1__username', 'user2__username','user1__email', 'user2__email', ]
    readonly_fields = ['id',]

    class Meta:
        model = PrivateChatRoom


admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)

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

class PrivateChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room','to_user', 'from_user', 'user', "timestamp"]
    list_display = ['room', 'to_user', 'from_user',  'user', 'content',"timestamp"]
    search_fields = ['user__username','content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = PrivateChatMessage

admin.site.register(PrivateChatMessage, PrivateChatMessageAdmin)

class UnreadPrivateChatMessagesAdmin(admin.ModelAdmin):
    list_display = ['room','user', 'count' ]
    search_fields = ['room__user1__username', 'room__user2__username', ]
    readonly_fields = ['id',]

    class Meta:
        model = UnreadPrivateChatMessages

admin.site.register(UnreadPrivateChatMessages, UnreadPrivateChatMessagesAdmin)

class User_Private_Room_List_Admin(admin.ModelAdmin):
    list_display = ['user','room_count','total_unread_private', 'date_created', 'last_updated']
    search_fields = ['user__username',]
    readonly_fields = ['date_created','last_updated' ]
    filter_horizontal = ['private_rooms',]
    list_filter = ['user',]

    class Meta:
        model = User_Private_Room_List

admin.site.register(User_Private_Room_List, User_Private_Room_List_Admin)
