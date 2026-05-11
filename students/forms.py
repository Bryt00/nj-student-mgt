from django import forms
from .models import Student

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select Excel file')

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'surname', 'firstname', 'other_names', 'gender', 
            'date_of_birth', 'guardian_name', 'guardian_phone', 
            'student_class', 'student_course', 'residence_status'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
