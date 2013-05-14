from django.db import models

class DeployPlatforms(models.Model):
	id = models.AutoField(primary_key=True)
	shortname = models.CharField(max_length=250)
	platform_id = models.CharField(max_length=250)
