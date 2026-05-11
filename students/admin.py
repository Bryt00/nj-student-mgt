from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Student, SchoolClass, Course, Subject, House

@admin.register(House)
class HouseAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ('name', 'code', 'subject_type')
    list_filter = ('subject_type',)
    search_fields = ('name', 'code')

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    filter_horizontal = ('subjects',)

@admin.register(SchoolClass)
class SchoolClassAdmin(ModelAdmin):
    list_display = ('name', 'next_class', 'description')
    search_fields = ('name',)
    filter_horizontal = ('subjects',)

@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = ('surname', 'firstname', 'gender', 'student_class', 'student_course', 'house', 'date_of_birth')
    list_filter = ('student_class', 'student_course', 'house', 'gender', 'residence_status')
    search_fields = ('surname', 'firstname', 'guardian_name')
    actions = ["promote_students"]

    @action(description="Promote selected students to next class")
    def promote_students(self, request, queryset):
        count = 0
        for student in queryset:
            if student.student_class and student.student_class.next_class:
                student.student_class = student.student_class.next_class
                student.save()
                count += 1
        
        if count > 0:
            self.message_user(request, f"Successfully promoted {count} students.", messages.SUCCESS)
        else:
            self.message_user(request, "No students were promoted (ensure classes have 'Next Class' defined).", messages.WARNING)

    # Unfold specific enhancements
    
    # Unfold specific enhancements
    list_filter_submit = True  # Add a submit button to filters
    list_fullwidth = True      # Make the list view full width
    
    fieldsets = (
        ("Personal Information", {
            "fields": (("surname", "firstname"), "other_names", "gender", "date_of_birth"),
        }),
        ("Academic Placement", {
            "fields": (("student_class", "student_course"), ("house", "residence_status")),
        }),
        ("Emergency Contact", {
            "fields": ("guardian_name", "guardian_phone"),
        }),
    )
