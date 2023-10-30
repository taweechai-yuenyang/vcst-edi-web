from typing import Any
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.template.response import TemplateResponse
from django.urls.resolvers import URLResolver

from forecasts.admin import ForecastAdmin
from forecasts.models import Forecast
from open_pds.admin import PDSHeaderAdmin
from open_pds.models import PDSHeader

# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_title = "EDI Web Application"
    site_header = "EDI Web Application"
    index_title = "EDI Management System"
    site_url = "/"
    enable_nav_sidebar = True
    empty_value_display = "-"
    
    def has_permission(self, request):
        Forecast._meta.verbose_name_plural = "Upload Forecast"
        PDSHeader._meta.verbose_name_plural = "Open PO"
        if request.user.groups.filter(name='Purchase').exists():
            Forecast._meta.verbose_name_plural = "Open PR"
            PDSHeader._meta.verbose_name_plural = "View PR"
            
        elif request.user.groups.filter(name='Supplier').exists():
            Forecast._meta.verbose_name_plural = "Data Forecast"
            PDSHeader._meta.verbose_name_plural = "Data PO"
        
        return super().has_permission(request)
    pass

admin_site = MyAdminSite()
admin_site.register(Forecast,ForecastAdmin)
admin_site.register(PDSHeader,PDSHeaderAdmin)