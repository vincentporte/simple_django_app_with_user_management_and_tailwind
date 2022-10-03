from django.urls import path

from apps.www.home.views import HomePageView

# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "home"


urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
]
