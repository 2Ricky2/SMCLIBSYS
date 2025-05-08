from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Librarian(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.employee_id
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    price = models.IntegerField(default=None, null=True)
    Date_acquired = models.DateTimeField(null=True, blank = True)

    def __str__(self):
        return self.title
    
class Students(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
class BorrowSlip(models.Model):
    Student_id = models.ForeignKey(Students, on_delete=models.CASCADE, default=None, null=True)
    Schedule = models.DateField()
    ScheduleDue = models.DateField()

    class Meta:
        ordering = ['-Schedule']
    
    def __str__(self):
        return f"{self.Schedule} by {self.Student_id}"
    
class Books_Borrowed(models.Model):
    BorrowSlip_id = models.ForeignKey(BorrowSlip, on_delete=models.CASCADE, default=None, null=True)
    Book_id = models.ForeignKey(Book, on_delete=models.CASCADE, default=None, null=True)
    
    def __str__(self):
        return f"{self.Book_id} by {self.BorrowSlip_id}"
    
class BooksStatus(models.Model):
    Book_id = models.ForeignKey(Book, on_delete=models.CASCADE, default=None, null=True)
    BookStatus = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.Book_id} is {self.BookStatus}"

class Penalty(models.Model):
    Student_id = models.ForeignKey(Students, on_delete=models.CASCADE, default=None, null=True) 
    BorrowSlip_id = models.ForeignKey(BorrowSlip, on_delete=models.CASCADE, default=None, null=True)
    calculated_ammount = models.IntegerField()

    def __str__(self):
        return f"{self.BorrowSlip_id} amountdue {self.calculated_ammount}"

class BookReservation(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(days=2))
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ['-student']

    def __str__(self):
        return f"{self.reserved_at} by {self.student}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    