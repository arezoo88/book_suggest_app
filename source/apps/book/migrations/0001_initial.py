# Generated by Django 4.2.14 on 2024-07-21 08:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated_at')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('author', models.CharField(max_length=200, verbose_name='Author')),
                ('genre', models.CharField(max_length=200, verbose_name='Genre')),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
                'ordering': ['-created_at'],
                'unique_together': {('title', 'author', 'genre')},
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated_at')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], verbose_name='Rating')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.book', verbose_name='Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'book')},
            },
        ),
    ]
