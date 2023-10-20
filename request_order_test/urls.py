from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('excel/<str:id>', views.export_excel),
]