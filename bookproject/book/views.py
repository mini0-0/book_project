from multiprocessing import context
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render,redirect,get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from random import *
# from .forms import SignupForm
from .forms import UserForm
from django.views.generic import(
    DetailView, UpdateView, ListView, CreateView, DeleteView
)
from book.forms import ProfileForm, ReviewForm
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.views import PasswordChangeView
from book.models import Genre, User, Book, WishBookList, Review, Tag
from book.functions import confirmation_required_redirect
from gensim.models import word2vec
import urllib.request
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
from django.views.decorators.csrf import csrf_exempt
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import re

df = pd.DataFrame(list(Book.objects.all().values()))
wish = pd.DataFrame(list(WishBookList.objects.all().values()))
re_model = word2vec.Word2Vec.load("recommend/title_model.doc2vec")

# main
def main(request):
    r_book = Book.objects.all()
    ran_list = []
    for i in range(0,20):
        ran_list.append(Book.objects.order_by("?")[i])

    reviews = Review.objects.order_by('-dt_created')
    context={
        'r_book':r_book,
        'ran_list':ran_list,
        'reviews':reviews
        
    }
    return render(request,'book/main.html',context)

# account/signup
def signup(request) :
    if request.method == 'GET' :
        form = UserForm()

    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
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
        search_key = request.GET['q']
        option_select = request.GET.getlist('option_select',None)
        
        if 'all' in option_select :
            search_books = Book.objects.filter(Q(book_title__icontains = search_key) | Q(book_publisher__icontains = search_key) | Q(book_author__icontains = search_key) | Q(genre_name__icontains = search_key))

        elif 'title' in option_select :
            search_books = Book.objects.filter(Q(book_title__icontains = search_key))

        elif 'author' in option_select :
            search_books = Book.objects.filter(Q(book_author__icontains = search_key))

        elif 'publisher' in option_select :
            search_books = Book.objects.filter(Q(book_publisher__icontains = search_key))

        elif 'genre' in option_select :
            search_books = Book.objects.filter(Q(genre_name__icontains = search_key))

        return render(request,'book/search.html', {'search_books': search_books, 'search_key': search_key})
    
    else:
        return render(request, 'book/main.html')


# 장르선택
class GenreList(ListView):
    model = Genre
    template_name = 'book/select_genre.html'


def SelectedGenreList(request, genre_id):

    genre = Genre.objects.get(id=genre_id)
    book_list = Book.objects.filter(genre_name=genre.genre_name)

    return render(
        request,
        'book/selected_genre.html',
        {
            'book_list': book_list,
            'genre_name': genre.genre_name
        }
    )



class BookList(ListView):
    model = Book
    template_name = 'book/book_list.html'


def bookDetail(request,book_isbn):
    user = request.user
    try:
        book = Book.objects.get(book_isbn=book_isbn)
    except:
        bookList = Book.objects.filter(book_isbn=book_isbn)
        book = bookList[0]


    
    try:
        wishlist = WishBookList.objects.get(user_id=user,book_id=book) 
        wished=True
    except:
        wished=False


    return render(
        request,
        'book/book_detail.html',
        {
            'book': book,
            'wishList': WishBookList,
            'wished' : wished
        }
    )






def addWishList(request, book_isbn):
    user = request.user
    book = Book.objects.get(book_isbn=book_isbn)

    # 위시리스트 추가
    if request.POST.get('wish-cancle') == None:
        wish_book = WishBookList(user_id=user, book_id=book)
        WishBookList.save(wish_book)
        wished=True

    # 위시리스트 취소
    else:
        wish_list = WishBookList.objects.get(user_id=user, book_id=book)
        wish_list.delete()
        wished=False

    
    return render(
        request,
        'book/book_detail.html',
        {
            'book': book,
            'wished': wished
        }
    )

def wishListView(request):
    user = request.user
    user_wishList = WishBookList.objects.filter(user_id=user)
    wishList_title=[]
    for b in user_wishList:
        wish_book_title = b.book_id.book_title
        wishList_title.append(wish_book_title)

    return render(
        request,
        'profile/profile_wishList.html',
        {
            'wishList' : user_wishList
        }
    )

