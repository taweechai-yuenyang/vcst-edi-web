import calendar
import os
from typing import Any
from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import FormView
from django.forms import BaseInlineFormSet
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.utils.html import format_html
from admin_confirm import AdminConfirmMixin
import nanoid
import numpy as np
import pandas as pd
import requests

from books.models import ReviseBook
from forecasts import greeter
from formula_vcst.models import BOOK, COOR, DEPT, EMPLOYEE, PROD, SECT, UM, OrderH, OrderI
from products.models import Product, ProductGroup
from users.models import ManagementUser, PlanningForecast, Supplier
from .models import FORECAST_ORDER_STATUS, FileForecast, Forecast, ForecastDetail, ForecastErrorLogs, PDSDetail, PDSHeader

class FileForecastAdmin(admin.ModelAdmin):
    fields = [
        'edi_file'
    ]
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        
        return request.user.has_perm("forecasts.add_file")
    
    # def has_module_permission(self, request):
    #     print(f"perms")
    #     print(request.user.has_perm("forecasts.add_file"))
    #     return request.user.has_perm("forecasts.add_file")
    
    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/portal/forecasts/forecast/')
    
    def save_model(self, request, obj, form, change):
        try:
            token = request.user.line_notification_id.token
            if bool(os.environ.get('DEBUG_MODE')):
                token = os.environ.get("LINE_TOKEN")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {token}'
            }
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
            obj.save() ### Debug
            
            planForecast = None
            try:
                supNotFound = []
                partNotFound = []
                listHeader = []
                data = pd.read_excel(request.FILES['edi_file'], sheet_name=0)
                
                ### Query Planning Forecast
                dumpDate = data.columns[0]
                month = str(dumpDate[len('Forecast '):len('Forecast ') + 3])
                mm = list(calendar.month_abbr)
                x = 0
                for m in mm:
                    x += 1
                    if month == m:
                        break
                
                planForecast = PlanningForecast.objects.get(plan_day=1, plan_month=str(x), plan_year=obj.upload_date.strftime('%Y'))
                #### End
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
                            supFilter = None
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
                            
                            partNoFilter = None
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
                            
                            
                            #### Create ForecastErrorLogs
                            if isCheckError:
                                description = str(f"{msgSup} {msgProduct} บรรทัดที่ {rows}").lstrip()
                                print(description)
                                
                            else:
                                ### Create PDS Header
                                pdsHeader = None
                                try:
                                    pdsHeader = Forecast.objects.get(edi_file_id=obj,supplier_id=supFilter,forecast_plan_id=planForecast)
                                    
                                except Forecast.DoesNotExist as ex:
                                    rndNo = f"FC{str(obj.upload_date.strftime('%Y%m'))[3:]}"
                                    rnd = f"{rndNo}{(Forecast.objects.filter(forecast_no__gte=rndNo).count() + 1):05d}"
                                    pdsHeader = Forecast(
                                        forecast_plan_id=planForecast,
                                        edi_file_id=obj,
                                        supplier_id=supFilter,
                                        section_id=request.user.section_id,
                                        book_id=obj.book_id,
                                        forecast_no=rnd,
                                        forecast_date=obj.upload_date,
                                        forecast_on_month=obj.upload_on_month,
                                        forecast_by_id=request.user,
                                        forecast_status="0",
                                    )
                                    pass
                                
                                pdsHeader.save()
                                ### Append Header
                                if (pdsHeader.id in listHeader) is False:
                                    listHeader.append(pdsHeader.id)
                                    
                                ### Create PDS Detail
                                pdsDetail = None
                                try:
                                    pdsDetail = ForecastDetail.objects.get(forecast_id=pdsHeader,product_id=partNoFilter)
                                except ForecastDetail.DoesNotExist as ex:
                                    pdsDetail = ForecastDetail(
                                        forecast_id=pdsHeader,
                                        product_id=partNoFilter,
                                        request_qty=rev0,
                                        balance_qty=rev0,
                                        price=partNoFilter.price,
                                        request_by_id=request.user,
                                        request_status="0",
                                        import_model_by_user=partModel,
                                    )
                                    pass
                                
                                pdsDetail.save()
                                
                            logError = ForecastErrorLogs(
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
                    
                ### Update Header
                for h in listHeader:
                    pdsHeader = Forecast.objects.get(id=h)
                    items = ForecastDetail.objects.filter(forecast_id=h)
                    rNum = 0
                    rQty = 0
                    rPrice = 0
                    for r in items:
                        rQty += r.request_qty
                        rPrice += float(r.product_id.price)
                        rNum += 1
                        r.seq = rNum
                        r.save()
                        
                    pdsHeader.forecast_item = rNum
                    pdsHeader.forecast_qty = rQty
                    pdsHeader.forecast_price = rPrice
                    pdsHeader.save()
                    
                if (len(supNotFound) > 0 or len(partNotFound) > 0):
                    messages.warning(request, format_html("{} <a class='text-success' href='/forecast/logging/{}'>{}</a>", f"เกิดข้อผิดพลาดไม่สามารถอัพโหลดข้อมูลได้", str(obj.id), "รบกวนกดที่ลิงค์นี้เพื่อตรวจข้อผิดพลาดดังกล่าว"))
                    obj.delete()
                    
                else:
                    messages.success(request, f'อัพโหลดเอกสารเลขที่ {documentNo} เรียบร้อยแล้ว')
                    obj.is_active = ((len(supNotFound) > 0 or len(partNotFound) > 0) is False)
                    obj.save()
                    msg = f"message=เรียนแผนก PU\nขณะนี้ทางแผนก Planning ทำการอัพโหลดเอกสาร {documentNo} กรุณาทำการยืนยันให้ด้วยคะ"
                    response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
                    print(response.status_code)
                
            except Exception as ex:
                messages.error(request, str(ex))
                obj.delete()
                    
        except Exception as ex:
            messages.error(request, str(ex))
        
    pass

class PDSDetailFormSet(BaseInlineFormSet): 
    def get_queryset(self) :
        qs = super().get_queryset()
        return qs
    
class ProductPDSDetailInline(admin.TabularInline):
    model = ForecastDetail
    readonly_fields = (
        'seq',
        'product_id',
        'request_qty',
        'balance_qty',
        'request_status',
        'updated_at',
    )

    fields = [
        'seq',
        'product_id',
        'request_qty',
        'price',
        'updated_at',
    ]

    # def updated_on(self, obj):
    #     # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
    #     return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")
    formset = PDSDetailFormSet
    extra = 25
    max_num = 5
    can_delete = False
    can_add = False
    show_change_link = False

    def has_change_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        return False

class ForecastDetailAdmin(admin.ModelAdmin):
    pass   

# @admin.action(description="Mark selected to Reject", permissions=["change"])
@admin.action(description="Mark selected to Reject")
def make_reject_forecast(modeladmin, request, queryset):
    # confirm_change = True
    # confirmation_fields = ['forecast_status',]
    queryset.update(forecast_status="3")

# @admin.action(description="Mark selected to Approve", permissions=["change"])
@admin.action(description="Mark selected to Approve")
def make_approve_forecast(modeladmin, request, queryset):
    ### 
    data = queryset
    isValid = False
    for i in data:
        if int(i.forecast_status) > 0:
            isValid = True
            break
        
    if isValid:
        messages.error(request, "ไม่สามารถดำเนินการตามที่ร้องขอได้เนื่องจาก สถานะของรายการไม่ถูกต้อง รบการทบทวนรายการที่เลือกใหม่ด้วย")
        return
    
    for obj in data:
        greeter.create_purchase_order(request, obj.id)
    
class ForecastAdmin(AdminConfirmMixin, admin.ModelAdmin):
    change_list_template = "admin/change_list_view.html"
    change_form_template = "admin/change_form_view.html"
    inlines = [ProductPDSDetailInline]
    list_display = (
        "forecast_no",
        "forecast_date_on",
        "supplier_id",
        "book_id",
        "forecast_item",
        "forecast_qty",
        "price",
        "status",
        "updated_on",
    )
    
    list_filter = (
        "forecast_date",
        "supplier_id",
        "forecast_status",
    )
    
    fields = [
        'forecast_no',
        'book_id',
        'forecast_date',
        'forecast_item',
        'forecast_qty',
        'supplier_id',
        'forecast_status',
    ]
    
    readonly_fields = [
        'forecast_no',
        'book_id',
        'forecast_date',
        'forecast_item',
        'forecast_qty',
        'supplier_id',
        'forecast_status',
    ]
    date_hierarchy = ('forecast_date')
    
    list_per_page = 25
    
    actions = [make_approve_forecast, make_reject_forecast]
    
    def get_actions(self, request):
        actions = super(ForecastAdmin, self).get_actions(request)
        permissions = request.user.get_all_permissions()
        # {'forecasts.view_pdsheader', 'forecasts.view_pdsdetail', 'forecasts.edit_qty_price', 'forecasts.view_forecast', 'forecasts.approve_reject', 'forecasts.select_item', 'forecasts.view_forecastdetail'}
        if ('forecasts.approve_reject' in permissions) is False:
            del actions['make_approve_forecast']
            del actions['make_reject_forecast']
        
        return actions
    
    # Set Overrides Message
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        pass
    
    def price(self, obj):
        return f'{obj.forecast_price:.2f}'
    
    def forecast_date_on(self, obj):
        return obj.forecast_date.strftime("%d-%m-%Y")

    def updated_on(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def status(self, obj):
        try:
            data = FORECAST_ORDER_STATUS[int(obj.forecast_status)]
            txtClass = "text-bold"
            if int(obj.forecast_status) == 0:
                txtClass = "text-info text-bold"

            elif int(obj.forecast_status) == 1:
                txtClass = "text-success text-bold"

            elif int(obj.forecast_status) == 2:
                txtClass = "text-info"

            elif int(obj.forecast_status) == 3:
                txtClass = "text-danger"

            elif int(obj.forecast_status) == 4:
                txtClass = "text-danger"

            return format_html(f"<span class='{txtClass}'>{data[1]}</span>")
        
        except:
            pass
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        ### Get object
        obj = Forecast.objects.get(id=object_id)
        ### Append Variable
        extra_context['osm_data'] = obj
        extra_context['forecast_status'] = int(obj.forecast_status)
        extra_context['forecast_revise'] = obj.edi_file_id.upload_seq
        ### If Group is Planning check PR status
        isPo = False
        if request.user.groups.filter(name='Planning').exists():
            isPo = obj.ref_formula_id != None
    
        extra_context['send_to_po'] = isPo
        return super().change_view(request, object_id, form_url, extra_context=extra_context,)
    
    def response_change(self, request, obj):
        return super().response_post_save_change(request, obj)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sup_id = []
        # if request.user.groups.filter(name='Supplier').exists():
        #     usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
        #     for u in usr:
        #         sup_id.append(u.supplier_id)
        
        usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
        for u in usr:
            sup_id.append(u.supplier_id)
        
        if request.user.groups.filter(name='Supplier').exists():
            obj = qs.filter(supplier_id__in=sup_id)
            # obj = qs.filter(supplier_id__in=sup_id, forecast_status="1")
            return obj
        
        return qs
        # sup_id = []
        # qs = super().get_queryset(request)
        # if len(request.GET) > 0:
        #     qs = super().get_queryset(request)
        #     if request.user.is_superuser:
        #         return qs
            
        #     sup_id = []
        #     # if request.user.groups.filter(name='Supplier').exists():
        #     #     usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
        #     #     for u in usr:
        #     #         sup_id.append(u.supplier_id)
            
        #     usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
        #     for u in usr:
        #         sup_id.append(u.supplier_id)
            
        #     if request.user.groups.filter(name='Supplier').exists():
        #         # obj = qs.filter(supplier_id__in=sup_id)
        #         # return obj
        #         obj = qs.filter(supplier_id__in=sup_id, forecast_status="1")
        #         return obj

        #     return qs

        # obj = qs.filter(supplier_id__in=sup_id)
        # return obj
    
    pass

class ForecastErrorLogsAdmin(admin.ModelAdmin):
    pass

class PDSDetailInlineAdmin(admin.TabularInline):
    model = PDSDetail
    readonly_fields = (
        'forecast_detail_id',
        'seq',
        'qty',
        'price',
        'is_active',
    )
    
    fields = [
        'forecast_detail_id',
        'seq',
        'qty',
        'price',
        'is_active',
    ]
    
    extra = 2
    max_num = 5
    can_delete = False
    can_add = False
    show_change_link = False

    def has_change_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        return False
    
    pass

@admin.action(description="Mark selected to PO", permissions=['change'])
def mark_as_po(modeladmin, request, queryset):
    try:
        data = queryset
        for r in data:
            if int(r.pds_status) == 0: 
                greeter.create_purchase_order(request, r.id, "PO", "002")
    except Exception as ex:
        messages.error(request, str(ex))
        pass
    pass

class PDSHeaderAdmin(admin.ModelAdmin):
    change_form_template = "admin/open_pds_form_view.html"
    inlines = [PDSDetailInlineAdmin]
    list_display = [
        "pds_no",
        "get_pds_date",
        "get_supplier_name",
        "item",
        "qty",
        "summary_price",
        "remark",
        "status",
        "updated_at",
    ]
    
    fields = [
        "pds_no",
        "pds_date",
        "forecast_id",
        "item",
        "qty",
        "summary_price",
        "remark",
    ]
    
    readonly_fields = [
        "forecast_id",
        "pds_date",
        "pds_no",
        "item",
        "qty",
        "summary_price",
        "pds_status",
        "ref_formula_id",
        "is_active",
    ]
    
    actions = [mark_as_po]
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        
        return request.user.has_perm("forecasts.create_purchase_order")
    
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     permissions = request.user.get_all_permissions()
    #     # print(permissions)
    #     if ('forecasts.create_purchase_order' in permissions) is False:
    #         del actions['mark_as_po']
        
    #     return actions
    
    def get_pds_date(self, obj):
        return obj.pds_date.strftime("%d-%m-%Y")
    get_pds_date.short_description = "PDS Date"
    
    def get_forecast_id(self, obj):
        return obj.forecast_id
    get_forecast_id.short_description = "Purchase No."
    def get_supplier_name(self, obj):
        return obj.forecast_id.supplier_id
    get_supplier_name.short_description = "Supplier Name"
    
    
    def status(self, obj):
        try:
            data = FORECAST_ORDER_STATUS[int(obj.pds_status)]
            txtClass = "text-bold"
            if int(obj.pds_status) == 0:
                txtClass = "text-info text-bold"

            elif int(obj.pds_status) == 1:
                txtClass = "text-success text-bold"

            elif int(obj.pds_status) == 2:
                txtClass = "text-info"

            elif int(obj.pds_status) == 3:
                txtClass = "text-danger"

            elif int(obj.pds_status) == 4:
                txtClass = "text-danger"

            return format_html(f"<span class='{txtClass}'>{data[1]}</span>")
        
        except:
            pass
        return format_html(f"<span class='text-bold'>-</span>")
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        ### Get object
        obj = PDSHeader.objects.get(id=object_id)
        ### Append Variable
        extra_context['osm_data'] = obj
        if obj.pds_status is None:
            extra_context['pds_status'] = 0
        else:
            extra_context['pds_status'] = int(obj.pds_status)
            
        ### If Group is Planning check PR status
        isPo = False
        if request.user.groups.filter(name='Planning').exists():
            isPo = obj.ref_formula_id != None
    
        extra_context['send_to_po'] = isPo
        return super().change_view(request, object_id, form_url, extra_context=extra_context,)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sup_id = []
        usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
        for u in usr:
            sup_id.append(u.supplier_id)
        
        if request.user.groups.filter(name='Supplier').exists():
            obj = qs.filter(supplier_id__in=sup_id)
            # obj = qs.filter(supplier_id__in=sup_id, forecast_status="1")
            return obj
        
        return qs
    
    pass

# admin.site.unregister(FileForecast)
# admin.site.unregister(ForecastDetail)
admin.site.register(FileForecast, FileForecastAdmin)
admin.site.register(Forecast, ForecastAdmin)
# admin.site.register(ForecastDetail, ForecastDetailAdmin)
admin.site.register(ForecastErrorLogs, ForecastErrorLogsAdmin)
admin.site.register(PDSHeader, PDSHeaderAdmin)