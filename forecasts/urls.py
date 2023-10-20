from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('logging/<str:id>', views.export_excel),
    path('approve/<str:id>', views.approve_forecast),
    path('download/<str:id>', views.download_forecast),
    path('test/<str:id>', views.test_reporting),
    path('api/files', views.FileForecastListApiView.as_view()),
]