import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from hasker.question.models import Question, Answer, Tag
from ..serializers import (QuestionsListSerializer, QuestionSerializer,
                           AnswerSerializer, TagSerializer, VoteSerializer)

User = get_user_model()


class TestQuestionListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            email='test1@example.com',
            password='secret'
        )
        total_questions = settings.PAGINATE_QUESTIONS * 2
        for i in range(total_questions):
            Question.objects.create(
                title='Question {}'.format(i),
                text='Small question description {}'.format(i),
                author=self.user,
                rating=(total_questions) - i,
            )

    def test_questions_sorted_by_new(self):
        url = reverse('api:questions-list')
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        questions = Question.objects.new()[:settings.PAGINATE_QUESTIONS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(questions))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], questions[i].pk)

    def test_questions_sorted_by_popular(self):
        url = reverse('api:questions-list') + '?sort=popular'
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        questions = Question.objects.popular()[:settings.PAGINATE_QUESTIONS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(questions))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], questions[i].pk)


class TestQuestionDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )
        self.question = Question.objects.create(
            title='Question',
            text='Small question description',
            author=self.user
        )

    def test_response_data_is_correct(self):
        question = self.question
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], question.id)
        self.assertEqual(response.data['title'], question.title)
        self.assertEqual(response.data['text'], question.text)
        self.assertEqual(response.data['author'], question.author.username)

    def test_author_can_delete_question(self):
        question = self.question
        # Check init
        self.assertEqual(question.author, self.user)
        self.assertEqual(len(Question.objects.all()), 1)

        # Author call http method DELETE
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Question.objects.all()), 0)

    def test_other_user_cannot_delete_question(self):
        question = self.question
        # Check init
        self.assertNotEqual(question.author, self.other_user)
        self.assertEqual(len(Question.objects.all()), 1)

        # Other user call http method DELETE
        self.client.force_login(self.other_user)
        response = self.client.delete(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Question.objects.all()), 1)


class TestAnswersListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.question1 = Question.objects.create(
            title='Question 1',
            text='Small question description 1',
            author=self.user
        )
        self.question2 = Question.objects.create(
            title='Question 2',
            text='Small question description 2',
            author=self.user
        )
        total_answers = settings.PAGINATE_ANSWERS * 2
        for question in (self.question1, self.question2):
            for i in range(total_answers):
                Answer.objects.create(
                    text='Answer {} for Question {}'.format(
                        i, question.id),
                    author=self.user,
                    question=question,
                    rating=(total_answers) - i,
                )

    def test_data_is_correct_for_question(self):
        self.client.force_login(self.user)

        # test with Question 1
        question = self.question1
        url = reverse('api:question-answers-list', kwargs={'pk': question.id})
        response = self.client.get(url, format="json")
        answers = Answer.objects.popular().filter(
            question=question)[:settings.PAGINATE_ANSWERS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(answers))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], answers[i].pk)

    def test_if_question_does_not_exist_return_404(self):
        question_pk = 22
        self.client.force_login(self.user)
        url = reverse('api:question-answers-list', kwargs={'pk': question_pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestAnswerDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )
        self.question = Question.objects.create(
            title='Question',
            text='Small question description',
            author=self.user
        )
        self.answer = Answer.objects.create(
            text='Answer',
            author=self.user,
            question=self.question,
        )

    def test_response_data_is_correct(self):
        answer = self.answer
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:answer-detail', kwargs={'pk': answer.id}),format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], answer.id)
        self.assertEqual(response.data['text'], answer.text)
        self.assertEqual(response.data['author'], answer.author.username)

    def test_author_can_delete_answer(self):
        answer = self.answer
        # Check init
        self.assertEqual(answer.author, self.user)
        self.assertEqual(len(Answer.objects.all()), 1)

        # Author call http method DELETE
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:answer-detail', kwargs={'pk': answer.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Answer.objects.all()), 0)

    def test_other_user_cannot_delete_answer(self):
        answer = self.answer
        # Check init
        self.assertNotEqual(answer.author, self.other_user)
        self.assertEqual(len(Answer.objects.all()), 1)

        # Other user call http method DELETE
        self.client.force_login(self.other_user)
        response = self.client.delete(reverse('api:answer-detail', kwargs={'pk': answer.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Answer.objects.all()), 1)


class TestTagsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        total_tags = settings.PAGINATE_TAGS * 2
        for i in range(total_tags):
            Tag.objects.create(
                name='tag_{}'.format(i)
            )

    def test_response_data_is_correct(self):
        self.client.force_login(self.user)

        url = reverse('api:tags-list')
        response = self.client.get(url, format="json")
        tags = Tag.objects.all().order_by('id')[:settings.PAGINATE_TAGS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(tags))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], tags[i].pk)
            self.assertEqual(item['name'], tags[i].name)


class TestTagQuestionsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.tag = Tag.objects.create(name="foo")

    def test_if_tag_does_not_exist_return_404(self):
        tag_pk = 22
        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag_pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_has_not_questions(self):
        tag = self.tag
        other_tag = Tag.objects.create(name="bar")
        question = Question.objects.create(
            title="Question", author=self.user)
        question.tags.add(other_tag)

        # test
        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_return_all_questions_with_tag(self):
        tag = self.tag
        total_questions = settings.PAGINATE_QUESTIONS * 2
        for i in range(total_questions):
            question = Question.objects.create(
                title="Question {}".format(i),
                author=self.user)
            question.tags.add(tag)

        # test
        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag.id})
        response = self.client.get(url, format="json")
        questions = Question.objects.popular().filter(tags=tag)[:settings.PAGINATE_QUESTIONS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], total_questions)
        self.assertEqual(len(response.data['results']), len(questions))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], questions[i].pk)


class TestSearchListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )

        self.question1 = Question.objects.create(
            title="Snow",
            text="Why is snow white?",
            author=self.user)
        self.question2 = Question.objects.create(
            title="Title of Second question",
            author=self.user)
        self.question3 = Question.objects.create(
            title="No title",
            text="I am second man?",
            author=self.user)

    def test_search_questions_by_title_and_text(self):
        url = reverse('api:search') + '?q={}'
        self.client.force_login(self.user)

        matches = [{'id': 1,
                    'query': 'Second',
                    'result': (self.question2.pk, self.question3.pk)},
                   {'id': 2,
                    'query': 'white+man',
                    'result': (self.question1.pk, self.question3.pk)},
                   {'id': 3,
                    'query': 'WhItE+TiTlE',
                    'result': (self.question1.pk, self.question2.pk, self.question3.pk)}]

        for request in matches:
            response = self.client.get(url.format(request['query']), format="json")
            response_result = [item['pk'] for item in response.data['results']]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                set(response_result),
                set(request['result']),
                'Fail in request #{} from matches'.format(request['id']))


    def test_search_questions_by_tags(self):
        tag1 = Tag.objects.create(name="foo")
        tag2 = Tag.objects.create(name="bar")
        tag3 = Tag.objects.create(name="baz")

        self.question1.tags.add(*[tag1, tag3])
        self.question2.tags.add(tag2)
        self.question3.tags.add(*[tag2, tag3])

        url = reverse('api:search') + '?q=tag:{}'
        self.client.force_login(self.user)

        matches = [{'id': 1,
                    'query': 'bar',
                    'result': (self.question2.pk, self.question3.pk)},
                   {'id': 2,
                    'query': 'ba',
                    'result': (self.question1.pk, self.question2.pk, self.question3.pk)}]

        for request in matches:
            response = self.client.get(url.format(request['query']), format="json")
            response_result = [item['pk'] for item in response.data['results']]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                set(response_result),
                set(request['result']),
                'Fail in request #{} from matches'.format(request['id']))


class TestTrendingQuestionsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        total_questions = settings.TRENDING_QUESTIONS_LIMIT * 2
        for i in range(total_questions):
            Question.objects.create(
                title='Question {}'.format(i),
                author=self.user,
                rating=(total_questions) - i,
            )

    def test_trending_questions_sorted_by_popular(self):
        self.client.force_login(self.user)
        url = reverse('api:trending-questions')
        response = self.client.get(url, format="json")
        questions = Question.objects.popular()[:settings.TRENDING_QUESTIONS_LIMIT]
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(questions))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], questions[i].pk)


