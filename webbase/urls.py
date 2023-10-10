"""
URL configuration for webbase project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt import views as jv
from users import urls as user_urls
from products import urls as product_urls
from books import urls as book_urls

admin.site.site_title = "EDI Web Application"
admin.site.site_header = "EDI Web Application"
admin.site.index_title = "EDI Management System"
admin.site.site_url = "/"
admin.site.enable_nav_sidebar = True
admin.site.empty_value_display = "-"


urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("api/users/", include(user_urls)),
    path("api/products/", include(product_urls)),
    path("api/books/", include(book_urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', jv.TokenObtainPairView.as_view()),
    path('api/token/refresh/', jv.TokenRefreshView.as_view()),
    path("", RedirectView.as_view(url="admin/", permanent=True)),
]
