from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProductGroup, Product, ProductType, Unit
from .serializers import ProductGroupSerializer, ProductTypeSerializer,UnitSerializer,ProductSerializer


class ProductTypeListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # Supplier = Supplier.objects.filter(user = request.user.id)
        id = self.request.query_params.get('id')
        if id:
            obj = ProductType.objects.get(id=id)
            serializer = ProductTypeSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = ProductType.objects.all()
        serializer = ProductTypeSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = ProductTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductGroupListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # Supplier = Supplier.objects.filter(user = request.user.id)
        id = self.request.query_params.get('id')
        if id:
            obj = ProductGroup.objects.get(id=id)
            serializer = ProductGroupSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = ProductGroup.objects.all()
        serializer = ProductGroupSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = ProductGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnitListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # Supplier = Supplier.objects.filter(user = request.user.id)
        id = self.request.query_params.get('id')
        if id:
            obj = Unit.objects.get(id=id)
            serializer = UnitSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Unit.objects.all()
        serializer = UnitSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = UnitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # Supplier = Supplier.objects.filter(user = request.user.id)
        id = self.request.query_params.get('id')
        if id:
            obj = Product.objects.get(id=id)
            serializer = ProductSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Product.objects.all()
        serializer = ProductSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        pGrp = ProductGroup.objects.get(code=request.data.get('prod_group_id'))
        pType = ProductType.objects.get(code=request.data.get('prod_type_id'))
        pUnit = Unit.objects.get(code=request.data.get('unit_id'))
        obj = request.POST.copy()
        obj['prod_type_id'] = pType.id
        obj['prod_group_id'] = pGrp.id
        obj['unit_id'] = pUnit.id
        
        try:
            prodID = Product.objects.get(code=request.data.get('code'))
            prodID.prod_type_id = pType
            prodID.prod_group_id = pGrp
            prodID.unit_id = pUnit
            prodID.no = request.data.get('no')
            prodID.name = request.data.get('name')
            prodID.price = request.data.get('price')
            prodID.description = request.data.get('description')
            prodID.save()
            return Response(None, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            serializer = ProductSerializer(data=obj)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print(f"Error ==>")
        print(obj)
        print(serializer.error_messages)
        print(f"<==")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)