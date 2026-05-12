from django.core.management.base import BaseCommand
from dashboard.models import College

class Command(BaseCommand):
    help = 'Populate college statistics with actual data'

    def handle(self, *args, **options):
        # Define college data with the statistics you want
        colleges_data = [
            {
                'name': 'College of Arts & Sciences',
                'abbreviation': 'CAS',
                'dean': 'Dr. Maria Santos',
                'total_students': 1935,
                'programs_offered': 2,
                'qualified_instructors': 37,
                'status': 'active',
                'description': 'The College of Arts & Sciences offers programs in Information Technology and Computer Science, providing students with cutting-edge knowledge in digital technologies and computational thinking.',
                'hero_description': 'Leading innovation in technology and sciences for the digital age',
                'about': 'The College of Arts & Sciences is committed to excellence in education, research, and community service. We prepare students to become leaders in their chosen fields through comprehensive academic programs and hands-on learning experiences.',
                'vision': 'To be a premier college in arts and sciences, recognized for excellence in teaching, research, and community engagement.',
                'mission': 'To provide quality education that develops competent professionals and leaders equipped with knowledge, skills, and values for global competitiveness.',
                'goals': ['Excellence', 'Innovation', 'Integrity', 'Service']
            },
            {
                'name': 'College of Industrial Technology',
                'abbreviation': 'CIT',
                'dean': 'Dr. Jose Reyes',
                'total_students': 1935,
                'programs_offered': 2,
                'qualified_instructors': 37,
                'status': 'active',
                'description': 'The College of Industrial Technology focuses on technical and industrial education, preparing students for careers in various industrial and technological fields.',
                'hero_description': 'Building the future through industrial technology and innovation',
                'about': 'CIT is dedicated to providing high-quality technical education that meets industry standards and addresses the needs of the modern workforce.',
                'vision': 'To be a center of excellence in industrial technology education and research.',
                'mission': 'To produce competent technologists and innovators who contribute to industrial development.',
                'goals': ['Technology', 'Innovation', 'Skills', 'Industry']
            },
            {
                'name': 'College of Teacher Education',
                'abbreviation': 'CTED',
                'dean': 'Dr. Elena Cruz',
                'total_students': 1935,
                'programs_offered': 2,
                'qualified_instructors': 37,
                'status': 'active',
                'description': 'The College of Teacher Education prepares future educators through comprehensive programs in elementary and secondary education.',
                'hero_description': 'Shaping the future through quality teacher education',
                'about': 'CTED is committed to producing competent, compassionate, and innovative teachers who can make a difference in the lives of learners.',
                'vision': 'To be a leading institution in teacher education and educational research.',
                'mission': 'To develop exemplary educators who are catalysts for positive change in society.',
                'goals': ['Excellence', 'Service', 'Leadership', 'Innovation']
            },
            {
                'name': 'College of Criminal Justice Education',
                'abbreviation': 'CCJE',
                'dean': 'Dr. Roberto Morales',
                'total_students': 1935,
                'programs_offered': 2,
                'qualified_instructors': 37,
                'status': 'active',
                'description': 'The College of Criminal Justice Education offers comprehensive programs in criminology and criminal justice.',
                'hero_description': 'Upholding justice and public safety through quality education',
                'about': 'CCJE is dedicated to producing competent criminal justice professionals who uphold the rule of law and serve with integrity.',
                'vision': 'To be a premier institution in criminal justice education and research.',
                'mission': 'To develop ethical and competent criminal justice professionals.',
                'goals': ['Justice', 'Integrity', 'Service', 'Excellence']
            },
            {
                'name': 'College of Business Administration',
                'abbreviation': 'CBA',
                'dean': 'Dr. Patricia Lim',
                'total_students': 1935,
                'programs_offered': 3,
                'qualified_instructors': 37,
                'status': 'active',
                'description': 'The College of Business Administration offers programs in Hospitality Management, Business Administration, and Office Administration.',
                'hero_description': 'Developing business leaders and entrepreneurs for the global economy',
                'about': 'CBA is committed to providing quality business education that prepares students for leadership roles in various business sectors.',
                'vision': 'To be a center of excellence in business education and entrepreneurship.',
                'mission': 'To produce competent business professionals and entrepreneurs with global competitiveness.',
                'goals': ['Leadership', 'Innovation', 'Ethics', 'Excellence']
            },
            {
                'name': 'College of Agriculture & Forestry',
                'abbreviation': 'CAF',
                'dean': 'Dr. Fernando Garcia',
                'total_students': 1935,
                'programs_offered': 1,
                'qualified_instructors': 40,
                'status': 'active',
                'description': 'The College of Agriculture & Forestry focuses on sustainable agriculture and forestry practices.',
                'hero_description': 'Promoting sustainable agriculture and environmental stewardship',
                'about': 'CAF is dedicated to advancing agricultural and forestry sciences through education, research, and community service.',
                'vision': 'To be a leader in agricultural and forestry education and sustainable development.',
                'mission': 'To develop professionals who contribute to food security and environmental sustainability.',
                'goals': ['Sustainability', 'Innovation', 'Research', 'Service']
            }
        ]

        # Clear existing colleges
        College.objects.all().delete()
        self.stdout.write('Cleared existing college data')

        # Create colleges with new data
        for college_data in colleges_data:
            college = College.objects.create(**college_data)
            self.stdout.write(f'Created: {college.name}')

        # Calculate and display totals
        total_colleges = College.objects.count()
        total_students = sum(college.total_students for college in College.objects.all())
        total_instructors = sum(college.qualified_instructors for college in College.objects.all())
        total_programs = sum(college.programs_offered for college in College.objects.all())

        self.stdout.write('\n=== Summary ===')
        self.stdout.write(f'Total Colleges: {total_colleges}')
        self.stdout.write(f'Total Students: {total_students}')
        self.stdout.write(f'Total Instructors: {total_instructors}')
        self.stdout.write(f'Total Programs: {total_programs}')
        self.stdout.write('\nCollege statistics populated successfully!')
