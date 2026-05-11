import random
from django.core.management.base import BaseCommand
from students.models import Student, SchoolClass, Course, Subject, House
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Reseeds with Houses and Grouped Subjects'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing data...")
        Student.objects.all().delete()
        SchoolClass.objects.all().delete()
        Course.objects.all().delete()
        Subject.objects.all().delete()
        House.objects.all().delete()

        self.stdout.write("Creating houses...")
        house_names = ['Aggrey', 'Guggisberg', 'Fraser', 'Casely Hayford']
        created_houses = [House.objects.create(name=n) for n in house_names]

        self.stdout.write("Creating subjects...")
        core_subjects = [
            ('Core Mathematics', 'C-MATH'),
            ('English Language', 'ENG'),
            ('Integrated Science', 'INT-SCI'),
            ('Social Studies', 'SOC-ST'),
        ]
        
        elective_subjects = {
            'S': [('Physics', 'PHY'), ('Chemistry', 'CHE'), ('Biology', 'BIO'), ('Elective Maths', 'E-MATH')],
            'B': [('Financial Accounting', 'ACC'), ('Business Management', 'B-MGMT'), ('Economics', 'ECON'), ('Cost Accounting', 'COST')],
            'GA': [('Government', 'GOV'), ('Literature in English', 'LIT'), ('Christian Religious Studies', 'CRS'), ('History', 'HIST')],
            'V': [('Graphic Design', 'GRAPH'), ('Ceramics', 'CER'), ('General Knowledge in Art', 'GKA'), ('Picture Making', 'PIC')],
            'H': [('Food and Nutrition', 'FOOD'), ('Management in Living', 'MIL'), ('Textiles', 'TEX'), ('Clothing and Textiles', 'CLOTH')],
            'AG': [('General Agriculture', 'G-AGRI'), ('Animal Husbandry', 'ANIMAL'), ('Crop Husbandry', 'CROP'), ('Chemistry', 'CHE')],
        }

        created_core = [Subject.objects.create(name=n, code=c, subject_type='CORE') for n, c in core_subjects]
        
        created_electives = {}
        for code, subjs in elective_subjects.items():
            created_electives[code] = [Subject.objects.get_or_create(name=n, code=c, subject_type='ELECTIVE')[0] for n, c in subjs]

        self.stdout.write("Creating courses and linking subjects...")
        courses_data = [
            ('Agricultural Science', 'AG'),
            ('Visual Arts', 'V'),
            ('General Arts', 'GA'),
            ('Business', 'B'),
            ('Home Economics', 'H'),
            ('General Science', 'S'),
        ]
        
        course_map = {}
        for name, code in courses_data:
            c = Course.objects.create(name=name, code=code)
            c.subjects.add(*created_core)
            if code in created_electives:
                c.subjects.add(*created_electives[code])
            course_map[code] = c

        self.stdout.write("Creating classes using course templates...")
        years = [1, 2, 3]
        streams = [1, 2]
        class_objects = {}
        
        for year in years:
            for code, course_obj in course_map.items():
                for stream in streams:
                    name = f"{year} {code} {stream}"
                    cls = SchoolClass.objects.create(name=name, course=course_obj)
                    cls.subjects.add(*course_obj.subjects.all())
                    class_objects[name] = cls

        self.stdout.write("Setting up promotion paths...")
        for name, cls in class_objects.items():
            parts = name.split()
            year = int(parts[0])
            if year < 3:
                next_name = f"{year + 1} {parts[1]} {parts[2]}"
                if next_name in class_objects:
                    cls.next_class = class_objects[next_name]
                    cls.save()

        self.stdout.write("Seeding students...")
        surnames = ['Appiah', 'Mensah', 'Owusu', 'Boateng', 'Kojo', 'Adu', 'Sarpong', 'Quansah', 'Asare', 'Danquah', 'Osei', 'Kyeremeh', 'Baffour', 'Donkor']
        firstnames_m = ['Kwame', 'Kofi', 'Yaw', 'Kweku', 'Kwesi', 'Kojo', 'Kwabena', 'Emmanuel', 'Samuel', 'John']
        firstnames_f = ['Ama', 'Efua', 'Abena', 'Akua', 'Yaa', 'Afua', 'Araba', 'Elizabeth', 'Mary', 'Theresa']
        residence_statuses = ['Day', 'Boarder']

        students_to_create = []
        all_classes = list(class_objects.values())

        for _ in range(150):
            gender = random.choice(['M', 'F'])
            firstname = random.choice(firstnames_m) if gender == 'M' else random.choice(firstnames_f)
            surname = random.choice(surnames)
            
            selected_class = random.choice(all_classes)
            selected_course = selected_class.course
            selected_house = random.choice(created_houses)
            
            residence = random.choice(residence_statuses)
            age = 14 + int(selected_class.name.split()[0])
            dob = date.today() - timedelta(days=age*365 + random.randint(0, 365))

            student = Student(
                surname=surname,
                firstname=firstname,
                gender=gender,
                date_of_birth=dob,
                guardian_name=f"{surname} {random.choice(['Snr', 'Sr', 'Elder'])}",
                guardian_phone=f"024{random.randint(1000000, 9999999)}",
                student_class=selected_class,
                student_course=selected_course,
                house=selected_house,
                residence_status=residence
            )
            students_to_create.append(student)

        Student.objects.bulk_create(students_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully reseeded 150 students with Houses and categorized subjects.'))
