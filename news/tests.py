from datetime import timedelta

from django.contrib.auth.models import Group, Permission, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import ARTICLE, Author, Category, NEWS, Post
from .tasks import send_weekly_newsletter


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='Zahar4ik135@yandex.ru',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class CategorySubscriptionTests(TestCase):
    def setUp(self):
        self.author_user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='test-password',
        )
        self.author = Author.objects.create(user=self.author_user)
        self.author_user.user_permissions.add(
            Permission.objects.get(codename='add_post'),
        )

        self.subscriber = User.objects.create_user(
            username='zahar',
            email='zahar2282007@mail.ru',
            password='test-password',
        )
        self.category = Category.objects.create(name='Тестовая категория')

    def test_authenticated_user_can_subscribe_to_category(self):
        self.client.force_login(self.subscriber)

        response = self.client.post(
            reverse('subscribe_to_category', args=[self.category.pk]),
        )

        self.assertRedirects(
            response,
            reverse('category_news', args=[self.category.pk]),
        )
        self.assertTrue(
            self.category.subscribers.filter(pk=self.subscriber.pk).exists(),
        )

    def test_creating_article_sends_personalized_html_email_with_link(self):
        self.category.subscribers.add(self.subscriber)
        self.client.force_login(self.author_user)
        text = 'Текст статьи, который содержит больше пятидесяти символов для проверки.'

        response = self.client.post(
            reverse('article_create'),
            {
                'title': 'Проверочная статья',
                'text': text,
                'categories': [self.category.pk],
            },
        )

        self.assertRedirects(response, reverse('news_list'))
        post = Post.objects.get(title='Проверочная статья')
        self.assertEqual(post.post_type, ARTICLE)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        post_url = f'http://example.com{reverse("news_detail", args=[post.pk])}'
        self.assertEqual(message.subject, post.title)
        self.assertEqual(message.from_email, 'Zahar4ik135@yandex.ru')
        self.assertEqual(message.to, ['zahar2282007@mail.ru'])
        self.assertIn('Здравствуй, zahar.', message.body)
        self.assertIn(text[:50], message.body)
        self.assertIn(post_url, message.body)
        self.assertEqual(message.alternatives[0].mimetype, 'text/html')
        self.assertIn('<h2>Проверочная статья</h2>', message.alternatives[0].content)
        self.assertIn(text[:50], message.alternatives[0].content)
        self.assertIn(f'href="{post_url}"', message.alternatives[0].content)

    def test_fourth_news_in_one_day_is_forbidden(self):
        for number in range(3):
            Post.objects.create(
                author=self.author,
                post_type=NEWS,
                title=f'Новость {number}',
                text='Текст',
            )

        self.client.force_login(self.author_user)
        response = self.client.post(
            reverse('news_create'),
            {
                'title': 'Четвёртая новость',
                'text': 'Эта новость не должна сохраниться',
                'categories': [self.category.pk],
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Post.objects.filter(title='Четвёртая новость').exists())

    def test_signal_sends_email_when_category_added_outside_create_view(self):
        self.category.subscribers.add(self.subscriber)
        post = Post.objects.create(
            author=self.author,
            post_type=ARTICLE,
            title='Статья через модель',
            text='Краткая информация о новой публикации для подписчика.',
        )

        post.categories.add(self.category)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['zahar2282007@mail.ru'])
        self.assertEqual(mail.outbox[0].subject, post.title)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='Zahar4ik135@yandex.ru',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class WelcomeEmailTests(TestCase):
    def test_signup_sends_activation_email_with_username(self):
        Group.objects.create(name='common')

        response = self.client.post(
            reverse('account_signup'),
            {
                'email': 'new-user@example.com',
                'password1': 'Safe-test-password-135!',
                'password2': 'Safe-test-password-135!',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='new-user@example.com')
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, ['new-user@example.com'])
        self.assertIn('Добро пожаловать в News Portal!', message.subject)
        self.assertIn(user.username, message.body)
        self.assertIn('/accounts/confirm-email/', message.body)
        self.assertTrue(message.alternatives)

        html_content = message.alternatives[0].content
        self.assertIn(user.username, html_content)
        self.assertIn('/accounts/confirm-email/', html_content)
        self.assertIn('Активировать учётную запись', html_content)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='Zahar4ik135@yandex.ru',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class WeeklyNewsletterTests(TestCase):
    def test_weekly_newsletter_contains_only_recent_subscribed_articles(self):
        author_user = User.objects.create_user(username='weekly-author')
        author = Author.objects.create(user=author_user)
        subscriber = User.objects.create_user(
            username='weekly-reader',
            email='reader@example.com',
        )
        subscribed = Category.objects.create(name='Подписанная')
        other = Category.objects.create(name='Другая')
        subscribed.subscribers.add(subscriber)

        recent = Post.objects.create(
            author=author,
            post_type=ARTICLE,
            title='Свежая статья',
            text='Содержание свежей статьи',
        )
        recent.categories.add(subscribed)

        old = Post.objects.create(
            author=author,
            post_type=ARTICLE,
            title='Старая статья',
            text='Старое содержание',
        )
        old.categories.add(subscribed)
        Post.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )

        unrelated = Post.objects.create(
            author=author,
            post_type=ARTICLE,
            title='Статья другой категории',
            text='Другое содержание',
        )
        unrelated.categories.add(other)

        # Подготовка статей вызывает мгновенные уведомления через сигнал.
        # Здесь проверяется только отдельная еженедельная подборка.
        mail.outbox.clear()

        sent_count = send_weekly_newsletter()

        self.assertEqual(sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['reader@example.com'])
        self.assertIn('Свежая статья', message.body)
        recent_url = f'http://example.com{reverse("news_detail", args=[recent.pk])}'
        self.assertIn(recent_url, message.body)
        self.assertNotIn('Старая статья', message.body)
        self.assertNotIn('Статья другой категории', message.body)
        self.assertTrue(message.alternatives)
        self.assertIn(
            f'href="{recent_url}"',
            message.alternatives[0].content,
        )
