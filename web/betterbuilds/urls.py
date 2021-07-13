from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('champions', views.champions, name='champions'),
    path('champions/<int:champion_id>/', views.champions_builds, name='champion_builds'),
]