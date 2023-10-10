from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Corporation
from .models import Book, EDIReviseType, RefType
from .serializers import BookSerializer, ReviseTypeSerializer, RefTypeSerializer

class ReviseTypeListApiView(APIView):
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
            obj = EDIReviseType.objects.get(id=id)
            serializer = ReviseTypeSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = EDIReviseType.objects.all()
        serializer = ReviseTypeSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = ReviseTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RefTypeListApiView(APIView):
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
            obj = RefType.objects.get(id=id)
            serializer = RefTypeSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = RefType.objects.all()
        serializer = RefTypeSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = RefTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookListApiView(APIView):
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
            obj = Book.objects.get(id=id)
            serializer = BookSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Book.objects.all()
        serializer = BookSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        ordType = RefType.objects.get(code=request.data.get('order_type_id'))
        corpType = Corporation.objects.get(name=request.data.get('corporation_id'))
        obj = request.POST.copy()
        obj['order_type_id'] = ordType.id
        obj['corporation_id'] = corpType.id
        
        
        serializer = BookSerializer(data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)