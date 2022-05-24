import csv
import pandas as pd
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
# from django.http import HttpResponse
# from django.contrib.auth.hashers import make_password
from .forms import SignupForm
from django.views.generic import(
    DetailView,UpdateView
)
from book.forms import ProfileForm
from braces.views import LoginRequiredMixin
from allauth.account.views import PasswordChangeView
from book.models import User, Book

# with open('./bookList.csv','r',encoding="UTF-8") as f:
#     dr = csv.DictReader(f)
#     s = pd.DataFrame(dr)
# ss = []
# for i in range(len(s)):
#     st = (s['book_isbn'][i], s['book_img_url'][i], s['book_title'][i],s['book_author'][i],s['book_publisher'][i],s['genre_name'][i])
#     ss.append(st)
# for i in range(len(s)):
#     Book.objects.create(book_isbn=ss[i][0], book_img_url=ss[i][1], book_title=ss[i][2],book_author=ss[i][3],book_publisher=ss[i][4],genre_name=ss[i][5])


# main
def main(request):
    return render(request,'book/main.html')

# account/signup
def signup(request) : 
    if request.method == 'GET' :
        form = SignupForm()
   
    elif request.method == 'POST' :
        form = SignupForm(request.POST)
        if form.is_valid() :
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'account/signup_success.html')
    return render(request, 'account/signup.html', {'form': form})

# account/login    
def loginview(request) :
    if request.method == 'GET' :
            return render(request, 'account/login.html')

    elif request.method == 'POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None :
            login(request, user)
            # 로그인 성공
            return render(request, 'book/main.html')
        else :
            # 로그인 실패
            return render(request, 'account/login.html', {'error': '아이디 또는 비밀번호를 확인하세요!'})
    else : 
        return render(request, 'account/login.html')

# profile
class ProfileView(DetailView):
    model = User
    template_name = 'profile/profile.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile_user'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
       
        return context

class ProfileSetView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'profile/profile_set_form.html'

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self) :
        return reverse('main')

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'profile/profile_update_form.html'

    def get_object(self, queryset= None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('profile',kwargs=({'user_id':self.request.user.id}))

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView) :
    def get_success_url(self):
        return reverse('profile',kwargs=({'user_id':self.request.user.id})) 

def search(request) :
    if request.method == "GET":
        searchKey = request.GET['q']

        search_books = Book.objects.filter(Q(book_title__icontains = searchKey))

        return render(request,'book/search.html', {'search_books': search_books})

    else:
        return render(request, 'book/main.html') 
        
