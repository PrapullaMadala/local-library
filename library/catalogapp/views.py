""" write all view functions here"""


from django.shortcuts import render
from django.views import generic
from .models import Book, Author, BookInstance, Genre


# pylint: disable=maybe-no-member
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Generate counts of some of the main objects
    num_genre = Genre.objects.all().count()

    # Available books (book_kind = 'Love')
    num_books_available = Genre.objects.filter(book_kind='Love').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_books_available': num_books_available
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


# pylint: disable=too-many-ancestors
class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10
    # Get 5 books containing the title war
#   queryset = Book.objects.filter(title__icontains='war')[:5]


class BookDetailView(generic.DetailView):
    """Generic class-based view for book details."""
    model = Book


# pylint: disable=too-many-ancestors
class AuthorListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Author
    paginate_by = 10
    # Get 5 books containing the title war
#   queryset = Book.objects.filter(title__icontains='war')[:5]


class AuthorDetailView(generic.DetailView):
    """Generic class-based view for author details"""
    model = Author
