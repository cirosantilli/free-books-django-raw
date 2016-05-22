import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

from .models import Article, ArticleForm, ArticleVote, ArticleVoteForm, UserForm, Profile, ProfileForm
from .permissions import has_perm
from .util import filter_by_get, get_page, get_verbose, get_verboses, Http401, render_markup_safe, website_name

def home(request):
    return render(request, 'home.html', {'title': website_name})

def help(request):
    return render(request, 'help.html', {'title': _('Help')})

def about(request):
    return render(request, 'about.html', {'title': _('About')})

def article_index(request):
    sort = request.GET.get('sort')
    if sort == 'last-edited':
        articles = Article.objects.order_by('-last_edited')
    elif sort == 'net-votes':
        articles = Article.get_articles_with_most_net_votes()
    else:
        articles = Article.objects.order_by('-date_published')
    articles = filter_by_get(articles, request, (('creator__username', 'creator'),))
    articles = get_page(request, articles, 25)
    return render(request, 'articles/index.html', {
        'articles': articles,
        'title': _('Articles'),
        'verbose_names': [
            get_verbose(Article, 'title'),
            get_verbose(Article, 'creator'),
            _('Net votes'),
            get_verbose(Article, 'date_published'),
            get_verbose(Article, 'last_edited'),
        ],

    })

def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    user = request.user
    context = {
        'ArticleVote': ArticleVote,
        'article': article,
        'body': render_markup_safe(article.body),
        'show_delete': has_perm(user, 'article_delete', article),
        'show_edit': has_perm(user, 'article_edit', article),
        'show_new': has_perm(user, 'article_new'),
        'show_vote': has_perm(user, 'article_vote', article),
        'title': article.title,
    }
    if (user.is_authenticated()):
        context.update({
            'has_downvoted': user.profile.has_downvoted(article),
            'has_upvoted': user.profile.has_upvoted(article),
        })
    return render(request, 'articles/detail.html', context)

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
            old_value = vote.value
        else:
            vote = None
            old_value = None
        form = ArticleVoteForm(post, instance=vote)
        if form.is_valid():
            vote = form.save(commit=False)
            if old_value == vote.value:
                vote.delete()
                return HttpResponse()
            else:
                vote.date_created = timezone.now()
                vote.save()
            return HttpResponse()
    return HttpResponseNotFound()

def user_index(request):
    users = get_page(request, User.objects.order_by('-date_joined'), 25)
    return render(request, 'users/index.html', {
        'users': users,
        'title': _('Users'),
        'verbose_names': [
            get_verbose(User, 'username'),
            _('Linear Reputation'),
            _('Real Name'),
            get_verbose(User, 'date_joined'),
            get_verbose(Profile, 'last_edited'),
        ],
    })

def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/detail.html', {
        'ArticleVote': ArticleVote,
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

def article_vote_index(request):
    votes = ArticleVote.objects.order_by('-date_created')
    votes = filter_by_get(votes, request, (
        ('article__id', 'article'),
        ('value', 'value'),
        ('user__username', 'user')
    ))
    votes = get_page(request, votes, 25)
    return render(request, 'article_votes/index.html', {
        'votes': votes,
        'title': _('Votes'),
        'verbose_names': [get_verbose(cls, name) for cls, name in (
            (User, 'username'),
            (Article, 'title'),
            # (ArticleVote, 'type'),
            (ArticleVote, 'value'),
            (ArticleVote, 'date_created')
        )]
    })
