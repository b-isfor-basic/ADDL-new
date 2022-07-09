from django.shortcuts import get_object_or_404, render, HttpResponse
from django.views.generic import ListView

from .models import Establishment, Division
from .forms import EstablishmentForm, DivisionForm

def establishment_list(request):
    all_areas = Establishment.objects.all()
    if 'is_active' in request.GET.keys():
        is_active = request.GET['is_active']
        all_active = Establishment.objects.filter(is_active=is_active)
        context = {
            'all_areas': all_active,
        }
    else:
        context = {
            'all_areas': all_areas,
        }
    return render(request, 'establishment_list.html', context)


def establishment_detail(request, pk):
    area = get_object_or_404(Establishment, pk=pk)
    divisions = Division.objects.filter(area=area)
    form = DivisionForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            division = form.save(commit=False)
            division.area = area
            division.is_active = False
            division.save()
            return HttpResponse('success')
        else:
            return render(request, 'partials/division_form.html', context={
                'form': form
            })

    context = {
        'form': form,
        'area': area,
        'divisions': divisions
    }

    return render(request, 'establishment_detail.html', context)

def create_division_form(request):
    form = DivisionForm()
    context = {
        'form': form
    }
    return render(request, 'partials/division_form.html', context)