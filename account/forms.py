from django import forms
# from django.contrib.auth import get_user_model
from django.forms import ModelForm
from account.models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "register-all-input", "name": "first_name"}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "register-all-input", "name": "last_name"}))
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "register-all-input", "name": "username"}))
    email = forms.CharField(required=True, widget=forms.EmailInput(
        attrs={"class": "register-all-input", "name": "email"}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "register-all-input", "id": "myPass", "name": "password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "register-all-input", "id": "cmyPass", "name": "password2"}))

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "username",
                  "phone_number", "email", "password"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email


class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "firstname_user", "name": "first_name"}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "lastname_user", "name": "last_name"}))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "phone_user", "name": "phone_number"}))

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    address_line_1 = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "address_line_1_user", "name": "address_line_1"}))
    address_line_1 = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "address_line_2_user", "name": "address_line_2"}))
    city = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "city_user", "name": "city"}))
    country = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "country_user", "name": "country"}))
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2',
                  'city', 'country')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
