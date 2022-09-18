from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Establishment(models.Model):
    class States(models.TextChoices):
        ALASKA = "AK", _("Alaska")
        ALABAMA = "AL", _("Alabama")
        ARKANSAS = "AR", _("Arkansas")
        ARIZONA = "AZ", _("Arizona")
        CALIFORNIA = "CA", _("California")
        COLORADO = "CO", _("Colorado")
        CONNECTICUT = "CT", _("Connecticut")
        DISTRICT_OF_COLUMBIA = "DC", _("District of Columbia")
        DELAWARE = "DE", _("Delaware")
        FLORIDA = "FL", _("Florida")
        GEORGIA = "GA", _("Georgia")
        HAWAII = "HI", _("Hawaii")
        IOWA = "IA", _("Iowa")
        IDAHO = "ID", _("Idaho")
        ILLINOIS = "IL", _("Illinois")
        INDIANA = "IN", _("Indiana")
        KANSAS = "KS", _("Kansas")
        KENTUCKY = "KY", _("Kentucky")
        LOUISIANA = "LA", _("Louisiana")
        MASSACHUSETTS = "MA", _("Massachusetts")
        MARYLAND = "MD", _("Maryland")
        MAINE = "ME", _("Maine")
        MICHIGAN = "MI", _("Michigan")
        MINNESOTA = "MN", _("Minnesota")
        MISSOURI = "MO", _("Missouri")
        MISSISSIPPI = "MS", _("Mississippi")
        MONTANA = "MT", _("Montana")
        NORTH_CAROLINA = "NC", _("North Carolina")
        NORTH_DAKOTA = "ND", _("North Dakota")
        NEBRASKA = "NE", _("Nebraska")
        NEW_HAMPSHIRE = "NH", _("New Hampshire")
        NEW_JERSEY = "NJ", _("New Jersey")
        NEW_MEXICO = "NM", _("New Mexico")
        NEVADA = "NV", _("Nevada")
        NEW_YORK = "NY", _("New York")
        OHIO = "OH", _("Ohio")
        OKLAHOMA = "OK", _("Oklahoma")
        OREGON = "OR", _("Oregon")
        PENNSYLVANIA = "PA", _("Pennsylvania")
        RHODE_ISLAND = "RI", _("Rhode Island")
        SOUTH_CAROLINA = "SC", _("South Carolina")
        SOUTH_DAKOTA = "SD", _("South Dakota")
        TENNESSEE = "TN", _("Tennessee")
        TEXAS = "TX", _("Texas")
        UTAH = "UT", _("Utah")
        VIRGINIA = "VA", _("Virginia")
        VERMONT = "VT", _("Vermont")
        WASHINGTON = "WA", _("Washington")
        WISCONSIN = "WI", _("Wisconsin")
        WEST_VIRGINIA = "WV", _("West Virginia")
        WYOMING = "WY", _("Wyoming")

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
        max_length=2, choices=States.choices, default="GA", null=True, blank=True
    )
    zipCode = models.PositiveIntegerField(
        verbose_name="Zip Code",
        blank=True,
        null=True,
    )
    generalManager = models.CharField(max_length=100, blank=True, null=True)
    managerEmail = models.EmailField(blank=True, null=True)
    managerPhone = PhoneNumberField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["number"]

    def get_address(self):
        address = ""
        if self.streetLine1 != None:
            address += f"{self.streetLine1}\n".title()
        if self.streetLine2 != None:
            address += f"{self.streetLine2}\n".title()
        if self.city != None:
            address += f"{self.city}, ".title()
        if self.state != None:
            address += f"{self.state} ".upper()
        if self.zipCode != None:
            address += str(self.zipCode)
        return "".join(address)

    def __str__(self):
        return f"{self.number} - {self.name}"

    def get_absolute_url(self):
        return reverse("area", kwargs={"pk": self.id})

    def get_area_divisions(self):
        return Establishment.division_set.all(self)


class DivisionManager(models.Manager):
    def num_active_divisions(self, season_number):
        return self.filter(season__seasonNum=season_number).count()

    @property
    def num_active_teams(self):
        return self.annotate(
            num_teams=Coalesce(models.Count('team_set'))
        )


class Division(models.Model):
    WEEKDAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    area = models.ForeignKey(
        to=Establishment, on_delete=models.SET_NULL, null=True, blank=True
    )
    matchNight = models.CharField(
        "Match Night", choices=WEEKDAY_CHOICES, max_length=9, null=True, blank=True
    )
    playerFee = models.IntegerField(
        "Player Fee",
        blank=True,
        null=True,
    )
    capacity = models.IntegerField(
        "Capacity",
        null=True,
        blank=True,
    )
    divisionManager = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name="Division Manager",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    season = models.ForeignKey(
        "Schedule.Season",
        models.CASCADE,
        blank=True,
        null=True,
    )
    
    objects = models.Manager()
    active = DivisionManager()


    def __str__(self):
        return f"Area {self.area.number} - {self.matchNight}"

    def get_absolute_url(self):
        return reverse("division_detail", kwargs={"pk": self.id})

    def board_groups(self):
        boards = self.capacity
        if boards % 2 != 0:
            boards -= 1
        groups = []
        for i in range(1, boards, 2):
            groups.append([i, i + 1])
        return groups
