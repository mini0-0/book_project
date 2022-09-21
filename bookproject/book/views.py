
from contextlib import nullcontext
from multiprocessing import context
from urllib import request
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render,redirect,get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from random import *

from formatter import NullFormatter
from .forms import UserForm
from django.views.generic import(
    DetailView, UpdateView, ListView, CreateView, DeleteView
)
from book.forms import ProfileForm, ReviewForm
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.views import PasswordChangeView
from book.models import Genre, User, Book, WishBookList, Review
from book.functions import confirmation_required_redirect
from gensim.models import word2vec
from django.core.paginator import Paginator
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
# import konlpy 
# from konlpy.tag import Okt,Twitter 
# from collections import Counter
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from krwordrank.word import summarize_with_keywords


df = pd.DataFrame(list(Book.objects.all().values()))
wish = pd.DataFrame(list(WishBookList.objects.all().values()))
re_model = word2vec.Word2Vec.load("recommend/title_model.doc2vec")

# main
def main(request):
    r_book = Book.objects.all()
    ran_list = []
    for i in range(0,20):
        ran_list.append(Book.objects.order_by("?")[i])

    context={
        'r_book':r_book,
        'ran_list':ran_list,
        
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
            return redirect('main')
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
        context['user_reviews'] = Review.objects.filter(author__id=user_id).order_by('-dt_created')[:6]
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
 
# 검색
def search(request) :
    search_key = request.GET.get('q')
    option_select = request.GET.getlist('option_select',None)
    search_books = Book.objects.all().order_by('book_isbn')
    
    if 'all' in option_select :
        search_books = search_books.filter(Q(book_title__icontains = search_key) | Q(book_publisher__icontains = search_key) | Q(book_author__icontains = search_key) | Q(genre_name__icontains = search_key))

    elif 'title' in option_select :
        search_books = search_books.filter(Q(book_title__icontains = search_key))

    elif 'author' in option_select :
        search_books = search_books.filter(Q(book_author__icontains = search_key))

    elif 'publisher' in option_select :
        search_books = search_books.filter(Q(book_publisher__icontains = search_key))

    else :
        search_books = search_books.filter(Q(genre_name__icontains = search_key))

    page = int(request.GET.get('page',1))
    paginator = Paginator(search_books,10)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    index = page_obj.number
    max_index = len(paginator.page_range)
    page_size = 5

    start_index = index - page_size if index > page_size else 1

    if index + page_size == max_index :
        end_index = max_index
    else :
        end_index = index + page_size if index <= max_index else max_index

    page_range = list(paginator.page_range[start_index-1:end_index])
    context = {
        'search_key': search_key,
        'page_obj': page_obj,
        'page_range' : page_range,
        'max_index' : max_index,
        'page_size' : page_size
    }

    return render(request,'book/search.html', context)


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
    book_list = Book.objects.all()
    try:
        book = Book.objects.get(book_isbn=book_isbn)
    except:
        bookMultiple = Book.objects.filter(book_isbn=book_isbn)
        book = bookMultiple[0]
    reviews = Review.objects.all()
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
            'wished' : wished,
            'reviews': reviews,
            'book_list':book_list,
        }
    )

def addWishList(request, book_isbn):
    user = request.user
    try:
        book = Book.objects.get(book_isbn=book_isbn)
    except:
        bookMultiple = Book.objects.filter(book_isbn=book_isbn)
        book = bookMultiple[0]

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

# def wishListView(request):
#     user = request.user
#     user_wishList = WishBookList.objects.filter(user_id=user)


#     return render(
#         request,
#         'profile/profile_wishList.html',
#         {
#             'wishList' : user_wishList
#         }
#     )

class WishList(ListView):
    model = Book
    ordering = '-pk'
    paginate_by = 5

    template_name = 'profile/profile_wishList.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        try:
            context['wishList'] = WishBookList.objects.filter(user_id=self.request.user)
        except:
            context['user_id'] = "no"
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
    template_name = "review/review_list.html"
    context_object_name = "reviews"
    paginate_by = 6
    ordering = ["-dt_created"]


class UserReviewListView(ListView):
    model = Review
    template_name = 'review/user_review_list.html'
    context_object_name = 'user_reviews'
    paginate_by = 6

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Review.objects.filter(author__id=user_id).order_by('dt_created')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = get_object_or_404(User, id = self.kwargs.get('user_id'))
        return context


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
    books = df[['book_title', 'book_img_url','book_author','book_publisher','genre_name','book_isbn']]
    document_embedding_list = get_document_vectors(df['book_plot'])
    cosine_similarities = cosine_similarity(document_embedding_list, document_embedding_list)

    # 책의 제목을 입력하면 해당 제목의 인덱스를 리턴받아 idx에 저장.
    indices = pd.Series(df.index, index = df['book_title']).drop_duplicates()    
    idx = indices[book_title]

    # 입력된 책과 줄거리(document embedding)가 유사한 책 15개 선정.
    sim_scores = list(enumerate(cosine_similarities[idx]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
    sim_scores = sim_scores[1:11]

    
    # 가장 유사한 책 15권의 인덱스
    book_indices = [i[0] for i in sim_scores]

    # 전체 데이터프레임에서 해당 인덱스의 행만 추출. 5개의 행을 가진다.
    recommend = books.iloc[book_indices].reset_index(drop=True)

    recommend_list = []
    for index, row in recommend.iterrows():
        book_img_url = row['book_img_url']
        book_title = row['book_title']
        book_publisher = row['book_publisher']
        genre_name = row['genre_name']
        book_author = row['book_author']
        book_isbn = row['book_isbn']
        recommend_list.append(
                {
                    'book_title': book_title,
                    'book_img_url': book_img_url,
                    'book_publisher': book_publisher,
                    'genre_name':genre_name,
                    'book_author':book_author,
                    'book_isbn':book_isbn,
                })

    return recommend_list

def book_recommend(request):
    user = request.user
    user_wishList = WishBookList.objects.filter(user_id=user)
    wishlist_title = []
    for b in user_wishList:
        wish_book_title = b.book_id.book_title
        wishlist_title.append(wish_book_title)

    re_list=[]
    for i in range(len(wishlist_title)):
        re = recommendations(wishlist_title[i])
        re_list.append(re)

    page = request.GET.get('page', '1') #GET 방식으로 정보를 받아오는 데이터
    paginator = Paginator(re_list, '2') #Paginator(분할될 객체, 페이지 당 담길 객체수)
    page_obj = paginator.get_page(page) #페이지 번호를 받아 해당 페이지를 리턴
    context={
        'wishlist_title':wishlist_title,
        're_list':re_list,
        'page_obj':page_obj,
    }
    return render(request,"book/recommend.html",context)

