from django.urls import path
from .views import (
    ArticleCreate,
    CategoryNewsList,
    NewsCreate,
    NewsDelete,
    NewsDetail,
    NewsList,
    NewsSearch,
    NewsUpdate,
    ProfileUpdate,
    become_author,
    subscribe_to_category,
)

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('search/', NewsSearch.as_view(), name='news_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('profile/edit/', ProfileUpdate.as_view(), name='profile_edit'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('become-author/', become_author, name='become_author'),
    path(
        'categories/<int:pk>/',
        CategoryNewsList.as_view(),
        name='category_news',
    ),
    path(
        'categories/<int:pk>/subscribe/',
        subscribe_to_category,
        name='subscribe_to_category',
    ),
]