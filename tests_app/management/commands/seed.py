from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tests_app.models import Test, Question, Answer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding database...')

        # Create admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@lawin.uz',
                full_name='System Administrator',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin created: admin / admin123'))

        # Create test students
        students = [
            ('student1', 'Alisher Karimov', 'student1@lawin.uz'),
            ('student2', 'Nodira Rashidova', 'student2@lawin.uz'),
            ('student3', 'Bobur Yusupov', 'student3@lawin.uz'),
        ]
        for uname, fname, email in students:
            if not User.objects.filter(username=uname).exists():
                User.objects.create_user(
                    username=uname,
                    password='student123',
                    email=email,
                    full_name=fname,
                    role='abituriyent',
                )
        self.stdout.write(self.style.SUCCESS('✅ Students created: student1,2,3 / student123'))

        # Sample tests
        admin_user = User.objects.get(username='admin')

        tests_data = [
            {
                'title': 'Constitutional Law Basics',
                'description': 'Fundamental principles of constitutional law in Uzbekistan.',
                'duration_minutes': 30,
                'passing_score': 60,
                'questions': [
                    {
                        'text': 'What is the supreme law of Uzbekistan?',
                        'answers': [
                            ('Presidential decree', False, 'A'),
                            ('The Constitution', True, 'B'),
                            ('Parliamentary law', False, 'C'),
                            ('International treaties', False, 'D'),
                        ]
                    },
                    {
                        'text': 'When was the current Constitution of Uzbekistan adopted?',
                        'answers': [
                            ('1991', False, 'A'),
                            ('1993', False, 'B'),
                            ('1992', True, 'C'),
                            ('1995', False, 'D'),
                        ]
                    },
                    {
                        'text': 'How many branches of government exist in Uzbekistan?',
                        'answers': [
                            ('Two', False, 'A'),
                            ('Three', True, 'B'),
                            ('Four', False, 'C'),
                            ('Five', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What is the term of the President of Uzbekistan?',
                        'answers': [
                            ('4 years', False, 'A'),
                            ('5 years', False, 'B'),
                            ('7 years', True, 'C'),
                            ('6 years', False, 'D'),
                        ]
                    },
                    {
                        'text': 'Which body has the power to adopt constitutional laws?',
                        'answers': [
                            ('The President', False, 'A'),
                            ('The Cabinet of Ministers', False, 'B'),
                            ('The Oliy Majlis', True, 'C'),
                            ('The Supreme Court', False, 'D'),
                        ]
                    },
                ]
            },
            {
                'title': 'Civil Law Fundamentals',
                'description': 'Core concepts of civil law and legal relationships.',
                'duration_minutes': 45,
                'passing_score': 65,
                'questions': [
                    {
                        'text': 'What term refers to a person who files a civil lawsuit?',
                        'answers': [
                            ('Defendant', False, 'A'),
                            ('Witness', False, 'B'),
                            ('Plaintiff', True, 'C'),
                            ('Prosecutor', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What is a legal contract?',
                        'answers': [
                            ('A verbal agreement between friends', False, 'A'),
                            ('A legally binding agreement with offer, acceptance, and consideration', True, 'B'),
                            ('Any written document', False, 'C'),
                            ('A government regulation', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What does "tort" mean in civil law?',
                        'answers': [
                            ('A type of contract', False, 'A'),
                            ('A civil wrong causing harm or loss', True, 'B'),
                            ('A criminal offense', False, 'C'),
                            ('A property right', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What is the statute of limitations?',
                        'answers': [
                            ('A law limiting government power', False, 'A'),
                            ('A rule about court procedures', False, 'B'),
                            ('The time limit to file a legal claim', True, 'C'),
                            ('A type of penalty', False, 'D'),
                        ]
                    },
                ]
            },
            {
                'title': 'Criminal Law Essentials',
                'description': 'Introduction to criminal law principles and procedures.',
                'duration_minutes': 40,
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'What is the standard of proof in criminal cases?',
                        'answers': [
                            ('Preponderance of evidence', False, 'A'),
                            ('Clear and convincing evidence', False, 'B'),
                            ('Beyond reasonable doubt', True, 'C'),
                            ('Balance of probabilities', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What does "presumption of innocence" mean?',
                        'answers': [
                            ('The accused is considered guilty until proven innocent', False, 'A'),
                            ('The accused is considered innocent until proven guilty', True, 'B'),
                            ('The accused has no rights', False, 'C'),
                            ('The court decides guilt before trial', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What is mens rea?',
                        'answers': [
                            ('The physical act of a crime', False, 'A'),
                            ('The crime scene evidence', False, 'B'),
                            ('The guilty mind or criminal intent', True, 'C'),
                            ('The victim statement', False, 'D'),
                        ]
                    },
                    {
                        'text': 'What is actus reus?',
                        'answers': [
                            ('The criminal intent', False, 'A'),
                            ('The physical act constituting the crime', True, 'B'),
                            ('The arrest warrant', False, 'C'),
                            ('The court verdict', False, 'D'),
                        ]
                    },
                    {
                        'text': 'Which principle states that no one can be tried twice for the same crime?',
                        'answers': [
                            ('Habeas corpus', False, 'A'),
                            ('Due process', False, 'B'),
                            ('Double jeopardy', True, 'C'),
                            ('Res judicata', False, 'D'),
                        ]
                    },
                ]
            },
        ]

        for td in tests_data:
            if Test.objects.filter(title=td['title']).exists():
                continue
            test = Test.objects.create(
                title=td['title'],
                description=td['description'],
                created_by=admin_user,
                duration_minutes=td['duration_minutes'],
                passing_score=td['passing_score'],
                is_active=True,
            )
            for i, qd in enumerate(td['questions'], start=1):
                q = Question.objects.create(test=test, text=qd['text'], order=i)
                for a_text, is_correct, label in qd['answers']:
                    Answer.objects.create(question=q, text=a_text, is_correct=is_correct, label=label)

        self.stdout.write(self.style.SUCCESS('✅ Sample tests created'))
        self.stdout.write(self.style.SUCCESS('🎉 Seeding complete!'))
        self.stdout.write('')
        self.stdout.write('  Admin login:   admin / admin123')
        self.stdout.write('  Student login: student1 / student123')
