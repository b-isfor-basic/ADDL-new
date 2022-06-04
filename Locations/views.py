from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, CreateView
from .models import Establishment, Division

class establishment_list(ListView):
    model = Establishment
    context_object_name = 'all_areas'
    template_name = 'Locations/establishment_list.html'
    paginate_by = 10
        

def establishment_detail(request, pk):
    area = get_object_or_404(Establishment, pk=pk)
    return render(request, 'Locations/establishment_detail.html', {'area': area})

   
class create_establishment(CreateView):
    model = Establishment
    context_object_name = 'create_area'