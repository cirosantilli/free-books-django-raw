from django.test import TestCase, TransactionTestCase

from free_books.models import Article, ArticleTagVote, User

class ArtcleModelTestCase(TestCase):
    def setUp(self):
        pass

    def test_filter_with_at_least_one_defined_tag_upvote(self):
        user0 = User.objects.create(username='user0', email='user0@mail.com')
        user1 = User.objects.create(username='user1', email='user1@mail.com')
        tag_name = 'a'

        article_with_tag_upvote = Article.objects.create(creator=user0, title='a')
        article_tag_upvote = ArticleTagVote.objects.create(
            article=article_with_tag_upvote,
            creator=user0,
            name=tag_name,
            value=ArticleTagVote.UPVOTE,
        )

        article_with_tag_novote = Article.objects.create(creator=user0, title='a')

        article_with_tag_downvote = Article.objects.create(creator=user0, title='a')
        article_tag_downvote = ArticleTagVote.objects.create(
            article=article_with_tag_downvote,
            creator=user0,
            name=tag_name,
            value=ArticleTagVote.DOWNVOTE,
        )

        article_with_tag_upvote_wrong_tag = Article.objects.create(creator=user0, title='a')
        article_tag_upvote_wrong_tag = ArticleTagVote.objects.create(
            article=article_with_tag_upvote_wrong_tag,
            creator=user0,
            name=(tag_name + 'b'),
            value=ArticleTagVote.UPVOTE,
        )

        article_with_tag_upvote_and_downvote = Article.objects.create(creator=user0, title='a')
        ArticleTagVote.objects.create(
            article=article_with_tag_upvote_and_downvote,
            creator=user0,
            name=(tag_name),
            value=ArticleTagVote.UPVOTE,
        )
        ArticleTagVote.objects.create(
            article=article_with_tag_upvote_and_downvote,
            creator=user1,
            name=(tag_name),
            value=ArticleTagVote.DOWNVOTE,
        )

        article_with_tag_upvote_non_defined = Article.objects.create(creator=user0, title='a')
        article_tag_upvote_wrong_tag = ArticleTagVote.objects.create(
            article=article_with_tag_upvote_non_defined,
            creator=user0,
            defined_by_article=False,
            name=(tag_name),
            value=ArticleTagVote.UPVOTE,
        )

        articles = Article.filter_with_at_least_one_defined_tag_upvote(Article.objects.all(), tag_name)
        self.assertEqual(
            set(articles.values_list('id', flat=True)),
            set([article_with_tag_upvote.id, article_with_tag_upvote_and_downvote.id])
        )
        self.assertEqual(articles.count(), 2)
