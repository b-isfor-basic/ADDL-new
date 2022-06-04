from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Establishment(models.Model):
    class States(models.TextChoices):
        ALASKA = 'AK', _('Alaska')
        ALABAMA = 'AL', _('Alabama')
        ARKANSAS = 'AR', _('Arkansas')
        ARIZONA = 'AZ', _('Arizona')
        CALIFORNIA = 'CA', _('California')
        COLORADO = 'CO', _('Colorado')
        CONNECTICUT = 'CT', _('Connecticut')
        DISTRICT_OF_COLUMBIA = 'DC', _('District of Columbia')
        DELAWARE = 'DE', _('Delaware')
        FLORIDA = 'FL', _('Florida')
        GEORGIA = 'GA', _('Georgia')
        HAWAII = 'HI', _('Hawaii')
        IOWA = 'IA', _('Iowa')
        IDAHO = 'ID', _('Idaho')
        ILLINOIS = 'IL', _('Illinois')
        INDIANA = 'IN', _('Indiana')
        KANSAS = 'KS', _('Kansas')
        KENTUCKY = 'KY', _('Kentucky')
        LOUISIANA = 'LA', _('Louisiana')
        MASSACHUSETTS = 'MA', _('Massachusetts')
        MARYLAND = 'MD', _('Maryland')
        MAINE = 'ME', _('Maine')
        MICHIGAN = 'MI', _('Michigan')
        MINNESOTA = 'MN', _('Minnesota')
        MISSOURI = 'MO', _('Missouri')
        MISSISSIPPI = 'MS', _('Mississippi')
        MONTANA = 'MT', _('Montana')
        NORTH_CAROLINA = 'NC', _('North Carolina')
        NORTH_DAKOTA = 'ND', _('North Dakota')
        NEBRASKA = 'NE', _('Nebraska')
        NEW_HAMPSHIRE = 'NH', _('New Hampshire')
        NEW_JERSEY = 'NJ', _('New Jersey')
        NEW_MEXICO = 'NM', _('New Mexico')
        NEVADA = 'NV', _('Nevada')
        NEW_YORK = 'NY', _('New York')
        OHIO = 'OH', _('Ohio')
        OKLAHOMA = 'OK', _('Oklahoma')
        OREGON = 'OR', _('Oregon')
        PENNSYLVANIA = 'PA', _('Pennsylvania')
        RHODE_ISLAND = 'RI', _('Rhode Island')
        SOUTH_CAROLINA = 'SC', _('South Carolina')
        SOUTH_DAKOTA = 'SD', _('South Dakota')
        TENNESSEE = 'TN', _('Tennessee')
        TEXAS = 'TX', _('Texas')
        UTAH = 'UT', _('Utah')
        VIRGINIA = 'VA', _('Virginia')
        VERMONT = 'VT', _('Vermont')
        WASHINGTON = 'WA', _('Washington')
        WISCONSIN = 'WI', _('Wisconsin')
        WEST_VIRGINIA = 'WV', _('West Virginia')
        WYOMING = 'WY', _('Wyoming')

    number = models.IntegerField(
        verbose_name="Area Number",
    )
    name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
    )
    streetLine1 = models.CharField(
        max_length=95,
        verbose_name="Street Address 1",
        blank=True,
        null=True,
    )
    streetLine2 = models.CharField(
        max_length=95,
        verbose_name="Street Address 2",
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=35,
        blank=True,
        null=True,
    )
    state = models.CharField(
        max_length=2,
        choices=States.choices,
        null=True,
        blank=True
    )
    zipCode = models.PositiveIntegerField(
        verbose_name="Zip Code",
        blank=True,
        null=True,
    )
    generalManager = models.CharField(max_length=100, blank=True, null=True)
    managerEmail = models.EmailField(blank=True, null=True)
    managerPhone = PhoneNumberField(blank=True, null=True)

    class Meta:
        ordering = ['number']

    def get_address(self):
        address = [self.streetLine1, self.streetLine2, self.city, self.state, self.zipCode]
        visibleAddress = []
        for i in address:
            if i != None:
                visibleAddress.append(str(i))
            else:
                continue
        return ' '.join(visibleAddress)

    def get_area_divisions(self):
        e = Establishment.objects.get(id=self.id)
        return e.division_set.all()

    def __str__(self):
        return f'{self.number} - {self.name}'

    def get_absolute_url(self):
        return reverse("area", kwargs={"pk": self.id})


class Division(models.Model):
    WEEKDAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]    

    area = models.ForeignKey(
        to=Establishment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    matchNight = models.CharField(
        choices=WEEKDAY_CHOICES,
        max_length=9,
        null=True,
        blank=True
    )
    playerFee = models.IntegerField(
        'Player Fee',
        blank=True,
        null=True,
    )
    capacity = models.IntegerField(
        'Capacity',
        null=True,
        blank=True,
    )
    divisionManager = models.ForeignKey(
        to=User,
        verbose_name='Division Manager', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    season = models.ForeignKey('Schedule.Season', models.CASCADE)

    def __str__(self):
        return f'{self.matchNight}'

    def get_absolute_url(self):
        return reverse("division_detail", kwargs={"pk": self.id})




    

