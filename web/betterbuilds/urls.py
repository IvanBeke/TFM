from django.conf.urls import url
from . import views

urlpatterns = [
    url('champions', views.champions, name="champions"),
    url('', views.index, name="index"),
]