class WishList(ListView):
    model = Book
    ordering = '-pk'
    paginate_by = 5

    template_name = 'profile/profile_wishList.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wishList'] = WishBookList.objects.filter(user_id=self.request.user)
        return context


# review
class ReviewDetailView(DetailView):
    model = Review
    template_name = 'review/review_detail.html'
    pk_url_kwarg = 'review_id'


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review/review_form.html'

    redirect_unauthenticated_users = True
    raise_exception = confirmation_required_redirect

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review/review_form.html'
    pk_url_kwarg = 'review_id'

    raise_exception = True
    redirect_unauthenticated_users = False

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})

    def test_func(self, user):
        review = self.get_object()
        if review.author == user:
            return True
        else:
            return False


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'review/review_confirm_delete.html'
    pk_url_kwarg = 'review_id'

    raise_exception = True
    redirect_unauthenticated_users = False

    def get_success_url(self):
        return reverse('main')

    def test_func(self, user):
        review = self.get_object()
        if review.author == user:
            return True
        else:
            return False

class ReviewView(ListView):
    model = Review
    template_name = "book/main.html"
    context_object_name = "reviews"
    paginate_by = 4
    ordering = ["-dt_created"]

def get_document_vectors(document_list):
    document_embedding_list = []

    # 각 문서에 대해서
    for line in document_list:
        doc2vec = None
        count = 0
        for word in line.split():
            if word in re_model.wv.vocab:
                count += 1
                # 해당 문서에 있는 모든 단어들의 벡터값을 더한다.
                if doc2vec is None:
                    doc2vec = re_model[word]
                else:
                    doc2vec = doc2vec + re_model[word]

        if doc2vec is not None:
            # 단어 벡터를 모두 더한 벡터의 값을 문서 길이로 나눠준다.
            doc2vec = doc2vec / count
            document_embedding_list.append(doc2vec)

    # 각 문서에 대한 문서 벡터 리스트를 리턴
    return document_embedding_list

def recommendations(book_title):
    books = df[['book_title', 'book_img_url']]
    document_embedding_list = get_document_vectors(df['book_plot'])
    cosine_similarities = cosine_similarity(document_embedding_list, document_embedding_list)

    # 책의 제목을 입력하면 해당 제목의 인덱스를 리턴받아 idx에 저장.
    indices = pd.Series(df.index, index = df['book_title']).drop_duplicates()    
    idx = indices[book_title]

    # 입력된 책과 줄거리(document embedding)가 유사한 책 20개 선정.
    sim_scores = list(enumerate(cosine_similarities[idx]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
    sim_scores = sim_scores[1:21]

    # 가장 유사한 책 20권의 인덱스
    book_indices = [i[0] for i in sim_scores]

    # 전체 데이터프레임에서 해당 인덱스의 행만 추출. 5개의 행을 가진다.
    recommend = books.iloc[book_indices].reset_index(drop=True)

    # fig = plt.figure(figsize=(20, 30))

    # # 데이터프레임으로부터 순차적으로 이미지를 출력
    # for index, row in recommend.iterrows():
    #     response = requests.get(row['book_img_url'])
    #     img = Image.open(BytesIO(response.content))
    #     fig.add_subplot(1, 11, index + 1)
    #     plt.imshow(img)
    #     plt.title(row['book_title'])

    recommend_list = []
    for index, row in recommend.iterrows():
        img = row['book_img_url']
        title = row['book_title']
        recommend_list.append(
                {
                    'title': title,
                    'book_img_url':img,
                })

    return recommend_list

def book_recommend(request):
    #wish_book = WishBookList.objects.all()
    book_recommend = recommendations("하룻밤에 읽는 숨겨진 세계사")

    #recommend = recommendations(wish[['book_title'])
    context={
        'book_recommend':book_recommend,
        #'recommend':recommend,
    }
    return render(request,"book/test.html",context)


