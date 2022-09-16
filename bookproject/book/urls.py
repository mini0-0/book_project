from argparse import Namespace
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.main,name='main'),
    # profile
    path('users/<int:user_id>',views.ProfileView.as_view(),name='profile'),
    path('set-profile/',views.ProfileSetView.as_view(),name='profile-set'),
    path('edit-profile/',views.ProfileUpdateView.as_view(),name='profile-update'),
    path('wishList-profile/', views.WishList.as_view(), name='profile-wishList'),

    # review
    path('reviews/<int:review_id>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/new/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:review_id>/edit/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('reviews/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),

    # account
    path('login/', views.loginview, name='login'),
    path('signup/', views.signup, name='signup'),

    path('search/', views.search, name='search'),  
    
    path('select_genre/', views.GenreList.as_view(), name='select-genre'),
    path('select_genre/<int:genre_id>', views.SelectedGenreList, name='selectd-genre'),
    
    path('book/list', views.BookList.as_view()),
    path('book/<int:book_isbn>/', views.bookDetail),
    path('book/like/<int:book_isbn>/', views.addWishList, name='like-book'),

    path('recommend/',views.book_recommend,name='book-recommend'),
    # #path('random/', views.get_random, name='book-random'),
]