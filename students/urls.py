from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('add/', views.add_student, name='add_student'),
    path('student/<uuid:pk>/', views.student_detail, name='student_detail'),
    path('student/<uuid:pk>/edit/', views.edit_student, name='edit_student'),
    path('student/<uuid:pk>/delete/', views.delete_student, name='delete_student'),
    path('export/csv/', views.export_students_csv, name='export_students_csv'),
    path('export/excel/', views.export_students_excel, name='export_excel'),
    path('export/pdf/', views.generate_report_pdf, name='generate_pdf'),
]
