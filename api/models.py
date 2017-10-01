from __future__ import unicode_literals
import uuid

from django.db import models

# Create your models here.
# Model for storing Moment details
class Device(models.Model):
    device_id = models.CharField(db_index=True, max_length=200)
    device_registration_id = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField()

class Session(models.Model):
	device = models.ForeignKey(Device, on_delete=models.CASCADE)
	token = models.UUIDField(default=uuid.uuid1, editable=False)



class Location(models.Model):
	latitude = models.CharField(max_length=200)
	longitude = models.CharField(max_length=200)

class Event(models.Model):
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	device = models.ForeignKey(Device, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='photos', max_length=254, blank=True, null=True)
	upvote = models.IntegerField(default=1)
	downvote = models.IntegerField(default=0)
	event_key = models.UUIDField(default=uuid.uuid1, editable=False)


class Trip(models.Model):
	device = models.ForeignKey(Device, on_delete=models.CASCADE)
	path = models.ManyToManyField(Location)
	finished = models.BooleanField(default=False)
	trip_key = models.UUIDField(default=uuid.uuid1, editable=False)

