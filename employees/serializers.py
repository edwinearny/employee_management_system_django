from rest_framework import serializers
from .models import EmployeeForm, FormField, Employee, EmployeeFieldValue


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'order']


class EmployeeFormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeForm
        fields = ['id', 'name', 'fields', 'created_at']


class EmployeeFieldValueSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(source='field.label', read_only=True)
    field_type = serializers.CharField(source='field.field_type', read_only=True)

    class Meta:
        model = EmployeeFieldValue
        fields = ['id', 'field', 'field_label', 'field_type', 'value']


class EmployeeSerializer(serializers.ModelSerializer):
    field_values = EmployeeFieldValueSerializer(many=True, read_only=True)
    form_name = serializers.CharField(source='form.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'form', 'form_name', 'field_values', 'created_at']