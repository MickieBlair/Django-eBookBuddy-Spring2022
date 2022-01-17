from django.contrib import admin
from site_admin.models import User_Team_Info

# Register your models here.
class User_Team_Info_Admin(admin.ModelAdmin):
	list_display = ('user', 'team_role', 'mega', 'team', 'date_created', 'last_updated')
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['team_role', 'mega', 'team', ]
	search_fields = ['user__username', 'user__first_name', 'user__last_name']

	class Meta:
		model = User_Team_Info

admin.site.register(User_Team_Info, User_Team_Info_Admin)