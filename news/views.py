from .filters import NewsFilter
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import PostForm
from .models import NEWS, Post

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

class NewsCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.post_type = NEWS
        return super().form_valid(form)

class NewsUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=NEWS)

class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=NEWS)
