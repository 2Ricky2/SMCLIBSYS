from django.contrib import admin
from .models import Librarian, Book, Students, BorrowSlip, Books_Borrowed, BooksStatus, Penalty, BookReservation

admin.site.register(Librarian)
admin.site.register(Book)
admin.site.register(Students)
admin.site.register(BorrowSlip)
admin.site.register(Books_Borrowed)
admin.site.register(BooksStatus)
admin.site.register(Penalty)
admin.site.register(BookReservation)



