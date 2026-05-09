from django.urls import path
from . import views

urlpatterns = [
    # HTML routes
    path('', views.employee_list_view, name='employee_list'),
    path('forms/', views.form_list_view, name='form_list'),
    path('forms/create/', views.form_builder_view, name='form_builder'),
    path('forms/edit/<int:pk>/', views.form_edit_view, name='form_edit'),
    path('employees/create/<int:form_id>/', views.employee_create_view, name='employee_create'),
    path('employees/edit/<int:pk>/', views.employee_edit_view, name='employee_edit'),

    # API routes
    path('api/forms/', views.EmployeeFormListAPI.as_view(), name='api_form_list'),
    path('api/forms/<int:pk>/', views.EmployeeFormDetailAPI.as_view(), name='api_form_detail'),
    path('api/employees/', views.EmployeeListAPI.as_view(), name='api_employee_list'),
    path('api/employees/<int:pk>/', views.EmployeeDetailAPI.as_view(), name='api_employee_detail'),
]