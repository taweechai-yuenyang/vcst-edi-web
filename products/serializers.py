from rest_framework import serializers
from .models import ProductGroup,ProductType, Product, Unit

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id','code','name','description','is_active','created_on','updated_on',)

class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = ('id','code','name','description','is_active','created_on','updated_on',)

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id','prod_type_id','prod_group_id','unit_id','code','no','name','description','is_active','created_on','updated_on',)
