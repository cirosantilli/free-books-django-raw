import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

from .models import Article, ArticleForm, ArticleVote, ArticleVoteForm, UserForm, ProfileForm
from .permissions import has_perm
from .util import get_page, Http401, render_markup_safe, website_name

def home(request):
    return render(request, 'home.html', {'title': website_name})

def help(request):
    return render(request, 'help.html', {'title': _('Help')})

def about(request):
    return render(request, 'about.html', {'title': _('About')})

def article_index(request):
    articles = Article.objects.order_by('-pub_date')
    creator = request.GET.get('creator')
    if creator:
        articles = articles.filter(creator__username=creator)
    articles = get_page(request, articles, 25)
    return render(request, 'articles/index.html', {
        'articles': articles,
        'show_new': has_perm(request.user, 'article_new'),
        'title': _('Articles'),
    })

def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    user = request.user
    return render(request, 'articles/detail.html', {
        'ArticleVote': ArticleVote,
        'article': article,
        'body': render_markup_safe(article.body),
        'has_downvoted': user.profile.has_downvoted(article),
        'has_upvoted': user.profile.has_upvoted(article),
        'show_delete': has_perm(user, 'article_delete', article),
        'show_edit': has_perm(user, 'article_edit', article),
        'show_new': has_perm(user, 'article_new'),
        'show_vote': has_perm(user, 'article_vote', article),
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
        return HttpResponseNotFound()
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
    if (has_perm(request.user, 'article_delete', article)
        and request.method == 'POST'):
        article.delete()
        return redirect('article_index')
    return HttpResponseNotFound()

def article_vote(request, article_id):
    """
    - (type, value) does not exist     -> create vote
    - (type, value) exists             -> delete vote
    - type exists with different value -> change vote value
    """
    article = get_object_or_404(Article, pk=article_id)
    if (has_perm(request.user, 'article_vote', article)
            and request.method == 'POST'):
        user = request.user
        votes = ArticleVote.objects.filter(
                article=article,
                type=request.POST.get('type'),
                user=user)
        post = request.POST.copy()
        post['user'] = user.id
        post['article'] = article.id
        if (votes):
            vote = votes[0]
        else:
            vote = None
        form = ArticleVoteForm(post, instance=vote)
        if form.is_valid():
            new_vote = form.save(commit=False)
            # TODO can't get that new_vote value no matter what!
            if vote.value == new_vote['value']:
                vote.delete()
                return HttpResponse()
            else:
                new_vote.date_created = timezone.now()
                new_vote.save()
            return HttpResponse()
    return HttpResponseNotFound()

def user_index(request):
    users = get_page(request, User.objects.order_by('-date_joined'), 25)
    return render(request, 'users/index.html', {
        'users': users,
        'title': _('Users'),
    })

def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/detail.html', {
        'anuser': user,
        'about': render_markup_safe(user.profile.about),
        'show_edit': has_perm(request.user, 'user_edit', user),
        'title': _('User') + ' ' + user.username,
    })

@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not has_perm(request.user, 'user_edit', user):
        return HttpResponseNotFound()
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user, prefix='user')
        profile_form = ProfileForm(request.POST, instance=user.profile, prefix='profile')
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.last_edited = timezone.now()
            profile.save()
            return redirect(user.profile)
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
