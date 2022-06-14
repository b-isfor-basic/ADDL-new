from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    # TODO: Model should extend User model. Convert to abstract user?
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
    player1 = models.ForeignKey(
        User,
        models.CASCADE,
        related_name= 'team_member_1'
    )
    player2 = models.ForeignKey(
        User,
        models.CASCADE,
        related_name= 'team_member_2'
    )
    division = models.ForeignKey('Locations.Division', models.CASCADE)
    season = models.ForeignKey('Schedule.Season', models.CASCADE)

    def __str__(self):
        return f'{self.player1.last_name}/{self.player2.last_name}'