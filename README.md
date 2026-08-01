from django.contrib.auth.models import User
from news.models import Author, Category, Post, PostCategory, Comment

user1 = User.objects.create_user("Ваня")
user2 = User.objects.create_user("Захар")

author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

category1 = Category.objects.create(name="Спорт")
category2 = Category.objects.create(name="Политика")
category3 = Category.objects.create(name="Образование")
category4 = Category.objects.create(name="Технологии")

article1 = Post.objects.create(
    author=author1,
    post_type="AE",
    title="Как искусственный интеллект меняет образование",
    text=(
        "Искусственный интеллект всё активнее используется в образовании. "
        "Он помогает преподавателям готовить материалы, а учащимся — получать "
        "персональные рекомендации и быстрее находить ответы на сложные вопросы."
    ),
)
article2 = Post.objects.create(
    author=author2,
    post_type="AE",
    title="Новые технологии в профессиональном спорте",
    text=(
        "Современные датчики и системы анализа данных позволяют тренерам "
        "точнее оценивать нагрузку спортсменов и корректировать программу тренировок."
    ),
)
news1 = Post.objects.create(
    author=author1,
    post_type="NS",
    title="Открылась международная образовательная конференция",
    text=(
        "Сегодня начала работу международная конференция, посвящённая цифровым "
        "технологиям, новым образовательным программам и обмену опытом."
    ),
)

PostCategory.objects.create(post=article1, category=category3)
PostCategory.objects.create(post=article1, category=category4)
PostCategory.objects.create(post=article2, category=category1)
PostCategory.objects.create(post=article2, category=category4)
PostCategory.objects.create(post=news1, category=category2)
PostCategory.objects.create(post=news1, category=category3)

comment1 = Comment.objects.create(
    post=article1,
    user=user2,
    text="Полезная статья, особенно часть о персональных рекомендациях.",
)
comment2 = Comment.objects.create(
    post=article1,
    user=user1,
    text="Интересно было бы увидеть больше практических примеров.",
)
comment3 = Comment.objects.create(
    post=article2,
    user=user1,
    text="Технологии действительно заметно меняют тренировочный процесс.",
)
comment4 = Comment.objects.create(
    post=news1,
    user=user2,
    text="Буду следить за результатами конференции.",
)

article1.like()
article1.like()
article1.like()
article1.like()
article1.dislike()
article2.like()
article2.like()
article2.dislike()
news1.like()
news1.like()

comment1.like()
comment1.like()
comment2.like()
comment2.dislike()
comment3.like()
comment4.like()
comment4.like()
comment4.dislike()

author1.update_rating()
author2.update_rating()

best_author = Author.objects.order_by("-rating").values("user__username", "rating").first()
print(best_author["user__username"], best_author["rating"])

best_article = Post.objects.filter(post_type="AE").order_by("-rating").first()
print(
    best_article.created_at,
    best_article.author.user.username,
    best_article.rating,
    best_article.title,
    best_article.preview(),
)

for comment in best_article.comments.select_related("user"):
    print(comment.created_at, comment.user.username, comment.rating, comment.text)