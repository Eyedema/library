from django.db import models
from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
import uuid
from django.conf import settings
from datetime import date

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="Enter a book genre")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("genre-detail", args=[str(self.id)])  # type: ignore

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre already exists (case insensitive match)",
            )
        ]


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse("author-detail", args=[str(self.id)])  # type: ignore

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"


class Language(models.Model):
    name = models.CharField(
        max_length=200, unique=True, help_text="Enter the book's language"
    )

    def get_absolute_url(self):
        """Returns the url to access a particular language instance."""
        return reverse("language-detail", args=[str(self.id)]) # type: ignore

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="language_name_case_insensitive_unique",
                violation_error_message="Language already exists (case insensitive match)",
            ),
        ]


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.RESTRICT, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description")
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
        '">ISBN number</a>',
    )
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("book-details", args=[str(self.id)])  # type: ignore
    
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre' # type: ignore

class BookInstance(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this book in the library",
    )
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    class Meta:
        ordering = ["book", "status", "due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self) -> str:
        return f"{self.id} ({self.book.title})"  # type: ignore
    
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False
