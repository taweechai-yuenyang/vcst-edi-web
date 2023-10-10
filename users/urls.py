from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('supplier', views.SupplierListApiView.as_view()),
    path("section", views.SectionListApiView.as_view()),
    path("position", views.PositionListApiView.as_view()),
    path("department", views.DepartmentListApiView.as_view()),
    path("employee", views.EmployeeListApiView.as_view()),
    path("factory", views.FactoryListApiView.as_view()),
    path("corporation", views.CorporationListApiView.as_view()),
    path("position", views.PositionListApiView.as_view()),
]