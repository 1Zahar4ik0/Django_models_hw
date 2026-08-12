from .filters import NewsFilter
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import PostForm, ProfileForm
from .models import ARTICLE, NEWS, Author, Category, Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.decorators.http import require_POST

class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        context['filterset'] = self.filterset

        context['is_not_author'] = (
                self.request.user.is_authenticated
                and not self.request.user.groups.filter(name='authors').exists()
        )

        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(post_type='NS')
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

class NewsSearch(NewsList):
    pass

class NewsDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'post'

class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        news_today = Post.objects.filter(
            author__user=self.request.user,
            post_type=NEWS,
            created_at__date=timezone.localdate(),
        ).count()

        if news_today >= 3:
            raise PermissionDenied(
                'Вы не можете публиковать более трёх новостей в сутки.'
            )

        form.instance.author = Author.objects.get(user=self.request.user)
        form.instance.post_type = NEWS
        return super().form_valid(form)


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.author = Author.objects.get(user=self.request.user)
        form.instance.post_type = ARTICLE
        return super().form_valid(form)

class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=NEWS)

class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=ARTICLE)

class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)

    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=NEWS)


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('news_list')

    def get_object(self, queryset=None):
        return self.request.user

@login_required
def become_author(request):
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(request.user)
    Author.objects.get_or_create(user=request.user)
    return redirect('news_list')

class CategoryNewsList(ListView):
    model = Post
    template_name = 'category_news.html'
    context_object_name = 'category_news'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                post_type=NEWS,
                categories__pk=self.kwargs['pk'],
            )
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['category'] = category
        context['is_subscribed'] = (
            self.request.user.is_authenticated
            and category.subscribers.filter(
                pk=self.request.user.pk,
            ).exists()
        )
        return context

@login_required
@require_POST
def subscribe_to_category(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user)
    return redirect('category_news', pk=category.pk)
