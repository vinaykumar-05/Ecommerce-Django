from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        max_length=15,
        label="Mobile Number",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        label="Address",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Username',
            'email': 'Email Address',
        }
        help_texts = {
            'username': '',  # remove Django default help text
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 150}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data
