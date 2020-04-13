""" write all view functions here"""


from django.shortcuts import render
from django.views import generic
from .models import Book, Author, BookInstance


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
    record = Author.objects.filter(id=4)
    print(record)
    print(type(record))
    print(record)
    field_label = record.get_field('first_name').verbose_name
    print(field_label)
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


# pylint: disable=too-many-ancestors
class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    # Get 5 books containing the title war
    queryset = Book.objects.filter(title__icontains='war')[:5]
