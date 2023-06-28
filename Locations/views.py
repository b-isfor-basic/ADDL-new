from typing import Any, Dict
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Establishment


class EstablishmentListView(ListView):
    model = Establishment
    template_name = "locations/establishment_list.html"
    context_object_name = "all_areas"

    def get_queryset(self):
        if self.kwargs.get("is_active"):
            self.all_areas = Establishment.objects.filter(is_active=True).order_by(
                "number"
            )
        else:
            self.all_areas = Establishment.objects.all().order_by("number")
        return self.all_areas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_areas"] = self.all_areas
        return context


class EstablishmentDetailView(DetailView):
    model = Establishment
    template_name = "locations/establishment_detail.html"
    context_object_name = "area_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["area_divisions"] = self.object.division_set.all()
        return context
