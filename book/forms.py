from django import forms
from .models import User
from django.contrib.auth.hashers import check_password
from .models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'nickname',
            'profile_pic',
            'intro',
        ]
        Widgets = {
            'intro' : forms.Textarea,
        }

class SignupForm(forms.ModelForm):
    username = forms.CharField(
        error_messages={'required':"아이디를 입력하세요."},
        widget = forms.TextInput, label = "아이디"
    )
    password = forms.CharField(
        error_messages={'required' : "비밀번호를 입력하세요"},
        widget = forms.PasswordInput, label = "비밀번호"
    )
    re_password = forms.CharField(
        error_messages={'required' : "비밀번호를 재입력하세요"},
        widget = forms.PasswordInput, label = "비밀번호 재입력"
    )
    email = forms.EmailField(
        error_messages={'required':"이메일을 입력하세요."},
        max_length=64, label = "이메일"
    )
    nickname = forms.CharField(
        error_messages={'required':"별명을 입력하세요."},
        widget = forms.TextInput, label = "별명"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'password']   

        help_texts = {
            'username': None,
        }

        widgets = {
                'username' : forms.TextInput,
                'password' : forms.PasswordInput, 
                'email' : forms.TextInput,
                'nickname' : forms.TextInput,       
            }

# class LoginForm(forms.Form):
#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get('username')
#         password = cleaned_data.get('password')

#         if password and username :
#             try:
#                 user = User.objects.get(username = username)
#             except User.DoesNotExist:
#                 self.add_error("username", "아이디가 존재하지 않습니다.")
#                 return

#             if not check_password(password, user.password):
#                 self.add_error("password", "비밀번호가 일치하지 않습니다.")
#             else:
#                 self.user_id = user.id


    # password 검사 
    def clean_re_password(self):
            cd = self.cleaned_data
            if cd['password'] != cd['re_password']:
                raise forms.ValidationError('비밀번호가 서로 다릅니다.')
                #self.add_error('password', '비밀번호가 서로 다릅니다.')    
            return cd['re_password']
            

    # id 중복 검사 
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            #self.add_error('아이디가 이미 사용중입니다')
            raise forms.ValidationError('아이디가 이미 사용중입니다')
        return username

    # # password와 password2의 값이 일치하는지 유효성 검사
    # def clean_password2(self):
    #     password = self.cleaned_data['password']
    #     password2 = self.cleaned_data['password2']
    #     if password1 != password2:
    #         raise forms.ValidationError('비밀번호와 비밀번호 확인란의 값이 일치하지 않습니다')
    #     return password2
    
    def signup(self):
        if self.is_valid():
            return User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password2']
            )
    
    def save(self, commit=True) :
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit :
            user.save()
        return user