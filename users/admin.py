from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Corporation,Factory, LineNotification,Section,Position,Department,Employee,ManagementUser,Supplier

# Register your models here.
class CorporationAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'code',
        'name',
    )
    
    list_filter = ('is_active',)
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    pass

class FactoryAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'code',
        'name',
    )
    
    list_filter = ('is_active',)
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    pass

class SectionAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'code',
        'name',
    )
    
    list_filter = ('is_active',)
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    pass

class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'code',
        'name',
    )
    
    list_filter = ('is_active',)
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    pass

class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'code',
        'name',
    )
    
    list_filter = ('is_active',)
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    pass

class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'description',
        'is_active',
        'created_on',
        'updated_on',
    ]
    
    list_filter = ['corporation_id','is_active',]
    search_fields = ['code','name',]
    pass

class ManagementUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name','position_id','department_id', 'section_id', 'is_staff')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('formula_user_id','position_id','department_id', 'section_id','line_notification_id','is_approve','avatar_url','signature_img', 'description')
        })
    )
    
    def save_model(self, request, obj, form, change):
        # if obj.position_id is None:
        #     pos = Position.objects.get(code="-")
        #     obj.position_id = pos
        
        if obj.line_notification_id is None:
            pos = LineNotification.objects.get(name="TEST")
            obj.line_notification_id = pos
        
        if obj.formula_user_id is None:
            pos = Employee.objects.get(code="TEST")
            obj.formula_user_id = pos
            
        if obj.department_id is None:
            dp = Department.objects.get(code="-")
            obj.department_id = dp
            
        if obj.section_id  is None:
            sp = Section.objects.get(code="-")
            obj.section_id = sp
            
        return super().save_model(request, obj, form, change)
    
    pass

class SupplierAdmin(admin.ModelAdmin):
    # change_list_template = "admin/change_list.html"
    # form = SupplierForm
    
    list_display = (
        # 'skid',
        'code',
        'name',
        # 'user_id',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'name',
        'code',
    )
    
    list_filter = (
        'is_active',
        'user_id',
    )
    
    # list_editable = (
    #     'code',
    #     'name',
    #     'is_active',
    # )
    
    fieldsets = (
        ("", {
            "fields": (
                ("user_id",),
                ("code",),
                ("name",),
                ("description",),
                "is_active",
                ),
        }),
    )
    
    # fieldsets = (
    #     ("ข้อมูลผู้ใช้งาน", {
    #         "fields": ("user_id",)
    #     }),
        
    #     ("รายละเอียดเพิ่มเติม", {
    #         "fields": (
    #             ("skid",),
    #             ("code",),
    #             ("name",),
    #             ("description",),
    #             "is_active",
    #             ),
    #     }),
    # )
    
    # ordering = ("code","name",)
    list_per_page = 25
    
    def created_at(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def updated_at(self, obj):
        # return obj.updated_on.strftime("%d %b %Y %H:%M:%S")
        return obj.updated_on.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        isStaff = False
        query_set = Group.objects.filter(user = request.user)
        for g in query_set:
            if g.name.find("VCS") >= 0:
                isStaff = True
                break

        if isStaff:
            return qs

        return qs.filter(user_id=request.user)
    
    pass

class LineNotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Corporation, CorporationAdmin,)
admin.site.register(Factory, FactoryAdmin,)
admin.site.register(Section, SectionAdmin,)
admin.site.register(Position, PositionAdmin,)
admin.site.register(Department, DepartmentAdmin,)
admin.site.register(Employee, EmployeeAdmin,)
admin.site.register(ManagementUser, ManagementUserAdmin,)
admin.site.register(Supplier, SupplierAdmin,)
admin.site.register(LineNotification, LineNotificationAdmin)