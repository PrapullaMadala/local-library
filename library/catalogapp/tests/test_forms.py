import datetime
import pytest
from django.test import TestCase
from django.utils import timezone

from catalogapp.forms import RenewBookForm


class TestRenewBookForm:
    @pytest.fixture
    def create_book_form(self):
        form = RenewBookForm()
        return form

    def test_renew_form_date_field_label(self, create_book_form):
        assert (create_book_form.fields['renewal_date'].label is None) or (create_book_form.fields['renewal_date'].label
                                                                           == 'renewal date')

    def test_renew_form_date_field_help_text(self, create_book_form):
        help_text = create_book_form.fields['renewal_date'].help_text
        assert help_text == 'Enter a date between now and 4 weeks (default 3).'

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        assert not form.is_valid()

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        assert form.is_valid() is False

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookForm(data={'renewal_date': date})
        assert form.is_valid()

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={'renewal_date': date})
        assert form.is_valid()