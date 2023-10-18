from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('logging/<str:id>', views.export_excel),
    path('download/<str:id>', views.download_forecast),
    path('test/<str:id>', views.test_reporting),
]