from django.db import models
from users.models import CustomUser
from buddy_program_data.models import Mega_Team, Team
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

TEAM_ROLE_CHOICE = [("Coordinator","Coordinator"),("Team Leader","Team Leader"),("Member","Member")]

# Create your models here.
class User_Team_Info(models.Model):
	user = models.OneToOneField(CustomUser,
							related_name='team_info',
							on_delete=models.CASCADE , unique=True)
	team_role = models.CharField(max_length=30, choices=TEAM_ROLE_CHOICE, null=True, blank=True)

	mega = models.ForeignKey(Mega_Team, on_delete=models.DO_NOTHING, 
							related_name='user_mega', null=True, blank=True)

	team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, 
							related_name='user_team', null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")



	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name = 'User Team Info'
		verbose_name_plural = 'Users Team Info'

def pre_save_user_info_receiver(sender, instance, *args, **kwargs):
	if instance.team:
		instance.mega = instance.team.mega


pre_save.connect(pre_save_user_info_receiver, sender=User_Team_Info)

