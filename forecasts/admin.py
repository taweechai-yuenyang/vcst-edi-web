from django.contrib import admin, messages
from django.shortcuts import redirect

from books.models import ReviseBook
from .models import FileForecast, OpenPDS, OpenPDSDetail

# Register your models here.

class FileForecastAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/admin/sales/invoice')
    
    def save_model(self, request, obj, form, change):
        try:
            # Get Book From Revise Book
            rvBook = ReviseBook.objects.get(name="Upload EDI")
            ### Check Revise Status
            obj.edi_filename = obj.edi_file.name
            # Set Section From User
            obj.section_id = request.user.section_id
            obj.book_id = rvBook.book_id
            # Set upload_by_id
            obj.upload_by_id = request.user
            # Generate Document No
            docNo = f"DOC{str(obj.upload_date.strftime('%Y%m%d'))[3:]}"
            n = FileForecast.objects.filter(upload_on_month=int(str(obj.upload_date.strftime('%Y%m'))),supplier_id=obj.supplier_id).count()
            obj.upload_seq = n
            documentNo = f"{docNo}{(n + 1):05d}"
            obj.document_no = documentNo
            ### Set Upload on Month with Year Number
            obj.upload_on_month = int(str(obj.upload_date.strftime('%Y%m')))
            obj.save()
            messages.success(request, f'อัพโหลดเอกสาร obj.edi_filename เลขที่ documentNo เรียบร้อยแล้ว')
                    
        except Exception as ex:
            messages.error(request, str(ex))
        
    pass

class OpenPDSAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_view.html"
    pass

class OpenPDSDetailAdmin(admin.ModelAdmin):
    pass

# admin.site.unregister(FileForecast)
# admin.site.unregister(OpenPDSDetail)
admin.site.register(FileForecast, FileForecastAdmin)
admin.site.register(OpenPDS, OpenPDSAdmin)
admin.site.register(OpenPDSDetail, OpenPDSDetailAdmin)