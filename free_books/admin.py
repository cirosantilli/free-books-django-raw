from django.contrib import admin

from .models import Article, Profile, ArticleVote, ArticleTagVote

admin.site.register(Article)
admin.site.register(Profile)
admin.site.register(ArticleVote)
admin.site.register(ArticleTagVote)
