from django.urls import include, path
from rest_framework import routers

from . import views

urlpatterns = [
    path('revise_book', views.ReviseBookListApiView.as_view()),
    path('revise_type', views.ReviseTypeListApiView.as_view()),
    path('ref_type', views.RefTypeListApiView.as_view()),
    path("book", views.BookListApiView.as_view()),
]