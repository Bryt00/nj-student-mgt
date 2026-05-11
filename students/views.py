import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .forms import ExcelUploadForm, StudentForm
from .models import Student, SchoolClass, Course, House
from django.db.models import Count
from django.db import models
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_report_pdf(request):
    # Reuse filtering logic from dashboard
    students = Student.objects.all().select_related('student_class', 'student_course', 'house')
    
    class_filter = request.GET.get('class')
    course_filter = request.GET.get('course')
    gender_filter = request.GET.get('gender')
    residence_filter = request.GET.get('residence_status')
    age_filter = request.GET.get('age_range')
    search_query = request.GET.get('search')

    if class_filter: students = students.filter(student_class__name=class_filter)
    if course_filter: students = students.filter(student_course__name=course_filter)
    if gender_filter: students = students.filter(gender=gender_filter)
    if residence_filter: students = students.filter(residence_status=residence_filter)
    
    if age_filter:
        from datetime import date
        today = date.today()
        if age_filter == '14-15':
            students = students.filter(date_of_birth__range=[today.replace(year=today.year-16), today.replace(year=today.year-14)])
        elif age_filter == '16-17':
            students = students.filter(date_of_birth__range=[today.replace(year=today.year-18), today.replace(year=today.year-16)])
        elif age_filter == '18+':
            students = students.filter(date_of_birth__lte=today.replace(year=today.year-18))

    if search_query:
        students = students.filter(
            models.Q(surname__icontains=search_query) | 
            models.Q(firstname__icontains=search_query) |
            models.Q(guardian_name__icontains=search_query)
        )

    context = {
        'students': students,
        'count': students.count(),
        'generated_at': models.DateTimeField().auto_now_add
    }
    
    template = get_template('students/report_pdf.html')
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})

def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/edit_student.html', {'form': form, 'student': student})

def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('dashboard')
    return render(request, 'students/delete_confirm.html', {'student': student})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('dashboard')
    else:
        form = StudentForm()
    return render(request, 'students/add_student.html', {'form': form})

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                # Read the excel file
                df = pd.read_excel(excel_file)
                
                # Check if required columns exist (based on the user's specific order)
                # surname, firstname, other_names, Gender (M/F), date_of_birth, guardian_name, guardian_phone, class_name
                
                # We can either use column names or indices. Since the user gave a specific order, 
                # let's assume the columns are in that order if names don't match.
                # However, pandas usually reads the first row as headers.
                
                students_to_create = []
                for _, row in df.iterrows():
                    # Map the row to Student model
                    # Using row.iloc for index-based access if headers are unknown, 
                    # but let's try to be flexible.
                    
                    try:
                        # Find or create the SchoolClass
                        class_obj, _ = SchoolClass.objects.get_or_create(name=str(row[7]))
                        
                        # Find or create Course if provided (index 9)
                        course_obj = None
                        if len(row) > 9 and pd.notna(row[9]):
                            course_obj, _ = Course.objects.get_or_create(name=str(row[9]))
                        
                        # Find or create House if provided (index 10)
                        house_obj = None
                        if len(row) > 10 and pd.notna(row[10]):
                            house_obj, _ = House.objects.get_or_create(name=str(row[10]))

                        student = Student(
                            surname=row[0],
                            firstname=row[1],
                            other_names=row[2] if pd.notna(row[2]) else None,
                            gender=row[3],
                            date_of_birth=pd.to_datetime(row[4]).date(),
                            guardian_name=row[5],
                            guardian_phone=row[6],
                            student_class=class_obj,
                            student_course=course_obj,
                            house=house_obj,
                            residence_status=row[8] if len(row) > 8 and pd.notna(row[8]) else 'Day'
                        )
                        students_to_create.append(student)
                    except Exception as e:
                        messages.warning(request, f"Error processing row: {e}")
                        continue
                
                if students_to_create:
                    Student.objects.bulk_create(students_to_create)
                    messages.success(request, f"Successfully uploaded {len(students_to_create)} students.")
                else:
                    messages.error(request, "No valid data found in the file.")
                
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error reading excel file: {e}")
    else:
        form = ExcelUploadForm()
    
    return render(request, 'students/upload.html', {'form': form})

def get_filtered_students(request):
    students = Student.objects.all()
    class_filter = request.GET.get('class_name')
    course_filter = request.GET.get('course_name')
    gender_filter = request.GET.get('gender')
    residence_filter = request.GET.get('residence_status')
    search_query = request.GET.get('search')
    age_filter = request.GET.get('age_range')

    if class_filter:
        students = students.filter(student_class__name=class_filter)
    if course_filter:
        students = students.filter(student_course__name=course_filter)
    if gender_filter:
        students = students.filter(gender=gender_filter)
    if residence_filter:
        students = students.filter(residence_status=residence_filter)
    
    if age_filter:
        from datetime import date
        today = date.today()
        if age_filter == '14-15':
            students = students.filter(date_of_birth__range=[today.replace(year=today.year-16), today.replace(year=today.year-14)])
        elif age_filter == '16-17':
            students = students.filter(date_of_birth__range=[today.replace(year=today.year-18), today.replace(year=today.year-16)])
        elif age_filter == '18+':
            students = students.filter(date_of_birth__lte=today.replace(year=today.year-18))
    if search_query:
        students = students.filter(
            models.Q(surname__icontains=search_query) | 
            models.Q(firstname__icontains=search_query)
        )
    return students

