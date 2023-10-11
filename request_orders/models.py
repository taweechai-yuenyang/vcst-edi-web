import uuid
import django
from django.db import models
from books.models import Book, EDIReviseType
from products.models import Product, ProductGroup

from users.models import ManagementUser, Section, Supplier

REQUEST_ORDER_STATUS = [
    ('0', 'Wait Approve'),
    ('1', 'Wait Rv1.'),
    ('2', 'Approve'),
    ('3', 'Reject'),
    ('4', 'Success'),
    ('5', 'Cancel'),
]

# Create your models here.
class UploadEDI(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    section_id = models.ForeignKey(Section, verbose_name="Section ID", blank=True,null=True, on_delete=models.SET_NULL)
    revise_id = models.ForeignKey(EDIReviseType, verbose_name="Revise Type ID", blank=True,null=True, on_delete=models.SET_NULL)
    book_id = models.ForeignKey(Book, verbose_name="Book ID", blank=True,null=True, on_delete=models.SET_NULL)
    supplier_id = models.ForeignKey(Supplier, verbose_name="Supplier ID", blank=False, on_delete=models.CASCADE)
    edi_file = models.FileField(upload_to='static/edi/%Y-%m-%d/', verbose_name="FILE EDI", null=False, blank=False)
    edi_filename = models.CharField(max_length=150,verbose_name="FILE EDI",blank=True, null=True)
    document_no = models.CharField(max_length=150,verbose_name="Document No.",blank=True, null=True, editable=False)
    upload_date = models.DateField(verbose_name="Upload On",default=django.utils.timezone.now)
    upload_on_month = models.IntegerField(verbose_name="Upload On Month",default="0", null=True, blank=True)
    description = models.TextField(verbose_name="Description",blank=True, null=True)
    upload_by_id = models.ForeignKey(ManagementUser, verbose_name="Upload By ID", blank=True, null=True, on_delete=models.SET_NULL, editable=False)
    is_generated = models.BooleanField(verbose_name="Is Generated", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.document_no
    
    class Meta:
        db_table = "ediFileUpload"
        verbose_name = "FileEDI"
        verbose_name_plural = "1.Upload File EDI"
        

class RequestOrder(models.Model):
    # REQUEST ORDER
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    edi_file_id = models.ForeignKey(UploadEDI, verbose_name="EDI File ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    supplier_id = models.ForeignKey(Supplier, verbose_name="Supplier ID", on_delete=models.SET_NULL, null=True, blank=True)
    section_id = models.ForeignKey(Section, verbose_name="Section ID", blank=True,null=True, on_delete=models.SET_NULL)
    product_group_id = models.ForeignKey(ProductGroup, verbose_name="Model ID", on_delete=models.SET_NULL, null=True, blank=True)
    book_id = models.ForeignKey(Book, verbose_name="Book ID", blank=True,null=True, on_delete=models.SET_NULL)
    ro_no = models.CharField(max_length=50,verbose_name="Request No.", blank=True, null=True)
    ro_date = models.DateField(verbose_name="Request Date",  null=True, blank=True)
    ro_on_month = models.IntegerField(verbose_name="Request On Month",  null=True, blank=True, default="0")
    ro_item = models.IntegerField(verbose_name="Item", blank=True,null=True, default="0")
    ro_qty = models.FloatField(verbose_name="Qty.", blank=True,null=True, default="0")
    ro_price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    ro_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    ro_status = models.CharField(max_length=1, choices=REQUEST_ORDER_STATUS,verbose_name="Request Status", default="0")
    supplier_download_count = models.IntegerField(verbose_name="Supplier Download Count", default="0", null=True, blank=True)
    ref_formula_id = models.CharField(max_length=8, verbose_name="Ref. Formula ID", blank=True, null=True)
    is_sync = models.BooleanField(verbose_name="Is Sync", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ro_no
    
    class Meta:
        db_table = "ediRO"
        verbose_name = "RO"
        verbose_name_plural = "2.Request Order"
        ordering = ('ro_status','ro_date','ro_no')
        
class RequestOrderDetail(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    request_order_id = models.ForeignKey(RequestOrder, verbose_name="Request ID", blank=False, null=False, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, verbose_name="Product ID", blank=False, null=False, on_delete=models.CASCADE)
    seq = models.IntegerField(verbose_name="Sequence", blank=True, null=True,default="0")
    request_qty = models.FloatField(verbose_name="Request Qty.", default="0.0")
    balance_qty = models.FloatField(verbose_name="Balance Qty.", default="0.0")
    price = models.FloatField(verbose_name="Price.", blank=True,null=True, default="0")
    request_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    request_status = models.CharField(max_length=1, choices=REQUEST_ORDER_STATUS,verbose_name="Request Status", default="0")
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
        db_table = "ediRODetail"
        verbose_name = "RO Detail"
        verbose_name_plural = "Request Order Detail"
        ordering = ('seq','product_id','created_at','updated_at')
        
class ApproveRequestOrder(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    request_order_id = models.ForeignKey(RequestOrder, verbose_name="Request ID", blank=False, null=False, on_delete=models.CASCADE)
    request_by_id = models.ForeignKey(ManagementUser, verbose_name="Request By ID", blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    request_status = models.CharField(max_length=1, choices=REQUEST_ORDER_STATUS,verbose_name="Request Status", default="0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "ediROApprove"
        verbose_name = "Approve RO"
        verbose_name_plural = "Approve Request Order"