from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name = "Welcome"),
    path("translate/", views.translate, name = "translate"),
    path("liveVideo/", views.live_video, name = "liveVideo"),

]