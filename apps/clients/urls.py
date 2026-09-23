from django.urls import path

from apps.clients.views import ClientCreateView

app_name = "clients"

urlpatterns = [
    path("register/", ClientCreateView.as_view(), name="client-create"),
]