def export_students_csv(request):
    students = get_filtered_students(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'

    # Custom header mapping
    data = []
    for s in students:
        data.append({
            'Surname': s.surname,
            'First Name': s.firstname,
            'Other Names': s.other_names,
            'Gender': s.get_gender_display(),
            'Date of Birth': s.date_of_birth,
            'Guardian Name': s.guardian_name,
            'Guardian Phone': s.guardian_phone,
            'Class': s.student_class.name,
            'Course': s.student_course.name if s.student_course else 'N/A',
            'Residence Status': s.residence_status,
        })
    df = pd.DataFrame(data)
    df.to_csv(path_or_buf=response, index=False)
    return response

def export_students_excel(request):
    students = get_filtered_students(request)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students_export.xlsx"'

    data = []
    for s in students:
        data.append({
            'Surname': s.surname,
            'First Name': s.firstname,
            'Other Names': s.other_names,
            'Gender': s.get_gender_display(),
            'Date of Birth': s.date_of_birth,
            'Guardian Name': s.guardian_name,
            'Guardian Phone': s.guardian_phone,
            'Class': s.student_class.name,
            'Course': s.student_course.name if s.student_course else 'N/A',
            'Residence Status': s.residence_status,
        })
    df = pd.DataFrame(data)
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return response

from django.core.paginator import Paginator

def dashboard(request):
    # Get filtered students
    students = get_filtered_students(request).order_by('surname', 'firstname')
    
    # Filtering query params for context
    class_filter = request.GET.get('class_name')
    course_filter = request.GET.get('course_name')
    gender_filter = request.GET.get('gender')
    residence_filter = request.GET.get('residence_status')
    search_query = request.GET.get('search')
    age_filter = request.GET.get('age_range')

    # Simple filtering counts
    total_count = students.count()
    
    # Counts by class, course, gender, and residence status (of the filtered set)
    stats_list = students.values('student_class__name', 'student_course__name', 'gender', 'residence_status').annotate(total=Count('id')).order_by('student_class__name')
    
    # Paginate stats list (10 per page)
    stats_paginator = Paginator(stats_list, 10)
    stats_page_number = request.GET.get('stats_page')
    stats_page_obj = stats_paginator.get_page(stats_page_number)
    
    # Aggregated counts by Course Code (S, B, AG, etc.)
    course_stats = students.values('student_course__code').annotate(total=Count('id')).order_by('student_course__code')

    # Aggregated counts by House
    house_stats = students.values('house__name').annotate(total=Count('id')).order_by('house__name')
    
    # Explicit totals for progress bars (avoiding queryset state issues)
    male_count = students.filter(gender='M').count()
    female_count = students.filter(gender='F').count()
    boarder_count = students.filter(residence_status='Boarder').count()
    day_count = students.filter(residence_status='Day').count()

    from datetime import date
    today = date.today()
    total_14_15 = students.filter(date_of_birth__range=[today.replace(year=today.year-16), today.replace(year=today.year-14)]).count()
    total_16_17 = students.filter(date_of_birth__range=[today.replace(year=today.year-18), today.replace(year=today.year-16)]).count()
    total_18_plus = students.filter(date_of_birth__lte=today.replace(year=today.year-18)).count()
    
    # Pagination
    paginator = Paginator(students, 10) # 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    classes = SchoolClass.objects.values_list('name', flat=True).distinct().order_by('name')
    courses = Course.objects.values_list('name', flat=True).distinct().order_by('name')

    return render(request, 'students/dashboard.html', {
        'page_obj': page_obj,
        'total_count': total_count,
        'stats_page_obj': stats_page_obj,
        'course_stats': course_stats,
        'house_stats': house_stats,
        'male_count': male_count,
        'female_count': female_count,
        'boarder_count': boarder_count,
        'day_count': day_count,
        'total_14_15': total_14_15,
        'total_16_17': total_16_17,
        'total_18_plus': total_18_plus,
        'classes': classes,
        'courses': courses,
        'class_filter': class_filter,
        'course_filter': course_filter,
        'gender_filter': gender_filter,
        'residence_filter': residence_filter,
        'search_query': search_query,
        'age_filter': age_filter,
        'age_ranges': ['14-15', '16-17', '18+'],
    })
