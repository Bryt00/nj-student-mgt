import uuid
from django.db import models

class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ('CORE', 'Core Subject'),
        ('ELECTIVE', 'Elective Subject'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPE_CHOICES, default='CORE')

    def __str__(self):
        return self.name

class House(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name='courses', blank=True)

    def __str__(self):
        return self.name

class SchoolClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    next_class = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_classes')
    subjects = models.ManyToManyField(Subject, related_name='classes', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "School Classes"

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    RESIDENCE_CHOICES = [
        ('Day', 'Day'),
        ('Boarder', 'Boarder'),
    ]

    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    other_names = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=20)
    student_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='students')
    student_course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='students', null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, related_name='students', null=True, blank=True)
    residence_status = models.CharField(max_length=10, choices=RESIDENCE_CHOICES, default='Day')

    def __str__(self):
        return f"{self.surname}, {self.firstname} ({self.student_class.name} - {self.residence_status})"
