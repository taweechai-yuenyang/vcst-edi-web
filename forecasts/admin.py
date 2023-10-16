from django.contrib import admin
from .models import FileForecast, OpenPDS, OpenPDSDetail

# Register your models here.

class FileForecastAdmin(admin.ModelAdmin):
    pass

class OpenPDSAdmin(admin.ModelAdmin):
    pass

class OpenPDSDetailAdmin(admin.ModelAdmin):
    pass

admin.site.register(FileForecast, FileForecastAdmin)
admin.site.register(OpenPDS, OpenPDSAdmin)
admin.site.register(OpenPDSDetail, OpenPDSDetailAdmin)