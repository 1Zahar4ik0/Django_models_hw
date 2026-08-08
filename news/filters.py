from django_filters import CharFilter, FilterSet

from .models import Post


class NewsFilter(FilterSet):
    author = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'created_at': ['date__gt'],
        }