from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from .forms import LibrarianRegisterForm, BookForm
from .models import Book, BorrowSlip, Books_Borrowed, Students,BooksStatus, Penalty, Librarian, BookReservation
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.contrib import messages

def register_librarian(request):
    template = loader.get_template('register.html')
    form = LibrarianRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('pagemain')
    context = {'form': form}
    return HttpResponse(template.render(context, request))

def login_user(request):
    template = loader.get_template('main.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        librarian_user = authenticate(request, username=username, password=password)

        if librarian_user and Librarian.objects.filter(username=username).exists():
            login(request, librarian_user)
            return redirect('pagemain')

        try:
            student = Students.objects.get(email=username, password=password)
            request.session['student_id'] = student.student_id
            return redirect('student_dashboard')
        except Students.DoesNotExist:
            messages.error(request, "Invalid credentials.")

    return HttpResponse(template.render({}, request))

def student_dashboard(request):
    template = loader.get_template('student_dashboard.html')
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('login')

    student = Students.objects.get(student_id=student_id)
    borrowed_books = Books_Borrowed.objects.filter(BorrowSlip_id__Student_id=student).select_related('Book_id')
    
    active_borrowed = [b for b in borrowed_books if not BooksStatus.objects.filter(Book_id=b.Book_id).first().BookStatus]
    returned_borrowed = [b for b in borrowed_books if BooksStatus.objects.filter(Book_id=b.Book_id).first().BookStatus]

    books = Book.objects.all()
    query = request.GET.get('q')
    if query:
        books = books.filter(title__icontains=query)

    reserved_books = BookReservation.objects.filter(
        student=student,
        status__in=['pending', 'reserved', 'borrowed']
    ).values_list('book_id', flat=True)

    books = books.exclude(id__in=reserved_books)

    if request.method == 'POST':
        if BookReservation.objects.filter(student=student, status__in=['pending', 'reserved', 'borrowed']).count() >= 3:
            messages.error(request, "You have reached the reservation limit (3).")
        else:
            book_id = request.POST.get('book_id')
            book = Book.objects.get(id=book_id)
            BookReservation.objects.create(student=student, book=book)
            messages.success(request, f"Book '{book.title}' reserved successfully.")
        return redirect('student_dashboard')

    reservations = BookReservation.objects.filter(student=student).order_by('-reserved_at')[:6]
    context = {
        'student': student,
        'active_borrowed': active_borrowed,
        'returned_borrowed': returned_borrowed,
        'books': books,
        'reservations': reservations,
        'query': query
    }
    return HttpResponse(template.render(context, request))

def logout_librarian(request):
    logout(request)
    return redirect('login')

def page_main(request):
    template = loader.get_template('pagemain.html')
    return HttpResponse(template.render({}, request))

def Searched(request):
    template = loader.get_template('searched.html')
    query = request.GET.get('q')
    books = Book.objects.filter(title__icontains=query) if query else Book.objects.all()
    context = {'books': books, 'query': query}
    return HttpResponse(template.render(context, request))

def add_book(request):
    template = loader.get_template('add_book.html')
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('book_list')
    context = {'form': form}
    return HttpResponse(template.render(context, request))

def book_list(request):
    template = loader.get_template('book_list.html')
    books = Book.objects.all()
    context = {'books': books}
    return HttpResponse(template.render(context, request))

def edit_book(request, book_id):
    template = loader.get_template('edit_book.html')
    book = Book.objects.get(pk=book_id)
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('book_list')
    context = {'form': form, 'book': book}
    return HttpResponse(template.render(context, request))

def delete_book(request, book_id):
    template = loader.get_template('delete_book.html')
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    context = {'book': book}
    return HttpResponse(template.render(context, request))

def borrow_book(request):
    template = loader.get_template('borrow_book.html')
    students = Students.objects.all()
    books = Book.objects.all()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        isbn_input = request.POST.get('isbn_input')

        try:
            student = Students.objects.get(student_id=student_id)
        except Students.DoesNotExist:
            messages.error(request, f"Student with ID '{student_id}' not found.")
            return redirect('borrow_book')

        isbns = [isbn.strip() for isbn in isbn_input.split(',')]
        if len(isbns) > 3:
            messages.error(request, "You can only borrow a maximum of 3 books.")
            return redirect('borrow_book')

        books_to_borrow = []
        for isbn in isbns:
            try:
                book = Book.objects.get(isbn=isbn)
                status = BooksStatus.objects.filter(Book_id=book).first()
                if not status or not status.BookStatus:
                    messages.error(request, f"The book '{book.title}' is currently not available.")
                    return redirect('borrow_book')
                books_to_borrow.append(book)
            except Book.DoesNotExist:
                messages.error(request, f"Book with ISBN '{isbn}' not found.")
                return redirect('borrow_book')

        borrow_slip = BorrowSlip.objects.create(
            Student_id=student,
            Schedule=date.today(),
            ScheduleDue=date.today() + timedelta(days=7)
        )

        for book in books_to_borrow:
            Books_Borrowed.objects.create(BorrowSlip_id=borrow_slip, Book_id=book)
            BooksStatus.objects.filter(Book_id=book).update(BookStatus=False)

        messages.success(request, f"Books successfully borrowed by {student.firstname} {student.lastname}.")
        return redirect('borrow_book')

    context = {'students': students, 'books': books}
    return HttpResponse(template.render(context, request))

def check_penalty(request):
    template = loader.get_template('check_penalty.html')
    penalty_info = None

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        
        try:
            student = Students.objects.get(student_id=student_id)
            slips = BorrowSlip.objects.filter(Student_id=student)
            overdue = []

            for slip in slips:
                if slip.ScheduleDue < date.today():
                    days_late = (date.today() - slip.ScheduleDue).days
                    amount_due = days_late * 3

                    Penalty.objects.update_or_create(
                        Student_id=student,
                        BorrowSlip_id=slip,
                        defaults={'calculated_ammount': amount_due}
                    )

                    overdue.append({
                        'slip': slip,
                        'days_late': days_late,
                        'amount_due': amount_due,
                        'due_date': slip.ScheduleDue,
                    })

            penalty_info = {
                'student': student,
                'overdue': overdue,
                'total_due': sum(o['amount_due'] for o in overdue)
            }

        except Students.DoesNotExist:
            messages.error(request, "Student ID not found.")

    context = {'penalty_info': penalty_info}
    return HttpResponse(template.render(context, request))

def manage_reservations(request):
    template = loader.get_template('manage_reservations.html')
    selected_date_str = request.GET.get('date')
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    reservations = BookReservation.objects.filter(
        reserved_at__date=selected_date
    ).exclude(status__in=['denied', 'accepted', 'returned'])

    if request.method == 'POST':
        res_id = request.POST.get('reservation_id')
        action = request.POST.get('action')
        
        try:
            reservation = BookReservation.objects.get(id=res_id)
            if reservation.is_expired():
                reservation.status = 'expired'
            elif action == 'accept':
                reservation.status = 'reserved'
            elif action == 'deny':
                reservation.status = 'denied'
            reservation.save()
        except BookReservation.DoesNotExist:
            messages.error(request, "Reservation not found.")

    context = {
        'reservations': reservations,
        'selected_date': selected_date,
        'prev_day': (selected_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'next_day': (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    return HttpResponse(template.render(context, request))

def accepted_reservations(request):
    template = loader.get_template('reserve_list.html')
    query = request.GET.get('q')
    
    reservations = BookReservation.objects.filter(status='reserved')
    if query:
        reservations = reservations.filter(student__student_id__icontains=query)

    if request.method == 'POST':
        res_id = request.POST.get('reservation_id')
        
        try:
            reservation = BookReservation.objects.get(id=res_id, status='reserved')
            today = timezone.localtime(timezone.now()).date()
            due_date = today + timedelta(days=7)

            borrow_slip = BorrowSlip.objects.create(
                Student_id=reservation.student,
                Schedule=today,
                ScheduleDue=due_date
            )

            Books_Borrowed.objects.create(
                BorrowSlip_id=borrow_slip,
                Book_id=reservation.book
            )

            BookReservation.objects.filter(id=res_id, status='reserved').update(status='borrowed')
            BooksStatus.objects.filter(Book_id=reservation.book).update(BookStatus=False)

            reservation.status = 'borrowed'
            reservation.save()

            messages.success(request, f"Book '{reservation.book.title}' officially borrowed by {reservation.student.firstname}.")

        except BookReservation.DoesNotExist:
            messages.error(request, "Reservation not found or already processed.")

    context = {'reservations': reservations,
                'query': query}
    return HttpResponse(template.render(context, request))

def return_book(request):
    template = loader.get_template('return_book.html')
    borrower_info, error = None, None

    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        confirm_return = request.POST.get('confirm_return')

        try:
            book = Book.objects.get(isbn=isbn)
            borrowed = Books_Borrowed.objects.get(Book_id=book)
            borrower = borrowed.BorrowSlip_id.Student_id
        except (Book.DoesNotExist, Books_Borrowed.DoesNotExist):
            error = 'Book or borrowing record not found.'
            context = {'error': error}
            return HttpResponse(template.render(context, request))

        if confirm_return == 'true':
            BooksStatus.objects.filter(Book_id=book).update(BookStatus=True)
            borrowed.delete()
            BookReservation.objects.filter(book=book, student=borrower).update(status='returned')
            messages.success(request, f"Book '{book.title}' successfully returned.")
            return redirect('return_book')
        else:
            borrower_info = {'book': book, 'borrower': borrower}

    context = {'borrower_info': borrower_info, 'error': error}
    return HttpResponse(template.render(context, request))
