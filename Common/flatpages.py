from django.views.generic import TemplateView, ListView
from django.utils import timezone

from Schedule.models import Announcement


class PrivacyPolicyView(TemplateView):
    template_name = "common/privacy.html"


class TermsOfServiceView(TemplateView):
    template_name = "common/terms.html"


class IndexView(ListView):
    model = Announcement
    queryset = Announcement.objects.filter(inactive_date__gte=timezone.now())
    template_name = "common/index.html"
    context_object_name = "announcement_list"
