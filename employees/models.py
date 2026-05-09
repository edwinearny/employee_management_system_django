from django.db import models
from django.contrib.auth.models import User


class EmployeeForm(models.Model):  # dynamic form (just a name/title)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FormField(models.Model):  # Each field (label + type)
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('password', 'Password'),
        ('email', 'Email'),
        ('textarea', 'Textarea'),
    ]

    form = models.ForeignKey(EmployeeForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    order = models.PositiveIntegerField(default=0)  # for drag-and-drop ordering

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class Employee(models.Model):  #employee record created using specific form
    form = models.ForeignKey(EmployeeForm, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee #{self.id}"


class EmployeeFieldValue(models.Model):  # actual values submitted for each field of an employee record
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='field_values')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value = models.TextField(blank=True)

    def __str__(self):
        return f"{self.field.label}: {self.value}"
