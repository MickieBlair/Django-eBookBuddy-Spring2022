from django.db import models

# Create your models here.
class Incoming_Message(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Incoming Message'
		verbose_name_plural = 'Incoming Message'

	def __str__(self):
		return self.name