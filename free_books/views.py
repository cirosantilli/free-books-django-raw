import datetime

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _

from .models import Article, ArticleForm
from .util import Http401

def profile(request):
    return render(request, 'registration/profile.html', {'title': 'Profile'})

def article_index(request):
    articles = Article.objects.order_by('-pub_date')[:100]
    return render(request, 'articles/index.html', {
        'articles': articles,
        'title': 'Articles',
    })
def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'articles/detail.html', {
        'article': article,
        'title': article.title,
    })

def article_new(request):
    if not request.user.is_authenticated():
        return Http401()
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.creator = request.user
            article.save()
            return redirect(article)
        # TODO else? Or does it throw?
    else:
        form = ArticleForm()
    return render(request, 'articles/new.html', {
        'form': form,
        'form_action': reverse('article_new'),
        'submit_value': 'Create',
        'title': 'New article',
    })

def article_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if not request.user.is_authenticated() or request.user != article.creator:
        return Http401()
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.last_edited = timezone.now()
            article.save()
            return redirect(article)
        # TODO else? Or does it throw?
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/new.html', {
        'form': form,
        'form_action': reverse('article_edit', args=[article.id]),
        'submit_value': 'Save changes',
        'title': 'Editing article',
    })

def article_delete(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if not request.user.is_authenticated() or request.user != article.creator:
        return Http401()
    if request.method == 'POST':
        article.delete()
        return redirect('article_index')
    else:
        return HttpResponseNotAllowed()
