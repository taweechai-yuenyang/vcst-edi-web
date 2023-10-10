from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Corporation, Department, Employee, Factory, LineNotification, Position,Section, Supplier
from .serializers import CorporationSerializer, DepartmentSerializer, EmployeeSerializer, FactorySerializer, LineNotificationSerializer, PositionSerializer, SectionSerializer, SupplierSerializer


class SupplierListApiView(APIView):
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
            obj = Supplier.objects.get(id=id)
            serializer = SupplierSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Supplier.objects.all()
        serializer = SupplierSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.error_messages)
        print(serializer.is_valid())
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. Update
    def put(self, request, *args, **kwargs):
        '''
        Update the Todo with given todo data
        '''

        id = self.request.query_params.get('id')
        if id:
            try:
                Supplier = Supplier.objects.get(id=id)
                Supplier.skid = request.data.get("skid")
                Supplier.code = request.data.get("code")
                Supplier.name = request.data.get("name")
                Supplier.description = request.data.get("description")
                Supplier.save()
                return Response(status=status.HTTP_200_OK)
            
            except:
                pass
        

            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 4. Delete
    def delete(self, request, *args, **kwargs):
        '''
        Delete the Todo with given id
        '''
        id = self.request.query_params.get('id')
        if id:
            Supplier = Supplier.objects.get(id=id)
            Supplier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)

class FactoryListApiView(APIView):
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
            obj = Factory.objects.get(id=id)
            serializer = FactorySerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Factory.objects.all()
        serializer = FactorySerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = FactorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CorporationListApiView(APIView):
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
            obj = Corporation.objects.get(id=id)
            serializer = CorporationSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Corporation.objects.all()
        serializer = CorporationSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = CorporationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SectionListApiView(APIView):
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
            obj = Section.objects.get(id=id)
            serializer = SectionSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Section.objects.all()
        serializer = SectionSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PositionListApiView(APIView):
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
            obj = Position.objects.get(id=id)
            serializer = PositionSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Position.objects.all()
        serializer = PositionSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DepartmentListApiView(APIView):
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
            obj = Department.objects.get(id=id)
            serializer = DepartmentSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Department.objects.all()
        serializer = DepartmentSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EmployeeListApiView(APIView):
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
            obj = Employee.objects.get(id=id)
            serializer = EmployeeSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = Employee.objects.all()
        serializer = EmployeeSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        corp = Corporation.objects.get(name=request.data.get('corporation_id'))
        obj = request.POST.copy()
        obj['corporation_id'] = corp.id
        serializer = EmployeeSerializer(data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LineNotificationListApiView(APIView):
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
            obj = LineNotification.objects.get(id=id)
            serializer = LineNotificationSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        obj = LineNotification.objects.all()
        serializer = LineNotificationSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        obj = request.POST.copy()
        serializer = LineNotificationSerializer(data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)