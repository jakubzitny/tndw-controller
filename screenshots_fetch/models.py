from django.db import models
from jsonfield import JSONField

class SdDistribution(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)
	newest_version = models.CharField(max_length=250)

class SdScreenshot(models.Model):
	id = models.AutoField(primary_key=True)
	distro = models.ForeignKey(SdDistribution)
	link = models.CharField(max_length=250)
