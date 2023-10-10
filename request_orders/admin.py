from io import BytesIO
import os
from django.contrib import admin, messages
from admin_confirm import AdminConfirmMixin
from django.utils.html import format_html
import requests

from books.models import Book, RefType
from products.models import Product
import pandas as pd
from .models import REQUEST_ORDER_STATUS, RequestOrderDetail, UploadEDI,RequestOrder

# Register your models here.
@admin.action(description="Mark selected as Purchase Request", permissions=["change"])
def make_request_request(modeladmin, request, queryset):
    queryset.update(status="p")
    
class UploadEDIAdmin(admin.ModelAdmin):
    # fields = ('section_id', 'book_id', 'supplier_id', 'product_group_id','edi_file','upload_date','revise_id','description',)
    confirm_change = True
    confirmation_fields = ['edi_filename', 'is_generated']

    actions = [make_request_request]

    list_filter = ['is_generated', 'document_no', 'edi_filename', 'revise_id']

    list_display = ('document_no', 'revise_id', 'link_edi_file', 'uploaded_at','upload_by_id', 'is_generated', 'created_on', 'updated_on')
    fieldsets = (
        (
            None, {
                "classes": ["wide", "extrapretty"],
                'fields': [
                    ('upload_date', 'revise_id'),
                    'supplier_id', 'edi_file', 'description',
                ]}
        ),
    )
    
    def link_edi_file(self, obj):
        return format_html(f'<a href="{obj.edi_file.url}" target="_blank">{obj.edi_filename}</a>')

    # Set Overrides Message
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        pass

    # Default Book PR-0002
    def save_model(self, request, obj, form, change):
        if request.user.section_id:
            obj.edi_filename = obj.edi_file.name
            # Set Section From User
            obj.section_id = request.user.section_id
            # Set Book From Default
            ordType = RefType.objects.get(code=r"PR")
            book = Book.objects.get(order_type_id=ordType, code=r'0002')
            obj.book_id = book
            # Set upload_by_id
            obj.upload_by_id = request.user
            # Generate Document No
            docNo = f"EDI{str(obj.upload_date.strftime('%Y%m%d'))[3:]}"
            n = UploadEDI.objects.filter(document_no__gte={docNo}).count()
            documentNo = f"{docNo}{(n + 1):05d}"
            obj.document_no = documentNo
            # Read Excel
            file_in_memory = request.FILES['edi_file'].read()
            data = pd.read_excel(BytesIO(file_in_memory)).to_numpy()
            addData = []
            for r in data:
                # if float(r[5]) > 0:
                #     partID = Product.objects.get(code=str(r[3]).strip())
                #     addData.append({"partName": partID, "group_id": partID.prod_group_id,"qty": r[5], "remark": str(r[1]).strip()})
                partID = Product.objects.get(code=str(r[3]).strip())
                addData.append({"partName": partID, "group_id": partID.prod_group_id,"qty": r[5], "remark": str(r[1]).strip()})

            # show Message
            try:
                super().save_model(request, obj, form, change)
                for r in addData:
                    # Filter Request Order Header
                    ordID = None
                    try:
                        ordID = RequestOrder.objects.get(supplier_id=obj.supplier_id, section_id=request.user.section_id,product_group_id=r["group_id"], book_id=obj.book_id, ro_date=obj.upload_date)
                    except Exception as e:
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
                            ro_by_id=request.user,
                            ro_status="0")
                        ordID.save()
                        pass

                    # Create Detail
                    ordDetail = RequestOrderDetail(request_order_id=ordID, product_id=r["partName"], request_qty=r["qty"], balance_qty=r["qty"], request_by_id=request.user, request_status="0", remark=r["remark"])
                    ordDetail.save()

                    # Update Qty/Item Request Order
                    orderDetail = RequestOrderDetail.objects.filter(
                        request_order_id=ordID)
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
                
                
                token = request.user.line_notification_id.token
                if bool(os.environ.get('DEBUG_MODE')):
                    token = os.environ.get("LINE_TOKEN")
                    
                msg = f"message=เรียนแผนก PU\nขณะนี้ทางแผนก Planning ทำการอัพโหลดเอกสาร {documentNo} จำนวน {len(n)} รายการ\nกรุณาทำการยืนยันให้ด้วยคะ"
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Bearer {token}'
                }
                response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
                print(response.text)
                
            except Exception as e:
                # messages.error(request, f'เกิดข้อผิดพลาดในการอัพโหลดเอกสาร')
                messages.error(request, str(e))
                obj.delete()
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลส่วนตัวของท่านด้วย")

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
    show_change_link = True

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
        lst = ('product_group_id', 'supplier_id','ro_no', 'ro_item', 'ro_qty', 'ro_status',)
        if int(obj.ro_status) == 2:
            lst += ('book_id', 'ro_date',)

        return lst

    def status(self, obj):
        data = REQUEST_ORDER_STATUS[int(obj.ro_status)]
        txtClass = "text-danger"
        if int(obj.ro_status) == 0:
            txtClass = "text-primary"

        elif int(obj.ro_status) == 1:
            txtClass = "text-info"

        elif int(obj.ro_status) == 2:
            txtClass = "text-success"

        elif int(obj.ro_status) == 3:
            txtClass = "text-danger"

        elif int(obj.ro_status) == 4:
            txtClass = "text-info"

        return format_html(f"<span class='{txtClass}'>{data[1]}</span>")

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
        return obj.edi_file_id.revise_id

    get_revise_status.short_description = 'Revise'

    def qty(self, obj):
        return f'{obj.ro_qty:,}'

    def balance(self, obj):
        return f'{obj.balance_qty:,}'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    # Set Overrides Message
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        pass

    # Create Overrides Save Methods
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)
    
    def response_change(self, request, obj):
        if "_approve_request_order" in request.POST:
            msg = f"เรียนแผนก Planning\nขณะนี้ทางแผนก PU ได้ทำการอนุมัติเอกสาร {obj} เรียบร้อยแล้ว\nรบกวนทางแผนก Planning ทำการอัพโหลดเอกสาร Revise 1 ด้วยคะ"
            token = request.user.line_notification_id.token
            if bool(os.environ.get('DEBUG_MODE')):
                token = os.environ.get("LINE_TOKEN")
                
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {token}'
            }
            response = requests.request("POST", "https://notify-api.line.me/api/notify", headers=headers, data=msg.encode("utf-8"))
            print(response.text)
            
        return super().response_change(request, object)
    pass


admin.site.register(UploadEDI, UploadEDIAdmin)
admin.site.register(RequestOrder, RequestOrderAdmin)