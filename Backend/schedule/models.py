from typing import Iterable
from django.db import models

# Create your models here.


class Venue(models.Model):
    name = models.CharField(max_length=20, unique=True, primary_key=True)
    capacity = models.IntegerField()
    address = models.TextField(max_length=500)
    is_available = models.BooleanField(default=True)
    image = models.CharField(max_length=10000)
    
    # event = models.ForeignKey('Event', on_delete=models.CASCADE, null=False, blank=False)


class Booking(models.Model):
    date = models.DateField(blank=False, null=False)
    time =  models.TimeField(blank=False, null=False)
    committee = models.ForeignKey('base.Committee', on_delete=models.CASCADE, blank=False, null=False)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=False, null=False)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=False, blank=False)
    is_approved_all = models.BooleanField(default=False)
    is_approved_pri = models.BooleanField(default=False)
    is_approved_mentor = models.BooleanField(default=False)
    is_approved_dean = models.BooleanField(default=False)
    is_approved_hod = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_approved_pri and self.is_approved_hod and self.is_approved_mentor and self.is_approved_dean:
            self.is_approved_all = True
            self.event.is_approved = True
            self.event.save()
            self.venue.is_available = False
            self.venue.save()
        else:
            self.is_approved_all = False
            self.event.is_approved = False
            self.event.save()
            self.venue.is_available = True
            self.venue.save()
        super().save(*args, **kwargs)


class Event(models.Model):
    ENTERTAINMENT = 'entertainment'
    EDUCATION = 'education'

    EVENT_TYPES = [
        (ENTERTAINMENT, 'entertainment'),
        (EDUCATION, 'education')
    ]
    name = models.CharField(max_length=200, unique=True)
    committee = models.ForeignKey('base.Committee', on_delete=models.CASCADE, blank=False, null=False)
    # booking = models.ForeignKey('Booking', on_delete=models.CASCADE, blank=False, null=False)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE)
    # regi_members = models.JSONField(default={"students" : []})
    regi_members = models.TextField(default="", max_length=10000)
    type = models.CharField(max_length=50, blank=False, null=False, choices=EVENT_TYPES)
    desc = models.TextField(max_length=1000)
    date = models.DateField(blank=False, null=False)
    time =  models.TimeField(blank=False, null=False)
    is_approved = models.BooleanField(default=False)
    image = models.CharField(max_length=10000, null=True)
    

    