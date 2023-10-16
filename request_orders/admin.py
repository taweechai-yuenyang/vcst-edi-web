from io import BytesIO
import xlwt
import os
from django.http import HttpResponse
import nanoid
from django.contrib import admin, messages
from admin_confirm import AdminConfirmMixin
from django.utils.html import format_html
import requests

from books.models import Book, RefType, ReviseBook
from formula_vcst.models import BOOK, COOR, DEPT, EMPLOYEE, PROD, SECT, UM, OrderH, OrderI
from products.models import Product
import pandas as pd

from users.models import ManagementUser
from .models import REQUEST_ORDER_STATUS, RequestOrderDetail, UploadEDI,RequestOrder

# Register your models here.
@admin.action(description="Mark selected as Purchase Request", permissions=["change"])
def make_request_request(modeladmin, request, queryset):
    queryset.update(status="p")
    
class UploadEDIAdmin(admin.ModelAdmin):
    # fields = ('section_id', 'book_id', 'supplier_id', 'product_group_id','edi_file','upload_date','revise_id','description',)
    change_list_template = "admin/change_list_template.html"
    confirm_change = True
    confirmation_fields = ['edi_filename', 'is_generated']

    actions = [make_request_request]

    list_filter = ['is_generated', 'document_no', 'edi_filename', 'revise_id']

    list_display = ('document_no', 'revise_id', 'link_edi_file', 'uploaded_at','upload_by_id', 'is_generated', 'created_on', 'updated_on')
    # fieldsets = (
    #     (
    #         None, {
    #             "classes": ["wide", "extrapretty"],
    #             'fields': [
    #                 ('upload_date', 'revise_id'),
    #                 'supplier_id', 'edi_file', 'description',
    #             ]}
    #     ),
    # )
    fields = [
        'upload_date', 'revise_id','supplier_id', 'edi_file', 'description',
    ]
    
    def link_edi_file(self, obj):
        return format_html(f'<a href="{obj.edi_file.url}" target="_blank">{obj.edi_filename}</a>')

    # Set Overrides Message
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        pass

    # Default Book PR-0002
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
            if request.user.section_id:
                ### Check Revise Status
                obj.edi_filename = obj.edi_file.name
                # Set Section From User
                obj.section_id = request.user.section_id
                obj.book_id = rvBook.book_id
                # Set upload_by_id
                obj.upload_by_id = request.user
                # Generate Document No
                docNo = f"EDI{str(obj.upload_date.strftime('%Y%m%d'))[3:]}"
                n = UploadEDI.objects.filter(upload_on_month=int(str(obj.upload_date.strftime('%Y%m'))),supplier_id=obj.supplier_id).count()
                obj.upload_seq = n
                documentNo = f"{docNo}{(n + 1):05d}"
                obj.document_no = documentNo
                ### Set Upload on Month with Year Number
                obj.upload_on_month = int(str(obj.upload_date.strftime('%Y%m')))
                # Read Excel
                file_in_memory = request.FILES['edi_file'].read()
                data = pd.read_excel(BytesIO(file_in_memory)).to_numpy()
                addData = []
                for r in data:
                    partID = Product.objects.get(code=str(r[1]).strip())
                    addData.append({"partName": partID, "group_id": partID.prod_group_id,"qty": r[4], "remark": str(r[3]).strip()})
                    
                ### Get Revise Type
                # if int(str(obj.revise_id.code)) == 0:
                try:
                    super().save_model(request, obj, form, change)
                    for r in addData:
                        # Filter Request Order Header
                        ordID = None
                        try:
                            ordID = RequestOrder.objects.get(supplier_id=obj.supplier_id, section_id=request.user.section_id,product_group_id=r["group_id"], book_id=obj.book_id, ro_on_month = int(str(obj.upload_date.strftime('%Y%m'))))
                            if ordID.is_po is False:
                                ordID.edi_file_id=obj
                                ordID.supplier_id=obj.supplier_id
                                ordID.section_id=request.user.section_id
                                ordID.product_group_id=r["group_id"]
                                ordID.book_id=obj.book_id
                                ordID.ro_date=obj.upload_date
                                ordID.ro_on_month=obj.upload_on_month
                                ordID.ro_by_id=request.user
                                ordID.ro_status="0"
                            
                        except RequestOrder.DoesNotExist as ex:
                            rndNo = f"RO{str(obj.upload_date.strftime('%Y%m%d'))[3:]}"
                            rnd = f"{rndNo}{(RequestOrder.objects.filter(ro_no__gte=rndNo).count() + 1):05d}"
                            ordID = RequestOrder(
                                edi_file_id=obj,
                                supplier_id=obj.supplier_id,
                                section_id=request.user.section_id,
                                product_group_id=r["group_id"],
                                book_id=obj.book_id,
                                ro_no=rnd,
                                ro_date=obj.upload_date,
                                ro_on_month=obj.upload_on_month,
                                ro_by_id=request.user,
                                ro_status="0")
                            pass
                            
                        ordID.save()
                        if ordID.is_po is False:    
                            # Create Detail
                            ordDetail = None
                            try:
                                ordDetail = RequestOrderDetail.objects.get(request_order_id=ordID, product_id=r["partName"])
                                ordDetail.request_qty=r["qty"]
                                ordDetail.balance_qty=r["qty"]
                                ordDetail.request_by_id=request.user
                                ordDetail.request_status="0"
                                ordDetail.remark=f'Revise {r["remark"]}'
                                
                            except RequestOrderDetail.DoesNotExist as ex:
                                ordDetail = RequestOrderDetail(request_order_id=ordID, product_id=r["partName"], request_qty=r["qty"], balance_qty=r["qty"], request_by_id=request.user, request_status="0", remark=r["remark"])
                                pass
                            
                            ordDetail.save()
                            # Update Qty/Item Request Order
                            orderDetail = RequestOrderDetail.objects.filter(request_order_id=ordID)
                            qty = 0
                            item = 0
                            seq = 1
                            for r in orderDetail:
                                qty += r.request_qty
                                item += 1
                                
                                # Update Seq Order Seq
                                r.seq = seq
                                r.save()
                                seq += 1
                            ordID.edi_file_id = obj
                            ordID.ro_item = item
                            ordID.ro_qty = qty
                            ordID.save()
                        
                    obj.is_generated = True
                    obj.save()
                    messages.success(
                        request, f'อัพโหลดเอกสาร {obj.edi_filename} เลขที่ {documentNo} เรียบร้อยแล้ว')
                    # SendNotifiedMessage
                    docs = RequestOrder.objects.filter(edi_file_id=obj).values()
                    n = []
                    for doc in docs:
                        n.append(doc['ro_no'])
                        
                    msg = f"message=เรียนแผนก PU\nขณะนี้ทางแผนก Planning ทำการอัพโหลดเอกสาร {documentNo} จำนวน {len(n)} รายการ\nกรุณาทำการยืนยันให้ด้วยคะ"
                    response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
                    print(response.text)
                    
                except Exception as e:
                    # messages.error(request, f'เกิดข้อผิดพลาดในการอัพโหลดเอกสาร')
                    messages.error(request, str(e))
                    obj.delete()
                    
        except Exception as ex:
            messages.error(request, str(ex))

    def uploaded_at(self, obj):
        return obj.upload_date.strftime("%d-%m-%Y")

    def created_on(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")

    def updated_on(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")

    # ordering = ("code","name",)
    list_per_page = 25
    pass


class ProductRequestOrderInline(admin.TabularInline):
    model = RequestOrderDetail
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
    
    max_num = 0
    extra = 0
    can_delete = False
    can_add = False
    show_change_link = False

    def has_change_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        print(request.build_absolute_uri)
        # for i in qs:
        #     print(f"{i.request_order_id} ID: {i.id} STATUS: {i.request_status}")

        return qs.filter(request_status__lte="1")

class RequestOrderAdmin(AdminConfirmMixin, admin.ModelAdmin):
    change_form_template = 'admin/save_request_order_change_form.html'
    confirm_change = True
    confirmation_fields = ['ro_status']
    inlines = [ProductRequestOrderInline]
    # actions = [make_draff_request_order, make_purchase_request]

    list_filter = ['edi_file_id', 'supplier_id','product_group_id', 'book_id', 'ro_status']
    list_select_related = ['edi_file_id']
    search_fields = ['ro_no', 'supplier_id']
    list_per_page = 25

    list_display = [
        'ro_no',
        'get_revise_status',
        'book_id',
        'req_date',
        'product_group_id',
        'ro_item',
        'qty',
        'supplier_id',
        'status',
        'updated_on',
    ]

    fields = [
        'ro_no',
        'book_id',
        'ro_date',
        'product_group_id',
        'ro_item',
        'ro_qty',
        'supplier_id',
        'ro_status',
    ]

    def get_readonly_fields(self, request, obj):
        try:
            lst = ('product_group_id', 'supplier_id','ro_no', 'ro_item', 'ro_qty', 'ro_status',)
            if int(obj.ro_status) == 2:
                lst += ('book_id', 'ro_date',)

            return lst
        except:
            pass
        
        return ('product_group_id', 'supplier_id','ro_no', 'ro_item', 'ro_qty',)

    def status(self, obj):
        try:
            data = REQUEST_ORDER_STATUS[int(obj.ro_status)]
            txtClass = "text-bold"
            if int(obj.ro_status) == 0:
                txtClass = "text-danger text-bold"

            elif int(obj.ro_status) == 1:
                txtClass = "text-success text-bold"

            elif int(obj.ro_status) == 2:
                txtClass = "text-info"

            elif int(obj.ro_status) == 3:
                txtClass = "text-success"

            elif int(obj.ro_status) == 4:
                txtClass = "text-danger"

            return format_html(f"<span class='{txtClass}'>{data[1]}</span>")
        
        except:
            pass

    status.short_description = 'Status'

    def req_date(self, obj):
        return obj.ro_date.strftime("%d-%m-%Y")
    req_date.short_description = "Request Date"

    def created_on(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    created_on.short_description = 'Created At'

    def updated_on(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")

    def get_revise_status(self, obj):
        return f"Revise {obj.edi_file_id.upload_seq}"

    get_revise_status.short_description = 'Revise'

    def qty(self, obj):
        return f'{obj.ro_qty:,}'

    def balance(self, obj):
        return f'{obj.balance_qty:,}'

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
            
        if len(sup_id) > 0:     
            obj = qs.filter(supplier_id__in=sup_id)
            return obj

        return qs
        
    # Set Overrides Message
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        pass

    # Create Overrides Save Methods
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        ### Get object
        obj = RequestOrder.objects.get(id=object_id)
        ### Append Variable
        extra_context['osm_data'] = obj
        extra_context['ro_status'] = int(obj.ro_status)
        extra_context['ro_revise'] = obj.edi_file_id.upload_seq
        ### If Group is Planning check PR status
        isPo = False
        if request.user.groups.filter(name='Planning').exists():
            isPo = obj.ref_formula_id != None
    
        extra_context['send_to_po'] = isPo
        return super().change_view(request, object_id, form_url, extra_context=extra_context,)
    
    def response_change(self, request, obj):
        if "_approve_request_order" in request.POST:
            ### Line Notification
            token = request.user.line_notification_id.token
            if bool(os.environ.get('DEBUG_MODE')):
                token = os.environ.get("LINE_TOKEN")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {token}'
            }
            ### Message Notification
            msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {obj} เรียบร้อยแล้วคะ"
            
            emp = EMPLOYEE.objects.filter(FCCODE=request.user.formula_user_id.code).values()
            dept = DEPT.objects.filter(FCCODE=request.user.section_id.code).values()
            sect = SECT.objects.filter(FCCODE=request.user.department_id.code).values()
            ordBook = BOOK.objects.filter(FCREFTYPE="PR", FCCODE="0002").values()
            supplier = COOR.objects.filter(FCCODE=obj.supplier_id.code).values()
            ### Check Formula exits record
            ordH = None
            if obj.ref_formula_id is None:
                ### Create PR to Formula
                # #### Create Formula OrderH
                fccode = obj.ro_date.strftime("%Y%m%d")[3:6]
                ordRnd = OrderH.objects.filter(FCCODE__gte=fccode).count() + 1
                fccodeNo = f"{fccode}{ordRnd:04d}"
                prNo = f"T{str(ordBook[0]['FCPREFIX']).strip()}{fccodeNo}"### PR TEST REFNO
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
                    FDDATE=obj.ro_date,
                    FDDUEDATE=obj.ro_date,
                    FNAMT=obj.ro_qty,
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
                ordH.FDDATE=obj.ro_date
                ordH.FDDUEDATE=obj.ro_date
                ordH.FNAMT=obj.ro_qty
                ordH.save()
                msg = f"message=เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {ordH.FCREFNO} เรียบร้อยแล้วคะ"
                pass
            
            ### OrderI
            # Get Order Details
            ordDetail = RequestOrderDetail.objects.filter(request_order_id=obj).all()
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
                        ordI.FDDATE=obj.ro_date
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
                            FDDATE=obj.ro_date,
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
            
            obj.ro_no = ordH.FCREFNO
            obj.ro_status = "1"    
            obj.ro_qty = qty
            obj.ro_item = (seq - 1)
            response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
            print(response.text)
            obj.save()
            
        return super().response_change(request, object)
    pass


admin.site.register(UploadEDI, UploadEDIAdmin)
admin.site.register(RequestOrder, RequestOrderAdmin)