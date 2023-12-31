from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('logging/<str:id>', views.export_excel),
    path('approve/<str:id>', views.approve_forecast),
    path('download/<str:id>', views.download_forecast),
    path('export_pds/<str:id>', views.download_open_pds),
    path('create_po/<str:id>', views.create_po_forecast),
    path('test/<str:id>', views.test_reporting),
    path('pdf/<str:id>', views.pdf_forecast, name="pdf_forecast"),
    path('api/files', views.FileForecastListApiView.as_view()),
]