from django.db import models
from jsonfield import JSONField

class Architecture(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)

class Desktop(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)

class Category(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)

class Link(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)
	href = models.CharField(max_length=250)

class Update(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=250)
	text = models.CharField(max_length=250)
	
class Article(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=250)
	text = models.CharField(max_length=250)

class FeatureType(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)

class Package(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)
	version = models.CharField(max_length=250)

class Feature(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)
	type = models.ForeignKey(FeatureType)

class DistroVersion(models.Model):
	id = models.AutoField(primary_key=True)
	number = models.IntegerField()	
	name = models.CharField(max_length=250)
	packages = models.ManyToManyField(Package)
	features = models.ManyToManyField(Feature)

class Thing(models.Model):
	name = models.CharField(max_length=250)
	numbers = JSONField()
	type = models.CharField(max_length=250)

class OsType(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)

class BasedOnDistro(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=250)
	shortname = models.CharField(max_length=250)
	type = models.CharField(max_length=250)

class Distribution(models.Model):

	id = models.AutoField(primary_key=True)

	STATE_ACTIVE = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

	name = models.CharField(max_length=250)
	shortname = models.CharField(max_length=250)
	os_type = models.ForeignKey(OsType)
	based_ons = models.ManyToManyField(BasedOnDistro)
	origin = models.CharField(max_length=250)
	architectures = models.ManyToManyField(Architecture)
	desktops = models.ManyToManyField(Desktop)
	categories = models.ManyToManyField(Category)
	description = models.TextField()
	#status = models.CharField(max_length=250, choices=STATE_ACTIVE)
	status = models.CharField(max_length=250)
	popularity = models.IntegerField()
	sdscreenshot_id = models.IntegerField()

	homepage = JSONField()
	mailing_lists = JSONField()
	user_forums = JSONField()
	documentations = JSONField()
	screenshots = JSONField()
	download_mirrors = JSONField()
	bug_trackers = JSONField()
	related_websites = JSONField()
	reviews = JSONField()
	articles = JSONField()
