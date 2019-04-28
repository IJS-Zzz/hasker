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

        self.paginate_by_page = settings.PAGINATE_QUESTIONS
        self.paginate_last_page = self.paginate_by_page//2
        total_questions = self.paginate_by_page + self.paginate_last_page

        self.total_pages = total_questions // self.paginate_by_page
        if (total_questions % self.paginate_by_page):
            self.total_pages += 1

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

    def test_data_is_correct(self):
        question = self.question
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], question.id)

    def test_only_owner_can_delete_question(self):
        question = self.question
        self.assertEqual(len(Question.objects.all()), 1)

        # Other user call http method DELETE
        self.client.force_login(self.other_user)
        response1 = self.client.delete(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        self.assertEqual(len(Question.objects.all()), 1)

        # Author call http method DELETE
        self.client.force_login(self.user)
        response2 = self.client.delete(reverse('api:question-detail', kwargs={'pk': question.id}), format="json")
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.assertEqual(len(Question.objects.all()), 0)


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

        self.paginate_by_page = settings.PAGINATE_ANSWERS
        self.paginate_last_page = self.paginate_by_page//2
        total_answers = self.paginate_by_page + self.paginate_last_page

        self.total_pages = total_answers // self.paginate_by_page
        if (total_answers % self.paginate_by_page):
            self.total_pages += 1

        for question in (self.question1, self.question2):
            for i in range(total_answers):
                Answer.objects.create(
                    text='Answer {} for Question {}'.format(
                        i, question.id),
                    author=self.user,
                    question=question,
                    rating=(total_answers) - i,
                )

    def test_data_is_correct_for_each_question(self):
        self.client.force_login(self.user)

        # test with question1
        question = self.question1
        url = reverse('api:question-answers-list', kwargs={'pk': question.id})
        response = self.client.get(url, format="json")
        answers = question.answer_set.popular()[:settings.PAGINATE_ANSWERS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(answers))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], answers[i].pk)

        # test with question2
        question = self.question1
        url = reverse('api:question-answers-list', kwargs={'pk': question.id})
        response = self.client.get(url, format="json")
        answers = question.answer_set.popular()[:settings.PAGINATE_ANSWERS]

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

    def test_data_is_correct(self):
        answer = self.answer
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:answer-detail', kwargs={'pk': answer.id}),format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], answer.id)

    def test_only_owner_can_delete_answer(self):
        answer = self.answer
        self.assertEqual(len(Answer.objects.all()), 1)

        # Other user call http method DELETE
        self.client.force_login(self.other_user)
        response1 = self.client.delete(reverse('api:answer-detail', kwargs={'pk': answer.id}), format="json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        self.assertEqual(len(Answer.objects.all()), 1)

        # Author call http method DELETE
        self.client.force_login(self.user)
        response2 = self.client.delete(reverse('api:answer-detail', kwargs={'pk': answer.id}), format="json")
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.assertEqual(len(Answer.objects.all()), 0)


class TestTagsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )

        self.paginate_by_page = settings.PAGINATE_TAGS
        self.paginate_last_page = self.paginate_by_page//2
        total_tags = self.paginate_by_page + self.paginate_last_page

        self.total_pages = total_tags // self.paginate_by_page
        if (total_tags % self.paginate_by_page):
            self.total_pages += 1

        for i in range(total_tags):
            Tag.objects.create(
                name='tag_{}'.format(i)
            )

    def test_data_is_correct(self):
        self.client.force_login(self.user)

        url = reverse('api:tags-list')
        response = self.client.get(url, format="json")
        tags = Tag.objects.all().order_by('id')[:settings.PAGINATE_TAGS]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(tags))
        for i, item in enumerate(response.data['results']):
            self.assertEqual(item['pk'], tags[i].pk)


class TestTagQuestionsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )

    def test_if_tag_does_not_exist_return_404(self):
        tag_pk = 22
        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag_pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_has_not_questions(self):
        tag = Tag.objects.create(name="foo")

        other_tag = Tag.objects.create(name="bar")
        question = Question.objects.create(
            title="Question", author=self.user)
        question.tags.add(other_tag)

        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag.id})
        response = self.client.get(url, format="json")
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), 0)

    def test_return_all_questions_with_tag(self):
        tag = Tag.objects.create(name="foo")

        paginate_by_page = settings.PAGINATE_QUESTIONS
        paginate_last_page = paginate_by_page//2
        total_questions = paginate_by_page + paginate_last_page

        for i in range(total_questions):
            question = Question.objects.create(
                title="Question {}".format(i),
                author=self.user)
            question.tags.add(tag)

        self.client.force_login(self.user)
        url = reverse('api:tag-questions-list', kwargs={'pk': tag.id})
        response = self.client.get(url, format="json")
        questions = Question.objects.popular().filter(tags=tag)[:paginate_by_page]

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

    def test_search_questions_by_title_and_text(self):
        question1 = Question.objects.create(
            title="Snow",
            text="Why is snow white?",
            author=self.user)
        question2 = Question.objects.create(
            title="Title of Second question",
            author=self.user)
        question3 = Question.objects.create(
            title="No title",
            text="I am second man?",
            author=self.user)

        url = reverse('api:search') + '?q={}'
        self.client.force_login(self.user)

        q = 'Second'
        response = self.client.get(url.format(q), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(item['pk'] for item in response.data['results']),
            set((question2.pk, question3.pk))
        )

        q = 'white+man'
        response = self.client.get(url.format(q), format="json")
        self.assertEqual(
            set(item['pk'] for item in response.data['results']),
            set((question1.pk, question3.pk))
        )

        q = 'WhItE+TiTlE'
        response = self.client.get(url.format(q), format="json")
        self.assertEqual(
            set(item['pk'] for item in response.data['results']),
            set((question1.pk, question2.pk, question3.pk))
        )

    def test_search_questions_by_tags(self):
        tag1 = Tag.objects.create(name="foo")
        tag2 = Tag.objects.create(name="bar")
        tag3 = Tag.objects.create(name="baz")

        question1 = Question.objects.create(
            title="Question 1", author=self.user)
        question1.tags.add(*[tag1, tag3])

        question2 = Question.objects.create(
            title="Question 2", author=self.user)
        question2.tags.add(tag2)

        question3 = Question.objects.create(
            title="Question 3", author=self.user)
        question3.tags.add(*[tag2, tag3])

        url = reverse('api:search') + '?q=tag:{}'
        self.client.force_login(self.user)

        q_tag = 'bar'
        response = self.client.get(url.format(q_tag), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(item['pk'] for item in response.data['results']),
            set((question2.pk, question3.pk))
        )

        q_tag = 'ba'
        response = self.client.get(url.format(q_tag), format="json")
        self.assertEqual(
            set(item['pk'] for item in response.data['results']),
            set((question1.pk, question2.pk, question3.pk))
        )


class TestTrendingQuestionsListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )

    def test_trending_questions_sorted_by_popular(self):
        total_questions = settings.TRENDING_QUESTIONS_LIMIT * 2
        for i in range(total_questions):
            Question.objects.create(
                title='Question {}'.format(i),
                author=self.user,
                rating=(total_questions) - i,
            )

        self.client.force_login(self.user)
        url = reverse('api:trending-questions')
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        questions = Question.objects.popular()[:settings.TRENDING_QUESTIONS_LIMIT]
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
        self.question_url = reverse('api:question-vote', kwargs={'pk': self.question.pk})

        # Answer
        self.answer = Answer.objects.create(
            text='answer1',
            author=self.answer_author,
            question=self.question,
            rating=0,
        )
        self.answer_url = reverse('api:answer-vote', kwargs={'pk': self.answer.pk})

    def test_unauthorized_user_can_not_vote_for_question(self):
        response = self.client.post(
            self.question_url,
            data=json.dumps({'value': 'true'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_can_not_for_vote_for_answer(self):
        response = self.client.post(
            self.answer_url,
            data=json.dumps({'value': 'true'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ######################
    # Test Question Vote #
    ######################

    def make_question_vote_request(self, value):
        return self.client.post(
            self.question_url,
            data={'value': value},
            HTTP_AUTHORIZATION='Token {}'.format(self.answer_author_token)
        )

    def test_authorized_user_can_do_only_one_question_vote_up(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        response = self.make_question_vote_request('true')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_question_vote_request('true')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorized_user_can_do_only_one_question_vote_down(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        response = self.make_question_vote_request('false')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1)
        self.assertEqual(response.data.get('rating'), -1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_question_vote_request('false')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1)
        self.assertEqual(response.data.get('rating'), -1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorized_user_can_do_question_vote_toggle(self):
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        response = self.make_question_vote_request('true')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_question_vote_request('false')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)
        self.assertEqual(response.data.get('rating'), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    ####################
    # Test Answer Vote #
    ####################

    def make_answer_vote_request(self, value):
        return self.client.post(
            self.answer_url,
            data={'value': value},
            HTTP_AUTHORIZATION='Token {}'.format(self.question_author_token)
        )

    def test_authorized_user_can_do_only_one_answer_vote_up(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        response = self.make_answer_vote_request('true')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_answer_vote_request('true')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorized_user_can_do_only_one_answer_vote_down(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        response = self.make_answer_vote_request('false')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1)
        self.assertEqual(response.data.get('rating'), -1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_answer_vote_request('false')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1)
        self.assertEqual(response.data.get('rating'), -1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorized_user_can_do_answer_vote_toggle(self):
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        response = self.make_answer_vote_request('true')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)
        self.assertEqual(response.data.get('rating'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.make_answer_vote_request('false')

        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)
        self.assertEqual(response.data.get('rating'), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
