import re

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from Members.models import Player

from .managers import DivisionManager


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
    shortName = models.CharField(
        max_length=35,
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
    is_active = models.BooleanField(default=True, db_index=True)
    numberOfBoards = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        if self.shortName is not None:
            return f"Area {self.number} - {self.shortName}"
        else:
            return f"Area {self.number} - {self.name}"

    def get_address(self):
        address = ""
        if self.streetLine1 is not None:
            address += f"{self.streetLine1}\n".title()
        if self.streetLine2 is not None:
            address += f"{self.streetLine2}\n".title()
        if self.city is not None:
            address += f"{self.city}, ".title()
        if self.state is not None:
            address += f"{self.state} ".upper()
        if self.zipCode is not None:
            address += str(self.zipCode)
        return "".join(address)

    def get_absolute_url(self):
        return reverse("area", kwargs={"pk": self.id})


class Division(models.Model):
    WEEKDAY_CHOICES = [
        ("Mon", "Mon"),
        ("Tues", "Tues"),
        ("Wed", "Wed"),
        ("Thurs", "Thurs"),
        ("Fri", "Fri"),
        ("Sat", "Sat"),
        ("Sun", "Sun"),
    ]

    area = models.ForeignKey(
        to=Establishment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )
    matchNight = models.CharField(
        "Match Night",
        choices=WEEKDAY_CHOICES,
        max_length=9,
        null=True,
        blank=True,
        db_index=True,
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
    division_manager = models.ForeignKey(
        to=Player,
        verbose_name="Division Manager",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    objects = models.Manager()
    details = DivisionManager()

    class Meta:
        ordering = ["area__number", "matchNight"]

    def __str__(self):
        if self.area.shortName is not None:
            area_nm = self.area.shortName
        else:
            area_nm = self.area.name
        return f"{area_nm} - {self.matchNight}"

    def get_absolute_url(self):
        return reverse("division_detail", kwargs={"pk": self.id})
