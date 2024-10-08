from django.urls import path, include
from . import views
from django.contrib import admin
from .views import  generate_text
from .views import event_visualization
from .views import activity_report
from .views import *
from django.contrib.auth import views as auth_views
from .views import generate_attendance_report




urlpatterns = [
    path('', views.index,name="index"),
    path('about/', views.about,name="about"),
    path('thanks/', views.thanks,name="thanks"),
    path('approval/', views.approval,name="approval"),
    path('register/', views.register, name='register'),
    path('<int:student_id>/', views.student_detail, name='student_detail'),
    path('attendance/', views.mark_attendance, name='attendance'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('student_view/<int:student_id>/', views.student_view, name='student_view'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('attendance_details/', views.attendance_details, name='attendance_details'),
    path('edit_attendance/<str:date>/', views.edit_attendance, name='edit_attendance'),
    path('student_dashboard/<int:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('s_student_detail/<int:pk>/', views.s_student_detail.as_view(),name='s_student_detail'),
    path('s_attendance_detail/<int:student_id>/', views.s_attendance_detail, name='s_attendance_detail'),
    path('st_attendance_detail/<int:student_id>/', views.st_attendance_detail, name='st_attendance_detail'),
    path('student_login/', views.student_login, name='student_login'),
    path('students_list/', views.students_list, name='students_list'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('gemini-data/', views.show_gemini_data, name='show_gemini_data'),
    path('generate/', generate_text, name='generate_text'),
    path('visualization/', views.visualization, name='visualization'),
    path('event-visualization/<int:student_id>/', event_visualization, name='event_visualization'),
    path('report/activity/', activity_report, name='activity_report'),
    path('internship/', internship_suggestion_view, name='internship_suggestion'),
    path('passwordreset/', password_reset_request, name='passwordreset'),
    path('resetpassword/<str:token>/', password_reset_confirm, name='passwordresetconfirm'),
    path('attendance-report/', generate_attendance_report, name='attendance_report'),
    path('student-summary-report/', generate_student_summary_report, name='student_summary_report'),
    
]
    
