from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, CreateView
from .models import Establishment, Division

def establishment_list(request):
    all_areas = Establishment.objects.all()
    context = {
        'all_areas': all_areas,
    }
    return render(request, 'establishment_list.html', context)
        

def establishment_detail(request, pk):
    area = get_object_or_404(Establishment, pk=pk)
    return render(request, 'establishment_detail.html', {'area': area})

   
class create_establishment(CreateView):
    model = Establishment
    context_object_name = 'create_area'