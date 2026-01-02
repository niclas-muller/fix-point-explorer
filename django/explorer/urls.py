from django.urls import path

from explorer.views import IndexView, DetailView

app_name = "explorer"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("<int:function_id>/", DetailView.as_view(), name="detail"),
]
