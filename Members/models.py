from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    # TODO: Model should extend User model. Possibly need to convert to abstract
    # user model instead?
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = PhoneNumberField() 
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Team(models.Model):
    players = models.ManyToManyField(User)
    division = models.ForeignKey('Locations.Division', models.CASCADE)
    season = models.ForeignKey('Schedule.Season', models.CASCADE)

    def display_players(self):
        return '/'.join(player.last_name for player in self.players.all())

    display_players.short_description = 'Name'

    def __str__(self):
        return self.display_players()
