from django.test import TestCase, TransactionTestCase

from free_books.models import Article, ArticleVote, ArticleTagVote, User

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

    def test_get_articles_with_most_net_votes(self):
        user0 = User.objects.create(username='user0', email='user0@mail.com')
        user1 = User.objects.create(username='user1', email='user1@mail.com')

        article_with_one_upvote = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_one_upvote,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )

        article_with_two_upvotes = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_two_upvotes,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )
        ArticleVote.objects.create(
            article=article_with_two_upvotes,
            creator=user1,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )

        article_with_one_downvote = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_one_downvote,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.DOWNVOTE,
        )

        article_with_no_votes = Article.objects.create(creator=user0, title='a')

        article_with_one_upvote_and_one_downvote = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_one_upvote_and_one_downvote,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )
        ArticleVote.objects.create(
            article=article_with_one_upvote_and_one_downvote,
            creator=user1,
            type=ArticleVote.LIKE,
            value=ArticleVote.DOWNVOTE,
        )

        # Tested action.

        articles = Article.get_articles_with_most_net_votes()

        # Assertions.

        values = articles.values()

        self.assertEqual(articles.count(), 5)

        article = values[0]
        self.assertEqual(
            article['id'],
            article_with_two_upvotes.id
        )
        self.assertEqual(
            article['net_votes'],
            2
        )

        article = values[1]
        self.assertEqual(
            article['id'],
            article_with_one_upvote.id
        )
        self.assertEqual(
            article['net_votes'],
            1
        )

        article = values[2]
        article2 = values[3]
        self.assertEqual(
            set([article['id'], article2['id']]),
            set([article_with_no_votes.id, article_with_one_upvote_and_one_downvote.id])
        )
        self.assertEqual(
            article['net_votes'],
            0
        )
        self.assertEqual(
            article2['net_votes'],
            0
        )

        article = values[4]
        self.assertEqual(
            article['id'],
            article_with_one_downvote.id
        )
        self.assertEqual(
            article['net_votes'],
            -1
        )

    def test_filter_by_tag_and_sort_by_upvotes(self):
        """
        Possibly problematic because if it was done with joins as it requires one join
        with each vote table, which can multiply the number of values.
        """
        user0 = User.objects.create(username='user0', email='user0@mail.com')
        user1 = User.objects.create(username='user1', email='user1@mail.com')
        tag_name = 'a'
        wrong_tag_name = 'b'

        article_with_one_upvote = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_one_upvote,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )
        ArticleTagVote.objects.create(
            article=article_with_one_upvote,
            creator=user0,
            name=tag_name,
            value=ArticleTagVote.UPVOTE,
        )
        # Add another tag vote to try and wrongly multiply an upvote JOIN count.
        ArticleTagVote.objects.create(
            article=article_with_one_upvote,
            creator=user1,
            name=tag_name,
            value=ArticleTagVote.UPVOTE,
        )

        article_with_two_upvotes_and_wrong_tag = Article.objects.create(creator=user0, title='a')
        ArticleVote.objects.create(
            article=article_with_two_upvotes_and_wrong_tag,
            creator=user0,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )
        ArticleVote.objects.create(
            article=article_with_two_upvotes_and_wrong_tag,
            creator=user1,
            type=ArticleVote.LIKE,
            value=ArticleVote.UPVOTE,
        )
        ArticleTagVote.objects.create(
            article=article_with_two_upvotes_and_wrong_tag,
            creator=user0,
            name=wrong_tag_name,
            value=ArticleTagVote.UPVOTE,
        )

        # Tested action.

        articles = Article.filter_with_at_least_one_defined_tag_upvote(Article.objects.all(), tag_name)
        articles = Article.get_articles_with_most_net_votes(articles)

        # Assertions.

        self.assertEqual(articles.count(), 1)
        article = articles.values()[0]
        self.assertEqual(
            article['id'],
            article_with_one_upvote.id
        )
        self.assertEqual(
            article['net_votes'],
            1
        )
