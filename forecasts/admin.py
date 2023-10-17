from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html
import numpy as np
import pandas as pd

from books.models import ReviseBook
from products.models import Product, ProductGroup
from users.models import Supplier
from .models import FileForecast, OpenPDS, OpenPDSDetail, PDSErrorLogs

# Register your models here.

class FileForecastAdmin(admin.ModelAdmin):
    fields = [
        'edi_file'
    ]
    def response_add(self, request, obj, post_url_continue=None):
        if obj.is_active:
            return redirect('/portal/forecasts/pdslogs/')
        
        return redirect('/portal/forecasts/openpds/')
    
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
            n = FileForecast.objects.filter(upload_on_month=int(str(obj.upload_date.strftime('%Y%m')))).count()
            obj.upload_seq = n
            documentNo = f"{docNo}{(n + 1):05d}"
            obj.document_no = documentNo
            ### Set Upload on Month with Year Number
            obj.upload_on_month = int(str(obj.upload_date.strftime('%Y%m')))
            obj.is_active = True
            obj.save()
            
            try:
                supNotFound = []
                partNotFound = []
                data = pd.read_excel(request.FILES['edi_file'], sheet_name=0)
                dumpDate = data.columns[0]
                print(dumpDate[len('Forecast '):len('Forecast ') + 3])
                
                ### - To Nan
                data.replace('-', np.nan, inplace=True)
                
                ### VCST To Nan
                data.replace('VCST', np.nan, inplace=True)
                
                ### Nan to 0
                data.fillna(0, inplace=True)
                df = data.to_records()
                i = 0
                for r in df:
                    if i > 0:
                        # print(r)
                        rows = int(r[0]) + 2
                        id = int(r[1])
                        partName = str(r[2]).strip()
                        partNo = str(r[3]).strip()
                        partDescription = str(r[4]).strip()
                        supName = str(r[5]).strip()
                        partModel = str(r[6]).strip()
                        rev0 = int(r[7])
                        rev1 = int(r[8])
                        rev2 = int(r[9])
                        rev3 = int(r[10])
                        description  = ""
                        
                        if partNo != "0":
                            isCheckError = False
                            ### Fetch Data Sup.
                            msgSup = ""
                            try:
                                if supName == "0":
                                    isCheckError = True
                                    msgSup = f"ไม่ระบุ Sup."
                                    
                                else:
                                    supFilter = Supplier.objects.get(code=str(supName).strip())
                                    
                            except Supplier.DoesNotExist as ex:
                                isCheckError = True
                                msgSup = f"ไม่พบข้อมูล Sup:{supName}"
                                if (supName in supNotFound) is False:
                                    supNotFound.append(supName)
                                    #### Create Error logging
                                    
                                pass
                            
                            msgProduct = ""
                            try:
                                partNoFilter = Product.objects.get(code=str(partNo).strip())
                                
                            except Product.DoesNotExist as ex:
                                isCheckError = True
                                msgProduct = f"ไม่พบข้อมูล Part:{partNo}"
                                if (partNo in partNotFound) is False:
                                    partNotFound.append(partNo)
                                    #### Create Error logging
                                    
                                pass
                            
                            # msgModel = ""
                            # try:
                            #     if partModel != 0:
                            #         partModelFilter = ProductGroup.objects.get(code=str(partModel).strip())
                                    
                            # except ProductGroup.DoesNotExist as ex:
                            #     isCheckError = True
                            #     msgModel = f"ไม่พบข้อมูล Model:{partModel}"
                            #     if (partModel in modelNotFound) is False:
                            #         modelNotFound.append(partModel)
                            #         #### Create Error logging
                                    
                            #     pass
                            
                            
                            #### Create PDSErrorLogs
                            if isCheckError:
                                description = str(f"{msgSup} {msgProduct} บรรทัดที่ {rows}").lstrip()
                                print(description)
                            
                            logError = PDSErrorLogs(
                                file_name=obj.id,
                                row_num=rows,
                                item=i,
                                part_code=partName,
                                part_no=partNo,
                                part_name=partDescription,
                                supplier=supName,
                                model=partModel,
                                rev_0=rev0,
                                rev_1=rev1,
                                rev_2=rev2,
                                rev_3=rev3,
                                remark=description,
                                is_error=isCheckError,
                                is_success=(isCheckError is False),
                            )
                            logError.save()
                            
                    i += 1
                    
                if (len(supNotFound) > 0 or len(partNotFound) > 0):
                    messages.warning(request, format_html("{} <a class='text-success' href='/forecast/logging/{}'>{}</a>", f"เกิดข้อผิดพลาดไม่สามารถอัพโหลดข้อมูลได้", str(obj.id), "รบกวนกดที่ลิงค์นี้เพื่อตรวจข้อผิดพลาดดังกล่าว"))
                    
                else:
                    messages.success(request, f'อัพโหลดเอกสาร {obj.edi_file} เลขที่ {documentNo} เรียบร้อยแล้ว')
                
                obj.is_active = ((len(supNotFound) > 0 or len(partNotFound) > 0) is False)
                obj.delete()
                
            except Exception as ex:
                messages.error(request, str(ex))
                obj.delete()
                    
        except Exception as ex:
            messages.error(request, str(ex))
        
    pass

class OpenPDSAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_view.html"
    pass

class OpenPDSDetailAdmin(admin.ModelAdmin):
    pass

class PDSErrorLogsAdmin(admin.ModelAdmin):
    pass

# admin.site.unregister(FileForecast)
# admin.site.unregister(OpenPDSDetail)
admin.site.register(FileForecast, FileForecastAdmin)
admin.site.register(OpenPDS, OpenPDSAdmin)
admin.site.register(OpenPDSDetail, OpenPDSDetailAdmin)
admin.site.register(PDSErrorLogs, PDSErrorLogsAdmin)