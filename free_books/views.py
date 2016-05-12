import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _

from .models import Article, ArticleForm, UserForm, ProfileForm
from .permissions import has_perm
from .util import Http401, website_name

def home(request):
    return render(request, 'home.html', {'title': website_name})

def article_index(request):
    articles = Article.objects.order_by('-pub_date')[:100]
    return render(request, 'articles/index.html', {
        'articles': articles,
        'show_new': has_perm(request.user, 'article_new'),
        'title': _('Articles'),
    })

def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'articles/detail.html', {
        'article': article,
        'show_delete': has_perm(request.user, 'article_delete', article),
        'show_edit': has_perm(request.user, 'article_edit', article),
        'show_new': has_perm(request.user, 'article_new'),
        'title': article.title,
    })

@login_required
def article_new(request):
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
        'submit_value': _('Create'),
        'title': _('New article'),
    })

# TODO store an undeletable permanent version history of articles
@login_required
def article_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if not has_perm(request.user, 'article_edit', article):
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
        'submit_value': _('Save changes'),
        'title': _('Editing article'),
    })

def article_delete(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if not has_perm(request.user, 'article_edit', article):
        return Http401()
    if request.method == 'POST':
        article.delete()
        return redirect('article_index')
    else:
        return HttpResponseNotAllowed()

def user_index(request):
    users = User.objects.order_by('-date_joined')[:100]
    print(users[0].profile.last_edited);
    return render(request, 'users/index.html', {
        'users': users,
        'title': _('Users'),
    })

def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/detail.html', {
        'anuser': user,
        'show_edit': has_perm(request.user, 'user_edit', user),
        'title': _('User') + ' ' + user.username,
    })

@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not has_perm(request.user, 'user_edit', user):
        return Http401()
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user, prefix='user')
        profile_form = ProfileForm(request.POST, instance=user.profile, prefix='profile')
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.last_edited = timezone.now()
            profile.save()
            return redirect(user)
        # TODO else? Or does it throw?
    else:
        user_form = UserForm(instance=user, prefix='user')
        profile_form = ProfileForm(instance=user.profile, prefix='profile')
    return render(request, 'users/new.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'form_action': reverse('user_edit', args=[user.id]),
        'submit_value': _('Save changes'),
        'title': _('User') + ' ' + user.username,
    })

@login_required
def user_settings(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/settings.html', {'title': _('Account settings')})
