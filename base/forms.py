from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Job, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
    pass


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = '__all__'
        exclude = []


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
    pass
