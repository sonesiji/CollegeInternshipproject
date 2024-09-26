from django.shortcuts import render, redirect , get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm





# Create your views here.
def index(request):
    return render (request,'index.html')

def about(request):
    return render (request,'about.html')

# gemini_integration/views.py
from django.shortcuts import render
from .utils import get_gemini_data

def show_gemini_data(request):
    # Replace 'example_endpoint' with the actual endpoint you need
    data = get_gemini_data('example_endpoint')
    return render(request, 'gemini_integration/show_data.html', {'data': data})

def register(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = StudentForm()

    return render(request, 'register.html', {'form': form})

def thanks(request):
    return render(request, 'thanks.html')


def approval(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        action = request.POST['action']
        student = Student.objects.get(id=student_id)

        if action == 'approve':
            student.is_approved = True
            student.save()

            # Send an email to the student
            send_mail(
                'Your registration has been approved',
                'Your User Name is {} and your password is {}.'.format(student.roll_number, student.password),
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )

        elif action == 'reject':
            student.delete()

    students = Student.objects.filter(is_approved=False)
    return render(request, 'approval.html', {'students': students})

def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'approve':
            student.is_approved = True
            student.save()

            send_mail(
                'Your registration has been approved',
                'Your User Name is {} and your password is {}.'.format(student.roll_number, student.password),
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )
            return redirect('approval')

        elif action == 'reject':
            student.delete()
            return redirect('approval')

    return render(request, 'student_detail.html', {'student': student})
 



def mark_attendance(request):
    students = Student.objects.filter(is_approved=True)
    date = request.POST.get('date')
    attendance_marked = Attendance.objects.filter(date=date).exists()

    if request.method == 'POST' and not attendance_marked:
        for student in students:
            is_present = request.POST.get(student.roll_number) == 'Present'
            Attendance.objects.create(student=student, date=date, is_present=is_present)
    return render(request, 'mark_attendance.html', {'students': students,'attendance_marked': attendance_marked})



   
def staff_dashboard(request):
    students = Student.objects.filter(is_approved=True)
    student_attendance = []
    for student in students:
        total_present = Attendance.objects.filter(student=student, is_present=True).count()
        total_absent = Attendance.objects.filter(student=student, is_present=False).count()
        total = total_present + total_absent
        if total > 0:
            percentage = round((total_present / total) * 100)
        else:
            percentage = 0
        student_attendance.append((student, total_present, total_absent, percentage))
    return render(request, 'staff_dashboard.html', {'student_attendance': student_attendance})




def student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendances = Attendance.objects.filter(student=student)
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    return render(request, 'student_view.html', {'student': student, 'total_present': total_present, 'total_absent': total_absent, 'attendances': attendances})


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('students_list')
    return render(request, 'confirm_delete.html', {'student': student})

def attendance_details(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        attendances = Attendance.objects.filter(date=date)
        present_students = [attendance.student for attendance in attendances if attendance.is_present]
        absent_students = [attendance.student for attendance in attendances if not attendance.is_present]
    else:
        date = request.GET.get('date')
        if date:
            attendances = Attendance.objects.filter(date=date)
            present_students = [attendance.student for attendance in attendances if attendance.is_present]
            absent_students = [attendance.student for attendance in attendances if not attendance.is_present]
        else:
            attendances = []
            present_students = []
            absent_students = []
    return render(request, 'attendance_details.html', {'present_students': present_students, 'absent_students': absent_students, 'date': date})



def edit_attendance(request, date):
    attendances = Attendance.objects.filter(date=date)
    if request.method == 'POST':
        for attendance in attendances:
            form = AttendanceForm(request.POST, instance=attendance, prefix=str(attendance.id))
            if form.is_valid():
                form.save()
        return redirect('attendance_details')
    else:
        forms = [AttendanceForm(instance=attendance, prefix=str(attendance.id)) for attendance in attendances]
    return render(request, 'edit_attendance.html', {'forms': forms, 'date': date})

def student_dashboard(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    total_present = Attendance.objects.filter(student=student, is_present=True).count()
    total_absent = Attendance.objects.filter(student=student, is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    return render(request, 'student_dashboard.html', {'student': student, 'total_present': total_present, 'total_absent': total_absent, 'percentage': percentage})


class s_student_detail(UpdateView):
    model = Student
    fields = ['name', 'email','contact', 'parent_name', 'gender', 'date_of_birth', 'student_image'] 
    template_name = 's_student_detail.html'

    def get_success_url(self):
        return reverse_lazy('student_dashboard', kwargs={'student_id': self.object.id})


def s_attendance_detail(request, student_id):
    # get the student object by id
    student = get_object_or_404(Student, id=student_id)
    # get the attendance queryset and sort it by date
    attendances = Attendance.objects.filter(student=student).order_by('date')
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    # pass the sorted attendances to the template context
    context = {
        'student': student,
        'attendances': attendances,
        'total_present': total_present,
        'total_absent': total_absent,
        'percentage': percentage,
    }
    return render(request, 's_attendance_detail.html', context)

def st_attendance_detail(request, student_id):
    # get the student object by id
    student = get_object_or_404(Student, id=student_id)
    # get the attendance queryset and sort it by date
    attendances = Attendance.objects.filter(student=student).order_by('date')
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    # pass the sorted attendances to the template context
    context = {
        'student': student,
        'attendances': attendances,
        'total_present': total_present,
        'total_absent': total_absent,
        'percentage': percentage,
    }
    return render(request, 'st_attendance_detail.html', context)



def student_login(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(roll_number=roll_number, password=password)
            if not student.is_approved:
                messages.error(request, "Your account has not been approved yet. Please contact the administrator.")
                return render(request, 'login.html')
            # Redirect to a profile page or any other page after successful login
            # For now, redirecting to a success message
            return redirect('student_dashboard', student_id=student.id)  # Replace 'success_page' with your desired URL name
        except Student.DoesNotExist:
            messages.error(request, "Invalid roll number or password. Please try again.")

    return render(request, 'login.html')





def students_list(request):
    students = Student.objects.filter(is_approved=True)
    return render(request, 'students_list.html', {'students': students})

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('staff_dashboard')
            else:
                return render(request, 'admin_login.html', {'form': form, 'error_message': 'Invalid credentials'})

    else:
        form = AuthenticationForm()

    return render(request, 'admin_login.html', {'form': form})





# views.py
from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai

# Configure API key
api_key = "AIzaSyCBHJzNyEhusj_bDljUkTvKYQU95hgcDag"
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_text(request):
    if request.method == 'POST':
        user_input = request.POST.get('input_text', '')
        if user_input:
            try:
                # Call generate_content
                response = model.generate_content(user_input)
                # Access the text directly if it's an attribute
                generated_text = response.text if hasattr(response, 'text') else 'No text found'
                return JsonResponse({'generated_text': generated_text})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'No input text provided'}, status=400)
    return render(request, 'generate_text.html')



# from django.shortcuts import render

# def visualization(request):
#     students = Student.objects.filter(is_approved=True)
#     student_attendance = []
#     for student in students:
#         total_present = Attendance.objects.filter(student=student, is_present=True).count()
#         total_absent = Attendance.objects.filter(student=student, is_present=False).count()
#         total = total_present + total_absent
#         if total > 0:
#             percentage = round((total_present / total) * 100)
#         else:
#             percentage = 0
#         student_attendance.append((student, total_present, total_absent, percentage))
#     return render(request, 'visualization.html', {'student_attendance': student_attendance})


from django.shortcuts import render
from django.utils.dateparse import parse_date
from .models import Student, Attendance

# def visualization(request):
#     # Get date from query parameters
#     date_str = request.GET.get('date', None)
#     date = parse_date(date_str) if date_str else None

#     students = Student.objects.filter(is_approved=True)
#     student_attendance = []
#     for student in students:
#         if date:
#             # Filter attendance for the specific date
#             total_present = Attendance.objects.filter(student=student, is_present=True, date=date).count()
#             total_absent = Attendance.objects.filter(student=student, is_present=False, date=date).count()
#         else:
#             # If no date is provided, consider all attendance records
#             total_present = Attendance.objects.filter(student=student, is_present=True).count()
#             total_absent = Attendance.objects.filter(student=student, is_present=False).count()

#         total = total_present + total_absent
#         percentage = round((total_present / total) * 100) if total > 0 else 0
#         student_attendance.append((student, total_present, total_absent, percentage))
    
#     return render(request, 'visualization.html', {'student_attendance': student_attendance, 'date': date_str})


from django.shortcuts import render
from django.utils.dateparse import parse_date
from .models import Student, Attendance

def visualization(request):
    # Get date from query parameters
    date_str = request.GET.get('date', None)
    date = parse_date(date_str) if date_str else None

    students = Student.objects.filter(is_approved=True)
    student_attendance = []
    for student in students:
        if date:
            # Filter attendance for the specific date
            total_present = Attendance.objects.filter(student=student, is_present=True, date=date).count()
            total_absent = Attendance.objects.filter(student=student, is_present=False, date=date).count()
        else:
            # If no date is provided, consider all attendance records
            total_present = Attendance.objects.filter(student=student, is_present=True).count()
            total_absent = Attendance.objects.filter(student=student, is_present=False).count()

        total = total_present + total_absent
        percentage = round((total_present / total) * 100) if total > 0 else 0
        student_attendance.append((student, total_present, total_absent, percentage))

    # Gender Distribution
    gender_counts = Student.objects.values('gender').annotate(count=models.Count('gender'))
    gender_distribution = {gender['gender']: gender['count'] for gender in gender_counts}

    # Course Enrollment
    course_counts = Student.objects.values('course').annotate(count=models.Count('course'))
    course_distribution = {course['course']: course['count'] for course in course_counts}

    return render(request, 'visualization.html', {
        'student_attendance': student_attendance,
        'date': date_str,
        'gender_distribution': gender_distribution,
        'course_distribution': course_distribution,
    })

from django.shortcuts import render
from .models import Student, Attendance

def event_visualization(request, student_id):
    student = Student.objects.get(id=student_id)
    
    # Prepare data for Behavioral Timeline
    timeline_data = [
        {'id': 1, 'content': 'Registration', 'start': student.registration_date.strftime('%Y-%m-%d')},
        {'id': 2, 'content': 'First Attendance', 'start': Attendance.objects.filter(student=student).order_by('date').first().date.strftime('%Y-%m-%d')},
        {'id': 3, 'content': 'Approval', 'start': student.registration_date.strftime('%Y-%m-%d') if student.is_approved else None},
    ]

    # Prepare data for Event Analysis (Gantt Chart)
    tasks = [
        {'id': '1', 'name': 'Exam Period', 'start': '2024-09-01', 'end': '2024-09-15', 'progress': 100},
        {'id': '2', 'name': 'Holiday Break', 'start': '2024-12-20', 'end': '2024-01-05', 'progress': 100},
        {
            'id': '3',
            'name': 'Attendance',
            'start': Attendance.objects.filter(student=student).order_by('date').first().date.strftime('%Y-%m-%d'),
            'end': Attendance.objects.filter(student=student).order_by('-date').first().date.strftime('%Y-%m-%d'),
            'progress': 85,  # Replace with actual calculation
        }
    ]

    return render(request, 'event_visualization.html', {'timeline_data': timeline_data, 'tasks': tasks})



import io
import tempfile
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import LoginActivity
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image as PdfImage

@login_required
def activity_report(request):
    user = request.user
    activities = LoginActivity.objects.filter(name=user)

    if request.GET.get('action') == 'download':
        # Generate PDF report
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Title and styles
        styles = getSampleStyleSheet()
        title = Paragraph("User Engagement Report", styles['Title'])
        elements.append(title)
        
        total_logins = activities.count()
        total_time_logged_in = timedelta()
        session_durations = []

        for activity in activities:
            if activity.logout_time:
                duration = activity.logout_time - activity.login_time
                session_durations.append(duration)
                total_time_logged_in += duration

        average_session_duration = (total_time_logged_in / len(session_durations)) if session_durations else timedelta()
        last_login = activities.last().login_time if activities.exists() else 'N/A'

        # Add summary
        summary_data = [
            ['Total Logins', total_logins],
            ['Total Time Logged In', str(total_time_logged_in)],
            ['Average Session Duration', str(average_session_duration)],
            ['Last Login', last_login]
        ]
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#d5a6a0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        elements.append(summary_table)

        # Add Activity Details
        activity_data = [['Username', 'Login Time', 'Logout Time', 'Session Duration']]
        for activity in activities:
            session_duration = (activity.logout_time - activity.login_time) if activity.logout_time else 'N/A'
            activity_data.append([activity.name.username, activity.login_time, activity.logout_time, session_duration])

        activity_table = Table(activity_data)
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#d5a6a0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        elements.append(activity_table)

        # Generate a sample chart
        fig, ax = plt.subplots()
        durations = [duration.total_seconds() / 3600 for duration in session_durations]
        ax.hist(durations, bins=10, edgecolor='black')
        ax.set_title('Session Duration Distribution')
        ax.set_xlabel('Duration (hours)')
        ax.set_ylabel('Frequency')
        plt.tight_layout()

        # Use tempfile to create a temporary file for the chart image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            chart_path = temp_file.name
            plt.savefig(chart_path)
            plt.close(fig)

        # Add chart to PDF
        elements.append(Paragraph("Session Duration Distribution Chart", styles['Heading2']))
        elements.append(PdfImage(chart_path, width=4*inch, height=3*inch))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="activity_report.pdf"'
        return response
    else:
        # Generate detailed analytics
        total_logins = activities.count()
        total_time_logged_in = timedelta()
        session_durations = []

        for activity in activities:
            if activity.logout_time:
                duration = activity.logout_time - activity.login_time
                session_durations.append(duration)
                total_time_logged_in += duration

        average_session_duration = (total_time_logged_in / len(session_durations)) if session_durations else timedelta()
        last_login = activities.last().login_time if activities.exists() else 'N/A'

        context = {
            'total_logins': total_logins,
            'total_time_logged_in': total_time_logged_in,
            'average_session_duration': average_session_duration,
            'last_login': last_login,
            'activities': activities,
        }
        return render(request, 'activity_analytics.html', context)







# Configure the Google Generative AI API
 # Securely fetch API key from environment

import google.generativeai as genai
from django.shortcuts import render
from .forms import InternshipForm

# Configure the Google Generative AI API
genai.configure(api_key=("AIzaSyBkYTw0j_pG4AJJN5RAnwmrfSqLkM7xOfk"))  # Use environment variables for production

# Define your generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Define the view that handles the form submission
def internship_suggestion_view(request):
    if request.method == "POST":
        form = InternshipForm(request.POST)
        if form.is_valid():
            qualification = form.cleaned_data['qualification']
            skills = form.cleaned_data['skills']
            experience = form.cleaned_data['experience']
            duration = form.cleaned_data['duration']
            stipend = form.cleaned_data['stipend']

            # Create the model and chat session
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config
            )

            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            f"Suggest internships for someone with the following details: Qualification: {qualification}, Skills: {skills}, Experience: {experience} years, Duration: {duration} months, Stipend: {stipend}"
                        ]
                    }
                ]
            )

            try:
                # Send the message and retrieve suggestions
                response = chat_session.send_message("Provide internship suggestions")
                response_text = response.text

                # Remove asterisks from the response
                cleaned_response = response_text.replace('*', '')

            except Exception as e:
                cleaned_response = f"Error occurred: {str(e)}"

            # Render the response in the template with cleaned response
            return render(request, 'suggestion.html', {'response': cleaned_response})

    else:
        form = InternshipForm()

    return render(request, 'internship_form.html', {'form': form})
















