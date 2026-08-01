from platform import release

from django.db import models
from django.contrib.auth.models import User

NEWS = "NS"
ARTICLE = "AE"

POST_TYPES = [
    (NEWS, "Новость"),
    (ARTICLE, "Статья"),
]

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = 0
        for post in self.posts.all():
            post_rating += post.rating

        comment_rating = 0
        for comment in self.user.comments.all():
            comment_rating += comment.rating

        post_comment_rating = 0
        for post in self.posts.all():
            for comment in post.comments.all():
                post_comment_rating += comment.rating

        self.rating = post_rating * 3 + comment_rating + post_comment_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Post(models.Model):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    post_type = models.CharField(
        max_length=255,
        choices=POST_TYPES,
        default=ARTICLE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    categories = models.ManyToManyField(
        Category,
        through='PostCategory',
        related_name='posts',
    )

    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save(update_fields=["rating"])

    def dislike(self):
        self.rating -= 1
        self.save(update_fields=["rating"])

    def preview(self):
        return self.text[:124] + '...'

class PostCategory(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save(update_fields=["rating"])

    def dislike(self):
        self.rating -= 1
        self.save(update_fields=["rating"])
