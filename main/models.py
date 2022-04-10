from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Data(models.Model):
    url = models.URLField(max_length=100)
    bad_data = models.TextField(blank=True)
    last_status = models.IntegerField(blank=True, null=True)
    last_response_time = models.FloatField(blank=True, null=True)
    last_check = models.DateTimeField(blank=True, null=True)


class SiteToCheck(models.Model):
    url = models.URLField(max_length=100)
    user = models.CharField(max_length=100, default='Admin')
    bad_data = models.TextField(blank=True)
    last_status = models.IntegerField(blank=True, null=True)
    last_response_time = models.FloatField(blank=True, null=True)
    last_check = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.url





# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email_to = models.EmailField(default='')
#
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

