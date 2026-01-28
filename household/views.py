from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import TemplateView, View


class HomeView(TemplateView):
    template_name = "home.html"


class ServerTimeView(View):
    """Return a DaisyUI badge snippet with the current server time."""

    def get(self, request, *args, **kwargs):
        current_time = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S %Z")
        fragment = render_to_string(
            "includes/server_time.html",
            {"current_time": current_time},
            request=request,
        )
        return HttpResponse(fragment)
