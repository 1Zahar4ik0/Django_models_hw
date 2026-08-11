from django import forms
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group, User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'author',
            'title',
            'text',
            'categories',
        ]

class CommonSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
        ]
