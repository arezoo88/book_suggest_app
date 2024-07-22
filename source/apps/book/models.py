from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_('Created_at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Updated_at'),
        auto_now=True
    )

    class Meta:
        abstract = True


class Book(BaseModel):
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
    )
    author = models.CharField(
        max_length=200,
        verbose_name=_('Author')
    )
    genre = models.CharField(
        max_length=200,
        verbose_name=_('Genre')
    )

    class Meta:
        unique_together = ('title', 'author', 'genre')
        ordering = ['-created_at']
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    def __str__(self):
        return self.title


class Review(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name=_('Book'),
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Rating')
    )

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-created_at']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.rating}"
