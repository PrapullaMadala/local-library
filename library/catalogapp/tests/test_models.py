import pytest
from catalogapp.models import Author, Book, Genre, BookInstance, Language


@pytest.mark.django_db
class TestAuthor:
    def create_author(self, first_name: str, last_name: str):
        author = Author.objects.create(first_name=first_name, last_name=last_name)
        return author

    @pytest.fixture
    def author_fixture(self, db):
        return self.create_author(first_name='prapulla', last_name='madala')

    def test_author_instance(self, author_fixture):
        assert author_fixture.id == 1
        assert author_fixture.first_name == 'prapulla'
        assert author_fixture.last_name == 'madala'

    def test_first_name_lable(self, author_fixture: Author):
        field_label = author_fixture._meta.get_field('first_name').verbose_name
        assert field_label == 'first name'

    def test_date_of_death_label(self, author_fixture):
        field_label = author_fixture._meta.get_field('date_of_death').verbose_name
        assert field_label == 'died'

    def test_first_name_max_length(self, author_fixture):
        max_length = author_fixture._meta.get_field('first_name').max_length
        assert max_length == 100

    def test_object_name_is_last_name_comma_first_name(self, author_fixture):
        expected_object_name = f'{author_fixture.last_name}, {author_fixture.first_name}'
        assert expected_object_name == str(author_fixture)

    def test_get_absolute_url(self, author_fixture):
        id = author_fixture.id
        expected_url = author_fixture.get_absolute_url()
        # This will also fail if the urlconf is not defined.
        assert expected_url == '/catalogapp/author/' + str(id)


@pytest.mark.django_db
class TestBook:
    @pytest.fixture
    def create_author_instance(self):
        author = Author.objects.create(first_name='prapulla')
        return author

    @pytest.fixture
    def create_book_instance(self, create_author_instance):

        self.book = Book.objects.create(title='mybook', author=create_author_instance)
        return self.book

    @pytest.fixture
    def create_genre_instance(self, create_book_instance):
        self.genre1 = Genre.objects.create(book_kind='genre1')
        self.genre2 = Genre.objects.create(book_kind='genre2')
        self.genre3 = Genre.objects.create(book_kind='genre3')
        self.genre4 = Genre.objects.create(book_kind='genre4')
        self.book1 = Book.objects.create(title='mybook1')
        self.book2 = Book.objects.create(title='mybook2')
        self.before_count = self.book1.genre.count()
        self.book1.genre.add(self.genre1, self.genre2)
        self.book2.genre.add(self.genre1, self.genre2, self.genre3, self.genre4)
        self.after_count = self.book1.genre.count()

    def test_book_instance(self, create_book_instance, create_author_instance):
        assert create_book_instance.id == 1
        assert create_book_instance.title == 'mybook'
        assert create_book_instance.author.pk == 7
        assert create_book_instance.author.pk == create_author_instance.pk

    def test_foreignkey_relation(self, create_book_instance, create_author_instance):
        assert Book.objects.filter(author=create_author_instance).exists()
        assert create_book_instance.author.first_name == 'prapulla'

    def test_book_has_many_genre(self, create_genre_instance):
        record = Book.objects.filter(genre=self.genre1)
        assert list(record) == [self.book1, self.book2]
        record = Book.objects.filter(genre=self.genre3)
        assert list(record) == [self.book2]

    def test_genre_count(self, create_genre_instance):
        assert self.before_count == 0
        assert self.after_count == 2

    def test_object_string_representation(self, create_book_instance):
        expected_value = str(create_book_instance)
        assert expected_value == create_book_instance.title

    def test_get_absolute_url(self, create_book_instance):
        _id = create_book_instance.id
        expected_url = create_book_instance.get_absolute_url()
        # This will also fail if the urlconf is not defined.
        assert expected_url == '/catalogapp/book/' + str(_id)

    def test_display_genre(self, create_genre_instance):
        genres = self.book2.genre.all()
        assert genres.count() == 4
        assert list(genres) == [self.genre1, self.genre2, self.genre3, self.genre4]
        assert self.genre1.book_kind == 'genre1'
        assert self.genre2.book_kind == 'genre2'
        expected_value = ", ".join(genre.book_kind for genre in self.book2.genre.all()[:3])
        assert expected_value == self.book2.display_genre()
        description = self.book2.display_genre.short_description
        assert description == 'Genre'

    def test_isbn_field(self, create_book_instance):
        max_length = create_book_instance._meta.get_field('isbn').max_length
        assert max_length == 13
        if max_length > 13:
            raise ValueError('max_length should be 13')
        help_text = create_book_instance._meta.get_field('isbn').help_text
        s = help_text[22:-17]
        expected_value = "https://www.isbn-international.org/content/what-isbn"
        assert s == expected_value

    def test_genre_string_representation(self):
        genre_obj = Genre.objects.create(book_kind='genretype')
        expected_value = str(genre_obj)
        assert expected_value == genre_obj.book_kind

    def test_language_string_representation(self):
        lang_obj = Language.objects.create(lang_name='english')
        expected_value = str(lang_obj)
        assert expected_value == lang_obj.lang_name


@pytest.mark.django_db
class TestBookInstance:
    @pytest.fixture
    def create_book(self):
        book = Book.objects.create(title='mybook')
        return book

    @pytest.fixture
    def create_bookcopy_instance(self, create_book):
        instance = BookInstance.objects.create(imprint='published', book=create_book)
        return instance

    def test_instance(self, create_bookcopy_instance):
        assert create_bookcopy_instance.book.title == 'mybook'

    def test_loan_status_field(self, create_bookcopy_instance):
        max_length = create_bookcopy_instance._meta.get_field('status').max_length
        assert max_length == 1
        choices = create_bookcopy_instance._meta.get_field('status').choices
        tuple_second_element = choices[1]
        assert tuple_second_element == ('o', 'On loan')

    def test_object_string_representation(self, create_bookcopy_instance):
        expected_value = f'{create_bookcopy_instance.id} ({create_bookcopy_instance.book.title})'
        assert str(create_bookcopy_instance) == expected_value

    def test_meta(self, create_bookcopy_instance):
        ordering = create_bookcopy_instance._meta.ordering[0]
        assert ordering == 'due_back'

