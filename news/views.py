from .filters import NewsFilter
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import PostForm, ProfileForm
from .models import ARTICLE, NEWS, Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

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
        form.instance.post_type = NEWS
        return super().form_valid(form)


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
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
    return redirect('news_list')