class TestVoteViews(TestCase):
    def setUp(self):
        # Question Author
        self.question_author = User.objects.create_user(
            username='test1',
            email='test1@eamil.com',
            password='top_secret'
        )
        self.question_author_token = self.client.post(
            reverse('api:api-token-auth'),
            data=json.dumps({'username': 'test1', 'password': 'top_secret'}),
            content_type='application/json'
        ).data.get('token')

        # Answer Author
        self.answer_author = User.objects.create_user(
            username='test2',
            email='test2@eamil.com',
            password='top_secret'
        )
        self.answer_author_token = self.client.post(
            reverse('api:api-token-auth'),
            data=json.dumps({'username': 'test2', 'password': 'top_secret'}),
            content_type='application/json'
        ).data.get('token')

        # Question
        self.question = Question.objects.create(
            title='question1',
            text='text1',
            author=self.question_author,
            rating=0,
        )
        self.question_vote_url = reverse('api:question-vote', kwargs={'pk': self.question.pk})

        # Answer
        self.answer = Answer.objects.create(
            text='answer1',
            author=self.answer_author,
            question=self.question,
            rating=0,
        )
        self.answer_vote_url = reverse('api:answer-vote', kwargs={'pk': self.answer.pk})

    def test_unauthorized_user_cannot_vote_for_question(self):
        response = self.client.post(
            self.question_vote_url,
            data=json.dumps({'value': 'true'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_for_vote_for_answer(self):
        response = self.client.post(
            self.answer_vote_url,
            data=json.dumps({'value': 'true'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ######################
    # Test Question Vote #
    ######################

    def make_question_vote_request(self, value):
        return self.client.post(
            self.question_vote_url,
            data={'value': value},
            HTTP_AUTHORIZATION='Token {}'.format(self.answer_author_token)
        )

    def test_authorized_user_can_do_only_one_question_vote_up(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        # first vote
        response = self.make_question_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after first vote')
        self.assertEqual(response.data.get('rating'), 1, 'after first vote')

        # second vote
        response = self.make_question_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after second vote')
        self.assertEqual(response.data.get('rating'), 1, 'after second vote')


    def test_authorized_user_can_do_only_one_question_vote_down(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        # first vote
        response = self.make_question_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1, 'after first vote')
        self.assertEqual(response.data.get('rating'), -1, 'after first vote')

        # second vote
        response = self.make_question_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1, 'after second vote')
        self.assertEqual(response.data.get('rating'), -1, 'after second vote')


    def test_authorized_user_can_do_question_vote_toggle(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        # first vote
        response = self.make_question_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after first vote')
        self.assertEqual(response.data.get('rating'), 1, 'after first vote')

        # second vote
        response = self.make_question_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0, 'after second vote')
        self.assertEqual(response.data.get('rating'), 0, 'after second vote')

    ####################
    # Test Answer Vote #
    ####################

    def make_answer_vote_request(self, value):
        return self.client.post(
            self.answer_vote_url,
            data={'value': value},
            HTTP_AUTHORIZATION='Token {}'.format(self.question_author_token)
        )

    def test_authorized_user_can_do_only_one_answer_vote_up(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        # first vote
        response = self.make_answer_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after first vote')
        self.assertEqual(response.data.get('rating'), 1, 'after first vote')

        # second vote
        response = self.make_answer_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after second vote')
        self.assertEqual(response.data.get('rating'), 1, 'after second vote')


    def test_authorized_user_can_do_only_one_answer_vote_down(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        # first vote
        response = self.make_answer_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1, 'after first vote')
        self.assertEqual(response.data.get('rating'), -1, 'after first vote')

        # second vote
        response = self.make_answer_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1, 'after second vote')
        self.assertEqual(response.data.get('rating'), -1, 'after second vote')


    def test_authorized_user_can_do_answer_vote_toggle(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        # first vote
        response = self.make_answer_vote_request('true')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after first vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after first vote')
        self.assertEqual(response.data.get('rating'), 1, 'after first vote')

        # second vote
        response = self.make_answer_vote_request('false')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'after second vote')
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0, 'after second vote')
        self.assertEqual(response.data.get('rating'), 0, 'after second vote')
