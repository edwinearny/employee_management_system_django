from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import EmployeeForm, FormField, Employee, EmployeeFieldValue
from .serializers import EmployeeFormSerializer, EmployeeSerializer


auth = [SessionAuthentication, JWTAuthentication]


@login_required
def form_builder_view(request):
    return render(request, 'employees/form_builder.html')


@login_required
def form_list_view(request):
    forms = EmployeeForm.objects.filter(created_by=request.user)
    return render(request, 'employees/form_list.html', {'forms': forms})


@login_required
def form_edit_view(request, pk):
    form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
    return render(request, 'employees/form_builder.html', {'form': form})


@login_required
def employee_create_view(request, form_id):
    employee_form = get_object_or_404(EmployeeForm, pk=form_id, created_by=request.user)
    return render(request, 'employees/employee_form.html', {'employee_form': employee_form, 'employee': None})


@login_required
def employee_edit_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_form.html', {'employee_form': employee.form, 'employee': employee})


@login_required
def employee_list_view(request):
    return render(request, 'employees/employee_list.html', {'employees': Employee.objects.all()})


class EmployeeFormListAPI(APIView):
    authentication_classes = auth
    permission_classes = [IsAuthenticated]

    def get(self, request):
        forms = EmployeeForm.objects.filter(created_by=request.user)
        return Response(EmployeeFormSerializer(forms, many=True).data)

    def post(self, request):
        name = request.data.get('name')
        fields = request.data.get('fields', [])

        if not name:
            return Response({'error': 'Form name is required'}, status=400)

        form = EmployeeForm.objects.create(name=name, created_by=request.user)
        for i, f in enumerate(fields):
            FormField.objects.create(form=form, label=f['label'], field_type=f['field_type'], order=i)

        return Response(EmployeeFormSerializer(form).data, status=201)


class EmployeeFormDetailAPI(APIView):
    authentication_classes = auth
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        return Response(EmployeeFormSerializer(form).data)

    def put(self, request, pk):
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        if request.data.get('name'):
            form.name = request.data.get('name')
            form.save()

        form.fields.all().delete()
        for i, f in enumerate(request.data.get('fields', [])):
            FormField.objects.create(form=form, label=f['label'], field_type=f['field_type'], order=i)

        return Response(EmployeeFormSerializer(form).data)

    def delete(self, request, pk):
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        form.delete()
        return Response({'message': 'Form deleted'}, status=204)


class EmployeeListAPI(APIView):
    authentication_classes = auth
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(EmployeeSerializer(Employee.objects.all(), many=True).data)

    def post(self, request):
        employee_form = get_object_or_404(EmployeeForm, pk=request.data.get('form'))
        employee = Employee.objects.create(form=employee_form)

        for fv in request.data.get('field_values', []):
            EmployeeFieldValue.objects.create(
                employee=employee,
                field=get_object_or_404(FormField, pk=fv['field']),
                value=fv['value']
            )

        return Response(EmployeeSerializer(employee).data, status=201)


class EmployeeDetailAPI(APIView):
    authentication_classes = auth
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        return Response(EmployeeSerializer(get_object_or_404(Employee, pk=pk)).data)

    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        for fv in request.data.get('field_values', []):
            obj, _ = EmployeeFieldValue.objects.get_or_create(
                employee=employee,
                field=get_object_or_404(FormField, pk=fv['field'])
            )
            obj.value = fv['value']
            obj.save()
        return Response(EmployeeSerializer(employee).data)

    def delete(self, request, pk):
        get_object_or_404(Employee, pk=pk).delete()
        return Response({'message': 'Employee deleted'}, status=204)