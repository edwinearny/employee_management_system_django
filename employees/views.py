from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
from django.db.models import Q

from .models import EmployeeForm, FormField, Employee, EmployeeFieldValue
from .serializers import EmployeeFormSerializer, EmployeeSerializer


# ──────────────────────────────────────────
# HTML VIEWS
# ──────────────────────────────────────────

@login_required
def form_builder_view(request):
    """Page to create a new dynamic form"""
    return render(request, 'employees/form_builder.html')


@login_required
def form_list_view(request):
    """List all forms created by the user"""
    forms = EmployeeForm.objects.filter(created_by=request.user)
    return render(request, 'employees/form_list.html', {'forms': forms})


@login_required
def form_edit_view(request, pk):
    """Page to edit an existing form"""
    form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
    return render(request, 'employees/form_builder.html', {'form': form})


# ──────────────────────────────────────────
# REST API VIEWS
# ──────────────────────────────────────────

class EmployeeFormListAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all forms"""
        forms = EmployeeForm.objects.filter(created_by=request.user)
        serializer = EmployeeFormSerializer(forms, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new form with its fields"""
        name = request.data.get('name')
        fields = request.data.get('fields', [])

        if not name:
            return Response({'error': 'Form name is required'}, status=400)

        form = EmployeeForm.objects.create(name=name, created_by=request.user)

        for i, field in enumerate(fields):
            FormField.objects.create(
                form=form,
                label=field['label'],
                field_type=field['field_type'],
                order=i
            )

        serializer = EmployeeFormSerializer(form)
        return Response(serializer.data, status=201)


class EmployeeFormDetailAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get a single form with its fields"""
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        serializer = EmployeeFormSerializer(form)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update form name and fields"""
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        name = request.data.get('name')
        fields = request.data.get('fields', [])

        if name:
            form.name = name
            form.save()

        # delete old fields and recreate (simplest approach)
        form.fields.all().delete()
        for i, field in enumerate(fields):
            FormField.objects.create(
                form=form,
                label=field['label'],
                field_type=field['field_type'],
                order=i
            )

        serializer = EmployeeFormSerializer(form)
        return Response(serializer.data)

    def delete(self, request, pk):
        """Delete a form"""
        form = get_object_or_404(EmployeeForm, pk=pk, created_by=request.user)
        form.delete()
        return Response({'message': 'Form deleted'}, status=204)

# ──────────────────────────────────────────
# EMPLOYEE HTML VIEWS
# ──────────────────────────────────────────

@login_required
def employee_create_view(request, form_id):
    """Page to create a new employee using a specific form"""
    employee_form = get_object_or_404(EmployeeForm, pk=form_id, created_by=request.user)
    return render(request, 'employees/employee_form.html', {
        'employee_form': employee_form,
        'employee': None
    })


@login_required
def employee_edit_view(request, pk):
    """Page to edit an existing employee"""
    employee = get_object_or_404(Employee, pk=pk)
    employee_form = employee.form
    return render(request, 'employees/employee_form.html', {
        'employee_form': employee_form,
        'employee': employee
    })


@login_required
def employee_list_view(request):
    """List all employees with search"""
    query = request.GET.get('q', '')
    employees = Employee.objects.all()

    if query:
        employees = employees.filter(
            field_values__value__icontains=query
        ).distinct()

    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'query': query
    })


# ──────────────────────────────────────────
# EMPLOYEE REST API VIEWS
# ──────────────────────────────────────────

class EmployeeListAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        employees = Employee.objects.all()
        if query:
            employees = employees.filter(
                field_values__value__icontains=query
            ).distinct()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        form_id = request.data.get('form')
        field_values = request.data.get('field_values', [])

        employee_form = get_object_or_404(EmployeeForm, pk=form_id)
        employee = Employee.objects.create(form=employee_form)

        for fv in field_values:
            field = get_object_or_404(FormField, pk=fv['field'])
            EmployeeFieldValue.objects.create(
                employee=employee,
                field=field,
                value=fv['value']
            )

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=201)


class EmployeeDetailAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        field_values = request.data.get('field_values', [])

        for fv in field_values:
            field = get_object_or_404(FormField, pk=fv['field'])
            obj, _ = EmployeeFieldValue.objects.get_or_create(
                employee=employee, field=field
            )
            obj.value = fv['value']
            obj.save()

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response({'message': 'Employee deleted'}, status=204)