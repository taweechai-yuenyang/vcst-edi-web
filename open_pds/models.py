import uuid
from django.db import models

from forecasts.models import FORECAST_ORDER_STATUS, Forecast, ForecastDetail
from users.models import Supplier

# Create your models here.
class PDSHeader(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, verbose_name="PRIMARY KEY", default=uuid.uuid4)
    forecast_id = models.ForeignKey(Forecast, verbose_name="Forecast ID", blank=False, null=False, on_delete=models.CASCADE, editable=False)
    supplier_id = models.ForeignKey(Supplier, verbose_name="Supplier ID", blank=True, null=True, on_delete=models.SET_NULL)
    pds_date = models.DateField(verbose_name="PDS Date", blank=True, null=True)
    pds_no = models.CharField(max_length=15,verbose_name="PDS No.", blank=True, null=True)
    item = models.IntegerField(verbose_name="Item")
    qty = models.FloatField(verbose_name="Qty")
    summary_price = models.FloatField(verbose_name="Summary Price", blank=True, null=True, default="0")
    remark = models.TextField(verbose_name="Remark", blank=True, null=True)
    pds_status = models.CharField(max_length=1, choices=FORECAST_ORDER_STATUS,verbose_name="PDS Status", blank=True, null=True, default="0")
    ref_formula_id = models.CharField(max_length=8, blank=True, null=True, verbose_name="Formula ID")
    is_active = models.BooleanField(verbose_name="Is Active", default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.pds_no)
    
    class Meta:
        db_table = "ediPDS"
        verbose_name = "PDS"
        verbose_name_plural = "EDI PDS"
        ordering = ('pds_status','pds_no','created_at','updated_at')
        permissions = [
            (
                "create_purchase_order",
                "เปิด PO"
            ),
            (
                "is_download_report",
                "ดูรายงาน"
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
        ordering = ('seq','forecast_detail_id','created_at','updated_at')
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
        
