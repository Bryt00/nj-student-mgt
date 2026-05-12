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
        help_texts = {
            'guardian_phone': 'Enter exactly 10 digits (e.g., 0244123456)',
        }

    def clean_guardian_phone(self):
        phone = self.cleaned_data.get('guardian_phone')
        if phone and len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone
