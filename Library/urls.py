from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('library/register', views.register_librarian, name='register'),
    path('library/logout', views.logout_librarian, name='logout'),
    path('library/pagemain', views.page_main, name='pagemain'),
    path('library/pagesearch', views.Searched, name='search'),
    path('library/addbook', views.add_book, name='add_book'),
    path('library/booklist', views.book_list, name='book_list'),
    path('library/editbook/<int:book_id>/', views.edit_book, name='edit_book'),
    path('library/deletebook/<int:book_id>/', views.delete_book, name='delete_book'),
    path('library/borrow', views.borrow_book, name='borrow_book'),
    path('library/check-penalty', views.check_penalty, name='check_penalty'),
    path('library/reservations/', views.manage_reservations, name='manage_reservations'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('library/return', views.return_book, name='return_book'),
    path('reservations/reserved_list/', views.accepted_reservations, name='accepted_reservations'),
    
]
