import uuid
import django
from django.db import models
from books.models import Book
from products.models import Product, ProductGroup

from users.models import ManagementUser, Section, Supplier

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
    is_generated = models.BooleanField(verbose_name="Is Generated", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.document_no
    
    class Meta:
        db_table = "ediFileUpload"
        verbose_name = "FileForecast"
        verbose_name_plural = "Upload Forecast"
        
class OpenPDS(models.Model):
    # REQUEST ORDER
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    edi_file_id = models.ForeignKey(FileForecast, verbose_name="Forecast ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    supplier_id = models.ForeignKey(Supplier, verbose_name="Supplier ID", on_delete=models.SET_NULL, null=True, blank=True)
    section_id = models.ForeignKey(Section, verbose_name="Section ID", blank=True,null=True, on_delete=models.SET_NULL)
    book_id = models.ForeignKey(Book, verbose_name="Book ID", blank=True,null=True, on_delete=models.SET_NULL)
    ro_no = models.CharField(max_length=50,verbose_name="Request No.", blank=True, null=True)
    ro_date = models.DateField(verbose_name="Request Date",  null=True, blank=True)
    ro_on_month = models.IntegerField(verbose_name="Request On Month",  null=True, blank=True, default="0")
    ro_item = models.IntegerField(verbose_name="Item", blank=True,null=True, default="0")
    ro_qty = models.FloatField(verbose_name="Qty.", blank=True,null=True, default="0")
    ro_price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    ro_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    ro_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="Request Status", default="0")
    supplier_download_count = models.IntegerField(verbose_name="Supplier Download Count", default="0", null=True, blank=True)
    ref_formula_id = models.CharField(max_length=8, verbose_name="Ref. Formula ID", blank=True, null=True)
    is_po = models.BooleanField(verbose_name="Is PO", default=False, blank=True, null=True)
    is_sync = models.BooleanField(verbose_name="Is Sync", default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ro_no
    
    class Meta:
        db_table = "ediOpenPDS"
        verbose_name = "ediOpenPDS"
        verbose_name_plural = "Open PDS"
        ordering = ('ro_status','ro_date','ro_no')
        
class OpenPDSDetail(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    request_order_id = models.ForeignKey(OpenPDS, verbose_name="Open PDS ID", blank=False, null=False, on_delete=models.CASCADE)
    product_group_id = models.ForeignKey(ProductGroup, verbose_name="Product Group ID", blank=False, null=False, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, verbose_name="Product ID", blank=False, null=False, on_delete=models.CASCADE)
    seq = models.IntegerField(verbose_name="Sequence", blank=True, null=True,default="0")
    request_qty = models.FloatField(verbose_name="Request Qty.", default="0.0")
    balance_qty = models.FloatField(verbose_name="Balance Qty.", default="0.0")
    price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    request_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    request_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="Request Status", default="0")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    is_selected = models.BooleanField(verbose_name="Is Selected", default=False)
    is_sync = models.BooleanField(verbose_name="Is Sync", default=True)
    ref_formula_id = models.CharField(max_length=8, verbose_name="Ref. Formula ID", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.seq
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        db_table = "ediOpenPDSDetail"
        verbose_name = "Open PDS Detail"
        verbose_name_plural = "Open PDS Detail"
        ordering = ('seq','product_id','created_at','updated_at')