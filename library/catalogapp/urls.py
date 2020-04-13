""" mapping application urls to view functions"""

from django.urls import path
from . import views

URLPATTERNS = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),

]
