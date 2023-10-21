import calendar
import os
from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from django.forms import BaseInlineFormSet
from django.shortcuts import redirect
from django.utils.html import format_html
from admin_confirm import AdminConfirmMixin
import nanoid
import numpy as np
import pandas as pd
import requests

from books.models import ReviseBook
from formula_vcst.models import BOOK, COOR, DEPT, EMPLOYEE, PROD, SECT, UM, OrderH, OrderI
from products.models import Product, ProductGroup
from users.models import ManagementUser, PlanningForecast, Supplier
from .models import FORECAST_ORDER_STATUS, FileForecast, Forecast, ForecastDetail, ForecastErrorLogs, PDSHeader

# Register your models here.

class FileForecastAdmin(admin.ModelAdmin):
    fields = [
        'edi_file'
    ]
    
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
    ### Line Notification
    token = request.user.line_notification_id.token
    if bool(os.environ.get('DEBUG_MODE')):
        token = os.environ.get("LINE_TOKEN")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }
    
    prNoList = []
    msg = ""
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
    
    
    emp = EMPLOYEE.objects.filter(FCCODE=request.user.formula_user_id.code).values()
    dept = DEPT.objects.filter(FCCODE=request.user.department_id.code).values()
    sect = SECT.objects.filter(FCCODE=request.user.section_id.code).values()
    ordBook = BOOK.objects.filter(FCREFTYPE="PR", FCCODE="0002").values()
    
    for obj in data:
        supplier = COOR.objects.filter(FCCODE=obj.supplier_id.code).values()
        ordH = None
        if obj.ref_formula_id is None:
            ### Create PR to Formula
            # #### Create Formula OrderH
            fccode = obj.forecast_date.strftime("%Y%m%d")[3:6]
            ordRnd = OrderH.objects.filter(FCCODE__gte=fccode).count() + 1
            fccodeNo = f"{fccode}{ordRnd:04d}"
            prNo = f"{str(ordBook[0]['FCPREFIX']).strip()}{fccodeNo}"### PR TEST REFNO
            msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {prNo} เรียบร้อยแล้วคะ"
            ordH = OrderH(
                FCSKID=nanoid.generate(size=8),
                FCREFTYPE="PR",
                FCDEPT=dept[0]['FCSKID'],
                FCSECT=sect[0]['FCSKID'],
                FCBOOK=ordBook[0]['FCSKID'],
                FCCREATEBY=emp[0]['FCSKID'],
                FCAPPROVEB=emp[0]['FCSKID'],
                FCCODE=fccodeNo,
                FCREFNO=prNo,
                FCCOOR=supplier[0]['FCSKID'],
                FDDATE=obj.forecast_date,
                FDDUEDATE=obj.forecast_date,
                FNAMT=obj.forecast_qty,
            )
            ordH.save()
            obj.ref_formula_id = ordH.FCSKID
        
        else:
            ordH = OrderH.objects.get(FCSKID=obj.ref_formula_id)
            ordH.FCREFTYPE="PR"
            ordH.FCDEPT=dept[0]['FCSKID']
            ordH.FCSECT=sect[0]['FCSKID']
            ordH.FCBOOK=ordBook[0]['FCSKID']
            ordH.FCCREATEBY=emp[0]['FCSKID']
            ordH.FCAPPROVEB=emp[0]['FCSKID']
            ordH.FCCOOR=supplier[0]['FCSKID']
            ordH.FDDATE=obj.forecast_date
            ordH.FDDUEDATE=obj.forecast_date
            ordH.FNAMT=obj.forecast_qty
            ordH.save()
            pass
        
        prNoList.append(ordH.FCREFNO)
        ### OrderI
        # Get Order Details
        ordDetail = ForecastDetail.objects.filter(forecast_id=obj).all()
        seq = 1
        qty = 0
        for i in ordDetail:
            ### Create OrderI Formula
            try:
                ordProd = PROD.objects.filter(FCCODE=i.product_id.code,FCTYPE=i.product_id.prod_type_id.code).values()
                unitObj = UM.objects.filter(FCCODE=i.product_id.unit_id.code).values()
                ordI = None
                try:
                    ordI = OrderI.objects.get(FCSKID=i.ref_formula_id)
                    ordI.FCCOOR=supplier[0]['FCSKID']
                    ordI.FCDEPT=dept[0]['FCSKID']
                    ordI.FCORDERH=ordH.FCSKID
                    ordI.FCPROD=ordProd[0]["FCSKID"]
                    ordI.FCPRODTYPE=ordProd[0]["FCTYPE"]
                    ordI.FCREFTYPE="PR"
                    ordI.FCSECT=sect[0]['FCSKID']
                    ordI.FCSEQ=f"{seq:03d}"
                    ordI.FCSTUM=unitObj[0]["FCSKID"]
                    ordI.FCUM=unitObj[0]["FCSKID"]
                    ordI.FCUMSTD=unitObj[0]["FCSKID"]
                    ordI.FDDATE=obj.forecast_date
                    ordI.FNQTY=i.request_qty
                    ordI.FMREMARK=i.remark
                    #### Update Nagative to Positive
                    olderQty = int(ordI.FNBACKQTY)
                    ordI.FNBACKQTY=abs(int(i.request_qty)-olderQty)
                    ######
                    ordI.FNPRICE=ordProd[0]['FNPRICE']
                    ordI.FNPRICEKE=ordProd[0]['FNPRICE']
                    ordI.FCSHOWCOMP=""
                        
                except OrderI.DoesNotExist as e:
                    ordI = OrderI(
                        FCSKID=nanoid.generate(size=8),
                        FCCOOR=supplier[0]['FCSKID'],
                        FCDEPT=dept[0]['FCSKID'],
                        FCORDERH=ordH.FCSKID,
                        FCPROD=ordProd[0]["FCSKID"],
                        FCPRODTYPE=ordProd[0]["FCTYPE"],
                        FCREFTYPE="PR",
                        FCSECT=sect[0]['FCSKID'],
                        FCSEQ=f"{seq:03d}",
                        FCSTUM=unitObj[0]["FCSKID"],
                        FCUM=unitObj[0]["FCSKID"],
                        FCUMSTD=unitObj[0]["FCSKID"],
                        FDDATE=obj.forecast_date,
                        FNQTY=i.request_qty,
                        FMREMARK=i.remark,
                        FNBACKQTY=i.request_qty,
                        FNPRICE=ordProd[0]['FNPRICE'],
                        FNPRICEKE=ordProd[0]['FNPRICE'],
                        FCSHOWCOMP="",
                    )
                    pass
                
                ordI.save()
                # Update Status Order Details
                i.ref_formula_id = ordI.FCSKID
                i.request_status = "1"
                
            except Exception as e:
                messages.error(request, str(e))
                ordH.delete()
                return
            # Summary Seq/Qty
            seq += 1
            qty += i.request_qty
            i.save()
        
        obj.forecast_no = ordH.FCREFNO
        obj.forecast_status = "1"    
        obj.forecast_qty = qty
        obj.forecast_item = (seq - 1)
        obj.save()
        
    # queryset.update(status="p")
    msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร\n{','.join(prNoList)}\nเรียบร้อยแล้วคะ"
    response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
    print(response.text)
    
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
            # obj = qs.filter(supplier_id__in=sup_id)
            # return obj
            obj = qs.filter(supplier_id__in=sup_id, forecast_status="1")
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

class PDSHeaderAdmin(admin.ModelAdmin):
    pass

# admin.site.unregister(FileForecast)
# admin.site.unregister(ForecastDetail)
admin.site.register(FileForecast, FileForecastAdmin)
admin.site.register(Forecast, ForecastAdmin)
# admin.site.register(ForecastDetail, ForecastDetailAdmin)
admin.site.register(ForecastErrorLogs, ForecastErrorLogsAdmin)
admin.site.register(PDSHeader, PDSHeaderAdmin)