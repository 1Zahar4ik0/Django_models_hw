from django.urls import path
from .views import (
    NewsCreate,
    NewsDelete,
    NewsDetail,
    NewsList,
    NewsSearch,
    NewsUpdate,
)

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('search/', NewsSearch.as_view(), name='news_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),

]