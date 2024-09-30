from django import forms
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100)

    class Meta:
        model = Student
        exclude = ['roll_number', 'is_approved']
        widgets = {
            'date_of_birth': DateInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
    

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['is_present']        

from django import forms

class InternshipForm(forms.Form):
    qualification = forms.CharField(label='Qualification', max_length=100)
    skills = forms.CharField(label='Skills', max_length=200)
    experience = forms.IntegerField(label='Years of Experience')
    duration = forms.IntegerField(label='Duration of Internship (in months)')
    stipend = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], label='With Stipend')



from django import forms

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(max_length=100, widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

