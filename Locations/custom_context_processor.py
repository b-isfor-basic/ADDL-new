from .models import Establishment

def area_renderer(request):
    return {
        'all_areas': Establishment.objects.all(),
    }