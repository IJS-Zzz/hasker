from datetime import datetime, timedelta

from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Question, Answer, Tag

User = get_user_model()


class TestIndexView(TestCase):

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
                author=self.user,
                rating=(total_questions) - i
            )

    def test_paginate_question_by_page(self):
        response = self.client.get(reverse('question:index'))
        questions = response.context['questions']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(questions), settings.PAGINATE_QUESTIONS)

    def test_questions_sorted_by_pub_date(self):
        response = self.client.get(reverse('question:index'))
        questions = list(response.context['questions'])
        for i in range(len(questions) - 1):
            self.assertGreater(questions[i].pub_date, questions[i+1].pub_date)

    def test_questions_sorted_by_rating_and_pub_date(self):
        exist_questions = Question.objects.popular()[:settings.PAGINATE_QUESTIONS]
        for q in exist_questions:
            Question.objects.create(
                title='{} - duplicate'.format(q.title),
                author=q.author,
                rating=q.rating
            )

        response = self.client.get(reverse('question:index') + '?sort=popular')
        questions = list(response.context['questions'])
        for i in range(len(questions) - 1):
            self.assertGreaterEqual(questions[i].rating, questions[i+1].rating)
            if questions[i].rating == questions[i+1].rating:
                self.assertGreater(questions[i].pub_date, questions[i+1].pub_date)


class TestSearchView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@example.com",
            password="secret"
        )
        self.question1 = Question.objects.create(
            title="Question 1 title",
            text="Some test about questions",
            author=self.user)
        self.question2 = Question.objects.create(
            title="Title of second question",
            author=self.user)
        self.question3 = Question.objects.create(
            title="No title",
            author=self.user)

    def test_search_questions_by_title_and_text(self):
        url = reverse('question:search') + '?q={}'

        matches = [{'id': 1,
                    'query': 'question',
                    'result': (self.question1, self.question2)},
                   {'id': 2,
                    'query': 'question+title',
                    'result': (self.question1, self.question2, self.question3)},
                   {'id': 3,
                    'query': 'about+second',
                    'result': (self.question1, self.question2)}]

        for request in matches:
            response = self.client.get(url.format(request['query']))
            self.assertEqual(
                set(response.context["questions"]),
                set(request['result']),
                'Fail in request #{} from matches'.format(request['id'])
            )

    def test_search_questions_by_tags(self):
        tag1 = Tag.objects.create(name="foo")
        tag2 = Tag.objects.create(name="bar")
        tag3 = Tag.objects.create(name="baz")

        self.question2.tags.add(tag2)
        self.question3.tags.add(*[tag2, tag3])
        self.question1.tags.add(*[tag1, tag3])

        url = reverse('question:search') + '?q=tag:{}'

        matches = [{'id': 1,
                    'query': 'baz',
                    'result': (self.question1, self.question3)},
                   {'id': 2,
                    'query': 'ba',
                    'result': (self.question1, self.question2, self.question3)}]

        for request in matches:
            response = self.client.get(url.format(request['query']))
            self.assertEqual(
                set(response.context["questions"]),
                set(request['result']),
                'Fail in request #{} from matches'.format(request['id'])
            )


class TestQuestionView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@example.com",
            password="secret"
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )
        self.question = Question.objects.create(
            title='My Question',
            author=self.user,
        )

        total_questions = settings.PAGINATE_ANSWERS * 2
        for i in range(total_questions):
            Answer.objects.create(
                text='Answer {}'.format(i),
                author=self.other_user,
                question=self.question,
                rating=(total_questions) - i
            )

    def test_paginate_question_by_page(self):
        response = self.client.get(self.question.get_absolute_url())
        answers = response.context['answers']
        self.assertEqual(len(answers), settings.PAGINATE_ANSWERS)

    def test_questions_sorted_by_rating_and_pub_date(self):
        exist_answers = self.question.answer_set.popular()[:settings.PAGINATE_ANSWERS]
        for a in exist_answers:
            Answer.objects.create(
                text='{} - duplicate'.format(a.text),
                author=a.author,
                question=a.question,
                rating=a.rating
            )

        response = self.client.get(self.question.get_absolute_url())
        answers = list(response.context['answers'])
        for i in range(len(answers) - 1):
            self.assertGreaterEqual(answers[i].rating, answers[i+1].rating)
            if answers[i].rating == answers[i+1].rating:
                self.assertGreater(answers[i].pub_date, answers[i+1].pub_date)

    def test_if_question_does_not_exist_return_404(self):
        slug = 'abracadabra'
        url = reverse('question:question', kwargs={'slug': slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_if_unauthorized_user_send_post_request_with_new_answer_redirect_to_login_page(self):
        data = {'text': 'New Answer'}
        response = self.client.post(self.question.get_absolute_url(), data)
        login_page_url = settings.LOGIN_URL + '?next=' + self.question.get_absolute_url()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], login_page_url)

    def test_authorized_user_can_add_new_answer_with_post_request(self):
        self.client.force_login(self.other_user)
        answers_count_before = Answer.objects.count()

        data = {'text': 'This is Abracadabra!'}
        response = self.client.post(self.question.get_absolute_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], self.question.get_absolute_url())
        
        answers_count_after = Answer.objects.count()
        last_answer = Answer.objects.last()
        self.assertGreater(answers_count_after, answers_count_before)
        self.assertEqual(last_answer.text, data['text'])


