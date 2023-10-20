from rest_framework import serializers
from .models import Corporation,Factory, LineNotification, PlanningForecast,Section,Position,Department,Employee,ManagementUser,Supplier



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class CorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id','corporation_id','code','name','description','is_active','created_on','updated_on',)
        
class LineNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineNotification
        fields = ('id','token','name','description','is_active','created_on','updated_on',)
        
class ManagementUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementUser
        fields = ('id','supplier_id','formula_user_id','department_id','position_id','section_id','description','avatar_url','signature_img','is_approve','is_active','created_on','updated_on',)
        
class PlanningForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningForecast
        fields = ("plan_day","plan_month","plan_year","plan_qty","revise_plan_qty","is_active",)