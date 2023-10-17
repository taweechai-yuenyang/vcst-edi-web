from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('logging/<str:id>', views.export_excel),
]