from rest_framework import serializers
from .models import Book, Corporation, Factory, RefType, ProductType, EDIReviseType, ReviseBook

class ReviseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIReviseType
        fields = ('id',"code",'name','description','is_active','created_on','updated_on',)
    

class RefTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefType
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
    
class CorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
        
class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ('id','code','name','description','is_active','created_on','updated_on',)
    
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id','skid', 'corporation_id', 'order_type_id','code','name','prefix','description','is_active','created_on','updated_on',)
        
class ReviseBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviseBook
        fields = ('id','ref_type_id','book_id','name','description','is_active','created_on','updated_on',)