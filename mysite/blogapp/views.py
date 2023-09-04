from django.shortcuts import render
from django.views.generic import ListView

from blogapp.models import Article


class ArticleListView(ListView):
    model = Article
    queryset = (
        Article.objects
        .select_related('author', 'category')
        .prefetch_related('tags')
        .defer('content')
    )
    template_name = "blogapp//article_list.html"
    context_object_name = "articles"
