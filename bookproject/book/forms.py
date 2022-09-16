from dataclasses import fields
import email
from pyexpat import model
from .models import User
from django import forms
from .models import User, Review
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm) :
    username = forms.CharField(label='아이디')
    email = forms.EmailField(label='이메일')
    nickname = forms.CharField(label='닉네임')

    class Meta :
        model = User
        fields = ("username", "password1","password2", "email", "nickname")

    # id 중복 검사 
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
             raise forms.ValidationError('이미 사용중인 아이디입니다')
        return username

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = [
            "title",
            "book",
            "review_context",
            "rating",

            ]

        widgets = {
            "rating": forms.Select,
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'nickname',
            'profile_pic',
            'intro',
        ]
        widgets = {
            'intro' : forms.Textarea,
        }