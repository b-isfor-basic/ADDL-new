from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Q

from .models import Player


@login_required
def PlayerProfileView(request):
    context = {
        'message': 'This is the profile page view.'
    }
    return render(request,'members/playerprofile.html', context)


# class PlayerSearchView(ListView):
#     model = Player
#     template_name = 'partials/player_search.html'
# 
#     def get_queryset(self):
#         q = self.request.GET.get('q')
#         object_list = Player.objects.filter(
#             Q(first_name__istartswith=q) | 
#             Q(last_name__istartswith=q) |
#             Q(username__istartswith=q) |
#             Q(email__istartswith=q)
#         )
#         return object_list

