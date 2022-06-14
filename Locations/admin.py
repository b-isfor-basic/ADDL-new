from django.contrib import admin
from .models import Establishment, Division

class DivisionInline(admin.StackedInline):
    model = Division

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('number', 'name')
        }),
        ('Address', {
            'fields': ('streetLine1', 'streetLine2', 'city', 'state', 'zipCode')
        }),
        ('Business Contact', {
            'fields': ('generalManager', 'managerEmail', 'managerPhone')
        })
    )

    inlines = [DivisionInline]

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_filter = ('matchNight', 'playerFee')
    list_display = ['area', 'matchNight', 'divisionManager',]


