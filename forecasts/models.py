import uuid
import django
from django.db import models
from books.models import Book
from products.models import Product

from users.models import ManagementUser, PlanningForecast, Section, Supplier

# Create your models here.
FORECAST_ORDER_STATUS = [
    ('0', 'In Progress'),
    ('1', 'Approve'),
    ('2', 'Success'),
    ('3', 'Reject')
]

class FileForecast(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    edi_file = models.FileField(upload_to='static/edi/%Y-%m-%d/', verbose_name="File Forecast", null=False, blank=False)
    edi_filename = models.CharField(max_length=150,verbose_name="File Forecast",blank=True, null=True)
    document_no = models.CharField(max_length=150,verbose_name="Document No.",blank=True, null=True, editable=False)
    upload_date = models.DateField(verbose_name="Upload On",blank=True, null=True ,default=django.utils.timezone.now)
    upload_on_month = models.IntegerField(verbose_name="Upload On Month",default="0", null=True, blank=True)
    upload_seq = models.IntegerField(verbose_name="Upload Seq", null=True, blank=True, default="0")
    description = models.TextField(verbose_name="Description",blank=True, null=True)
    upload_by_id = models.ForeignKey(ManagementUser, verbose_name="Upload By ID", blank=True, null=True, on_delete=models.SET_NULL, editable=False)
    is_generated = models.BooleanField(verbose_name="Is Generated", default=False,blank=True, null=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=False,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.document_no
    
    class Meta:
        db_table = "ediFileUpload"
        verbose_name = "Upload"
        verbose_name_plural = "Upload Forecast"
        permissions = [
            (
                "add_file",
                "อัพโหลดข้อมูล"
            )
        ]
        
class Forecast(models.Model):
    # REQUEST ORDER
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    forecast_plan_id = models.ForeignKey(PlanningForecast, blank=True, null=True, on_delete=models.SET_NULL)
    edi_file_id = models.ForeignKey(FileForecast, verbose_name="Forecast ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    supplier_id = models.ForeignKey(Supplier, verbose_name="Supplier ID", on_delete=models.SET_NULL, null=True, blank=True)
    section_id = models.ForeignKey(Section, verbose_name="Section ID", blank=True,null=True, on_delete=models.SET_NULL)
    book_id = models.ForeignKey(Book, verbose_name="Book ID", blank=True,null=True, on_delete=models.SET_NULL)
    forecast_no = models.CharField(max_length=15,verbose_name="Request No.", blank=True, null=True)
    forecast_date = models.DateField(verbose_name="Request Date",  null=True, blank=True)
    forecast_on_month = models.IntegerField(verbose_name="Request On Month",  null=True, blank=True, default="0")
    forecast_item = models.IntegerField(verbose_name="Item", blank=True,null=True, default="0")
    forecast_qty = models.FloatField(verbose_name="Qty.", blank=True,null=True, default="0")
    forecast_price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    forecast_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    forecast_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="Request Status", default="0")
    supplier_download_count = models.IntegerField(verbose_name="Supplier Download Count", default="0", null=True, blank=True)
    ref_formula_id = models.CharField(max_length=8, verbose_name="Ref. Formula ID", blank=True, null=True)
    is_po = models.BooleanField(verbose_name="Is PO", default=False, blank=True, null=True)
    is_sync = models.BooleanField(verbose_name="Is Sync", default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.forecast_no
    
    class Meta:
        db_table = "ediForecast"
        verbose_name = "Forecast"
        verbose_name_plural = "Upload Forecast"
        ordering = ('forecast_status','forecast_date','forecast_no')
        permissions = [
            (
                "approve_reject",
                "Approve/Reject"
            )
        ]
        
class ForecastDetail(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    forecast_id = models.ForeignKey(Forecast, verbose_name="Open PDS ID", blank=False, null=False, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, verbose_name="Product ID", blank=False, null=False, on_delete=models.CASCADE)
    seq = models.IntegerField(verbose_name="Sequence", blank=True, null=True,default="0")
    request_qty = models.FloatField(verbose_name="Request Qty.", default="0.0")
    balance_qty = models.FloatField(verbose_name="Balance Qty.", default="0.0")
    price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    request_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    request_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="Request Status", default="0")
    import_model_by_user = models.CharField(max_length=255, blank=True, null=True)
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    is_selected = models.BooleanField(verbose_name="Is Selected", default=False)
    is_sync = models.BooleanField(verbose_name="Is Sync", default=True)
    ref_formula_id = models.CharField(max_length=8, verbose_name="Ref. Formula ID", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.product_id.code)
    
    class Meta:
        db_table = "ediForecastDetail"
        verbose_name = "ForecastDetail"
        verbose_name_plural = "Forecast Detail"
        ordering = ('seq','product_id','created_at','updated_at')
        permissions = [
            (
                "edit_qty_price",
                "แก้ไขจำนวนและราคา"
            ),
            (
                "select_item",
                "เลือกรายการสินค้า"
            )
        ]
        
class ForecastErrorLogs(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    file_name = models.UUIDField(max_length=36, verbose_name="File Forecast")
    row_num = models.IntegerField(verbose_name="Row")
    item = models.IntegerField(verbose_name="Item")
    part_code = models.CharField(max_length=50, verbose_name="Part Code")
    part_no = models.CharField(max_length=50, verbose_name="Part No.")
    part_name = models.CharField(max_length=50, verbose_name="Part Name")
    supplier = models.CharField(max_length=50, verbose_name="Supplier")
    model = models.CharField(max_length=50, verbose_name="Model")
    rev_0 = models.IntegerField(verbose_name="Rev.0",default=0, blank=True, null=True)
    rev_1 = models.IntegerField(verbose_name="Rev.1",default=0, blank=True, null=True)
    rev_2 = models.IntegerField(verbose_name="Rev.2",default=0, blank=True, null=True)
    rev_3 = models.IntegerField(verbose_name="Rev.3",default=0, blank=True, null=True)
    rev_4 = models.IntegerField(verbose_name="Rev.4",default=0, blank=True, null=True)
    rev_5 = models.IntegerField(verbose_name="Rev.5",default=0, blank=True, null=True)
    rev_6 = models.IntegerField(verbose_name="Rev.6",default=0, blank=True, null=True)
    rev_7 = models.IntegerField(verbose_name="Rev.7",default=0, blank=True, null=True)
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    is_error = models.BooleanField(verbose_name="Is Error", default=True, blank=True, null=True)
    is_success = models.BooleanField(verbose_name="Is Success", default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "ediForecastErrorLogs"
        verbose_name = "PDS Error Logging"
        verbose_name_plural = "PDS Error Logging"
        ordering = ('row_num','item','created_at','updated_at')
        
class PDSHeader(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    forecast_id = models.ForeignKey(Forecast, verbose_name="Forecast ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    pds_date = models.DateField(verbose_name="PDS Date", blank=True, null=True)
    pds_no = models.CharField(max_length=10,verbose_name="PDS No.", blank=True, null=True)
    item = models.IntegerField(verbose_name="Item")
    qty = models.FloatField(verbose_name="Qty")
    summary_price = models.FloatField(verbose_name="Summary Price", blank=True, null=True, default="0")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    pds_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="PDS Status", blank=True, null=True, default="0")
    ref_formula_id = models.CharField(max_length=8, blank=True, null=True, verbose_name="Formula ID")
    is_active = models.BooleanField(verbose_name="Is Active", default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "ediPDS"
        verbose_name = "PDS"
        verbose_name_plural = "Open PDS"
        ordering = ('pds_status','pds_no','created_at','updated_at')
        permissions = [
            (
                "create_purchase_order",
                "เปิด PO"
            )
        ]
        
class PDSDetail(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    pds_header_id = models.ForeignKey(PDSHeader, verbose_name="PDS ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    forecast_detail_id = models.ForeignKey(ForecastDetail, verbose_name="PDS Detail", on_delete=models.CASCADE)
    seq = models.IntegerField(verbose_name="Seq.")
    qty = models.FloatField(verbose_name="Qty")
    price = models.FloatField(verbose_name="Price", blank=True, null=True, default="0")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    ref_formula_id = models.CharField(max_length=8, blank=True, null=True, verbose_name="Formula ID")
    is_active = models.BooleanField(verbose_name="Is Active", default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.forecast_detail_id)
    
    class Meta:
        db_table = "ediPDSDetail"
        verbose_name = "PDSDetail"
        verbose_name_plural = "PDS Detail"
        # ordering = ('row_num','item','created_at','updated_at')
        permissions = [
            (
                "create_purchase_order",
                "เปิด PO"
            ),
            (
                "edit_purchase_qty_price",
                "แก้ไขจำนวน/ราคา"
            )
        ]