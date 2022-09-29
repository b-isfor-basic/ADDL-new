from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from dal import autocomplete


@login_required
def PlayerProfileView(request):
    context = {
        'message': 'This is the profile page view.'
    }
    return render(request,'members/playerprofile.html', context)


class PlayerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return None

        users = get_user_model()
        qs = users.objects.all()

        if self.q:
            qs = qs.filter(first_name__istartswith=self.q)

        return qs

