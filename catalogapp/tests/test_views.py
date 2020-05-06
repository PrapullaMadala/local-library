import pytest
import datetime
import uuid
from django.urls import reverse
from django.contrib.auth.models import User, Permission  # Required to assign User as a borrower
from django.utils import timezone
from catalogapp.models import Book, Author, Genre, BookInstance, Language


@pytest.mark.django_db
class TestAuthorListView:
    @pytest.fixture()
    def setUpTestData(self):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self, client, setUpTestData):
        response = client.get('/catalogapp/authors/')
        assert response.status_code == 200

    def test_view_url_accessible_by_name(self, client, setUpTestData):
        response = client.get(reverse('authors'))
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client, setUpTestData):
        response = client.get(reverse('authors'))
        assert response.status_code == 200
        assert response.template_name == ['catalogapp/author_list.html']

    def test_pagination_is_ten(self, client, setUpTestData):
        response = client.get(reverse('authors'))
        assert response.status_code == 200
        assert 'is_paginated' in response.context
        assert response.context['is_paginated'] is True
        assert len(response.context['author_list']) == 10

    def test_lists_all_authors(self, client, setUpTestData):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = client.get(reverse('authors') + '?page=2')
        assert response.status_code == 200
        assert 'is_paginated' in response.context
        assert response.context['is_paginated'] is True
        assert len(response.context['author_list']) == 3


@pytest.mark.django_db
class TestLoanedBookInstancesByUserListView:
    @pytest.fixture
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(book_kind='Fantasy')
        test_language = Language.objects.create(lang_name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self, client, setUp):
        response = client.get(reverse('my-borrowed'))
        assert response.url == '/accounts/login/?next=/catalogapp/mybooks/'

    def test_logged_in_uses_correct_template(self, client, setUp):
        login = client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = client.get(reverse('my-borrowed'))
        assert login is True
        # Check our user is logged in
        assert str(response.context['user']) == 'testuser1'
        # Check that we got a response "success"
        assert response.status_code == 200
        # Check we used correct template
        assert response.template_name == ['catalogapp/bookinstance_list_borrowed_user.html',
                                          'catalogapp/bookinstance_list.html']

    def test_only_borrowed_books_in_list(self, client, setUp):
        login = client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = client.get(reverse('my-borrowed'))

        # Check our user is logged in
        assert str(response.context['user']) == 'testuser1'
        # Check that we got a response "success"
        assert response.status_code == 200

        # Check that initially we don't have any books in list (none on loan)
        assert 'bookinstance_list' in response.context
        assert len(response.context['bookinstance_list']) == 0

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = client.get(reverse('my-borrowed'))
        # Check our user is logged in
        assert str(response.context['user']) == 'testuser1'
        # Check that we got a response "success"
        assert response.status_code == 200

        assert 'bookinstance_list' in response.context

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            assert response.context['user'] == bookitem.borrower
            assert 'o' == bookitem.status

    def test_pages_ordered_by_due_date(self, client, setUp):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = client.get(reverse('my-borrowed'))

        # Check our user is logged in
        assert str(response.context['user']) == 'testuser1'
        # Check that we got a response "success"
        assert response.status_code == 200

        # Confirm that of the items, only 10 are displayed due to pagination.
        assert len(response.context['bookinstance_list']) == 10

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                assert last_date <= book.due_back
                last_date = book.due_back


@pytest.mark.django_db
class TestRenewBookInstancesView:
    @pytest.fixture
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(book_kind='Fantasy')
        test_language = Language.objects.create(lang_name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self, client, setUp):
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        assert response.status_code == 302
        assert response.url.startswith('/accounts/login/') is True

    def test_redirect_if_logged_in_but_not_correct_permission(self, client, setUp):
        login = client.login(username='testuser1', password='1X<ISRUkw+tuK')
        assert login is True
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        assert response.status_code == 302

    def test_logged_in_with_permission_borrowed_book(self, client, setUp):
        login = client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        assert response.status_code == 200

    def test_logged_in_with_permission_another_users_borrowed_book(self, client, setUp):
        login = client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        assert response.status_code == 200

    def test_HTTP404_for_invalid_book_if_logged_in(self, client, setUp):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        assert response.status_code == 404

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self, client, setUp):
        login = client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        assert response.status_code == 200

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        assert response.context['form'].initial['renewal_date'], date_3_weeks_in_future

    def test_redirects_to_all_borrowed_book_list_on_success(self, client, setUp):
        login = client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                    {'renewal_date': valid_date_in_future})
        assert response.url == reverse('all-borrowed')
