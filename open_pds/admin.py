from django.contrib import admin
from django.contrib import admin, messages
from django.contrib.admin.sites import AdminSite
from django.utils.html import format_html
from forecasts import greeter
from rangefilter.filter import DateRangeFilter
from forecasts.models import FORECAST_ORDER_STATUS

from users.models import ManagementUser
from .models import PDSDetail, PDSHeader

# Register your models here.
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
        'seq',
        'forecast_detail_id',
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
    
    list_filter = [('pds_date', DateRangeFilter), "supplier_id", "pds_status"]
    
    actions = [mark_as_po]
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        
        return request.user.has_perm("open_pds.create_purchase_order")
    
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
        sup_id = []
        qs = super().get_queryset(request)
        if len(request.GET) > 0:
            qs = super().get_queryset(request)
            if request.user.is_superuser:
                return qs
            
            usr = ManagementUser.supplier_id.through.objects.filter(managementuser_id=request.user.id)
            for u in usr:
                sup_id.append(u.supplier_id)
            
            if request.user.groups.filter(name='Supplier').exists():
                # obj = qs.filter(supplier_id__in=sup_id)
                # return obj
                obj = qs.filter(supplier_id__in=sup_id)
                return obj

            return qs

        obj = qs.filter(supplier_id__in=sup_id)
        return obj
    
    pass

admin.site.register(PDSHeader, PDSHeaderAdmin)
