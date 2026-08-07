from django.contrib import admin
from .models import Author, Category, PostCategory, Post, Comment

admin.site.register(Category)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Author)