from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Librarian, Book, BooksStatus

class LibrarianRegisterForm(UserCreationForm):
    class Meta:
        model = Librarian
        fields = ['username', 'employee_id', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['username'].help_text = ""


class BookForm(forms.ModelForm):
    available = forms.BooleanField(label="Is Available", required=False, initial=False)

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'price', 'Date_acquired']

    def __init__(self, *args, **kwargs):
        book_instance = kwargs.get('instance', None)
        if book_instance:
            try:
                kwargs.setdefault('initial', {})['available'] = book_instance.booksstatus_set.first().BookStatus
            except:
                kwargs.setdefault('initial', {})['available'] = False
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        book = super().save(commit)
        status, _ = BooksStatus.objects.get_or_create(Book_id=book)
        status.BookStatus = self.cleaned_data.get('available', False)
        status.save()
        return book
    
