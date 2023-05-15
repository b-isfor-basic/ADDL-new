from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Establishment


class EstablishmentListView(ListView):
    model = Establishment
    template_name = "locations/establishment_list.html"
    context_object_name = "all_areas"

    def get_queryset(self):
        qs = super().get_queryset()
        if "is_active" in self.request.GET.keys():
            is_active = self.request.GET.get("is_active")
            qs = qs.filter(is_active=is_active)
        return qs


class EstablishmentDetailView(DetailView):
    model = Establishment
    template_name = "locations/establishment_detail.html"
    context_object_name = "area_detail"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("division_set__scheduleweek_set__match_set")