class TestVoteViews(TestCase):

    def setUp(self):
        self.password = 'secret'

        self.question_author = User.objects.create(username="test",
                                                   email="test@example.com",)
        self.question_author.set_password(self.password)
        self.question_author.save()

        self.answer_author = User.objects.create(username='test2',
                                                 email='test2@example.com')
        self.answer_author.set_password(self.password)
        self.answer_author.save()

        self.question = Question.objects.create(
            title='My Question',
            author=self.question_author,
        )
        self.answer = Answer.objects.create(
            text='Useful Answer',
            author=self.answer_author,
            question=self.question
        )

    def test_unauthorized_user_can_not_vote_for_question(self):
        response = self.client.post(self.question.get_vote_url())
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_can_not_for_vote_for_answer(self):
        response = self.client.post(self.answer.get_vote_url())
        self.assertEqual(response.status_code, 403)

    ######################
    # Test Question Vote #
    ######################

    def test_authorized_user_can_do_only_one_question_vote_up(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)
        self.assertEqual(self.question.rating, 0, 'Init')

        # first vote
        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(response.status_code, 200, 'after first vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after first vote')

        # second vote
        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(response.status_code, 200, 'after second vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after second vote')


    def test_authorized_user_can_do_only_one_question_vote_down(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)

        self.assertEqual(self.question.rating, 0, 'Init')

        # first vote
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(response.status_code, 200, 'after first vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1, 'after first vote')

        # second vote
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(response.status_code, 200, 'after second vote')
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1, 'after second vote')


    def test_authorized_user_can_do_question_vote_toggle(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)
        self.assertEqual(self.question.rating, 0, 'Init')

        # vote #1
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1, 'after vote #1')

        # vote #2
        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0, 'after vote #2')

        # vote #3
        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1, 'after vote #3')

        # vote #4
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0, 'after vote #4')

    ####################
    # Test Answer Vote #
    ####################

    def test_authorized_user_can_do_only_one_answer_vote_up(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)
        self.assertEqual(self.answer.rating, 0, 'Init')

        # first vote
        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after first vote')

        # second vote
        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after second vote')

    def test_authorized_user_can_do_only_one_answer_vote_down(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)
        self.assertEqual(self.answer.rating, 0, 'Init')

        # first vote
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1, 'after first vote')

        # second vote
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1, 'after second vote')

    def test_authorized_user_can_do_answer_vote_toggle(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)
        self.assertEqual(self.answer.rating, 0, 'Init')

        # vote #1
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1, 'after vote #1')

        # vote #2
        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0, 'after vote #2')

        # vote #3
        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1, 'after vote #3')

        # vote #4
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0, 'after vote #4')


class TestAnswerMarkView(TestCase):
    def setUp(self):
        self.password = 'secret'

        self.question_author = User.objects.create(username="test",
                                                   email="test@example.com",)
        self.question_author.set_password(self.password)
        self.question_author.save()

        self.answer_author = User.objects.create(username='test2',
                                                 email='test2@example.com')
        self.answer_author.set_password(self.password)
        self.answer_author.save()

        self.question = Question.objects.create(
            title='My Question',
            author=self.question_author,
        )
        self.answer = Answer.objects.create(
            text='Useful Answer',
            author=self.answer_author,
            question=self.question
        )

    def test_unauthorized_user_can_not_mark_answer(self):
        response = self.client.post(self.answer.get_mark_url())
        self.assertEqual(response.status_code, 403)

    def test_question_author_can_mark_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False, 'Init')

        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(question.has_answer, True)
        self.assertEqual(question.correct_answer, self.answer)

    def test_not_question_author_cannot_mark_answer(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False, 'Init')

        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(question.has_answer, False)


    def test_question_author_can_unmark_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False, 'Init')

        # Mark Answer
        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True, 'After Mark Answer')

        # Unmark Answer
        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, False, 'After Unmark Answer')

    def test_question_author_can_mark_other_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.answer2 = Answer.objects.create(
            text='Useful Answer',
            author=self.answer_author,
            question=self.question
        )

        self.assertEqual(self.question.has_answer, False, 'Init')

        # Mark Answer 1
        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True, 'After Mark Answer 1')
        self.assertEqual(question.correct_answer, self.answer, 'After Mark Answer 1')

        # Mark Answer 2
        response = self.client.post(self.answer2.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True, 'After Mark Answer 2')
        self.assertEqual(question.correct_answer, self.answer2, 'After Mark Answer 2')
