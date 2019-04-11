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
        self.paginate_by_page = settings.PAGINATE_QUESTIONS
        self.paginate_last_page = self.paginate_by_page//2
        total_questions = self.paginate_by_page + self.paginate_last_page

        self.total_pages = total_questions // self.paginate_by_page
        if (total_questions % self.paginate_by_page):
            self.total_pages += 1

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
        self.assertEqual(len(questions), self.paginate_by_page)

        response_last_page = self.client.get(reverse('question:index') + '?page={}'.format(self.total_pages))
        questions_last_page = response_last_page.context['questions']
        self.assertEqual(response_last_page.status_code, 200)
        self.assertEqual(len(questions_last_page), self.paginate_last_page)

        response_last_page2 = self.client.get(reverse('question:index') + '?page=last')
        self.assertEqual(response_last_page2.status_code, 200)
        self.assertEqual([*questions_last_page], [*response_last_page2.context['questions']])

    def test_questions_sorted_by_pub_date(self):
        response = self.client.get(reverse('question:index'))
        questions = list(response.context['questions'])
        for i in range(len(questions) - 1):
            self.assertGreater(questions[i].pub_date, questions[i+1].pub_date)

    def test_questions_sorted_by_rating_and_pub_date(self):
        exist_questions = Question.objects.popular()[:self.paginate_by_page]
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

    def test_search_questions_by_title_and_text(self):
        url = reverse('question:search') + '?q={}'

        question1 = Question.objects.create(
            title="Question 1 title",
            text="Some test about questions",
            author=self.user)
        question2 = Question.objects.create(
            title="Title of second question", author=self.user)
        question3 = Question.objects.create(
            title="No title", author=self.user)

        response = self.client.get(url.format('question'))
        self.assertEqual(
            set(response.context["questions"]),
            set([question1, question2])
        )

        response = self.client.get(url.format('question+title'))
        self.assertEqual(
            set(response.context["questions"]),
            set([question1, question2, question3])
        )

        response = self.client.get(url.format('about+second'))
        self.assertEqual(
            set(response.context["questions"]),
            set([question1, question2])
        )

    def test_search_questions_by_tags(self):
        url = reverse('question:search') + '?q=tag:{}'

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

        response = self.client.get(url.format('baz'))
        self.assertEqual(
            set(response.context["questions"]),
            set([question1, question3])
        )

        response = self.client.get(url.format('ba'))
        self.assertEqual(
            set(response.context["questions"]),
            set([question1, question2, question3])
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
        self.paginate_by_page = settings.PAGINATE_ANSWERS
        self.paginate_last_page = self.paginate_by_page//2
        total_questions = self.paginate_by_page + self.paginate_last_page

        self.total_pages = total_questions // self.paginate_by_page
        if (total_questions % self.paginate_by_page):
            self.total_pages += 1

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
        self.assertEqual(len(answers), self.paginate_by_page)

        response_last_page = self.client.get(self.question.get_absolute_url() + '?page={}'.format(self.total_pages))
        answers_last_page = response_last_page.context['answers']
        self.assertEqual(len(answers_last_page), self.paginate_last_page)

        response_last_page2 = self.client.get(self.question.get_absolute_url() + '?page=last')
        self.assertEqual([*answers_last_page], [*response_last_page2.context['answers']])

    def test_questions_sorted_by_rating_and_pub_date(self):
        exist_answers = self.question.answer_set.popular()[:self.paginate_by_page]
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

    def test_authorized_user_can_do_only_one_question_vote_up(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)

        self.assertEqual(self.question.rating, 0)
        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)

        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)

    def test_authorized_user_can_do_only_one_question_vote_down(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)

        self.assertEqual(self.question.rating, 0)
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1)

        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1)


    def test_authorized_user_can_do_question_vote_toggle(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)
        
        self.assertEqual(self.question.rating, 0)
        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, -1)

        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

        response = self.client.post(self.question.get_vote_url(), {'value': 'true'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 1)

        response = self.client.post(self.question.get_vote_url(), {'value': 'false'})
        self.assertEqual(Question.objects.get(pk=self.question.pk).rating, 0)

    def test_authorized_user_can_do_only_one_answer_vote_up(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.answer.rating, 0)
        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)

        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)

    def test_authorized_user_can_do_only_one_answer_vote_down(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.answer.rating, 0)
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1)

        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1)

    def test_authorized_user_can_do_answer_vote_toggle(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.answer.rating, 0)
        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, -1)

        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)

        response = self.client.post(self.answer.get_vote_url(), {'value': 'true'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 1)

        response = self.client.post(self.answer.get_vote_url(), {'value': 'false'})
        self.assertEqual(Answer.objects.get(pk=self.answer.pk).rating, 0)


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

    def test_not_question_author_can_not_mark_answer(self):
        self.client.login(username=self.answer_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False)
        response = self.client.post(self.answer.get_mark_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.get(pk=self.question.pk).has_answer, False)

    def test_question_author_can_mark_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False)
        response = self.client.post(self.answer.get_mark_url())
        self.assertEqual(response.status_code, 200)
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True)
        self.assertEqual(self.answer, question.correct_answer)

    def test_question_author_can_unmark_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.assertEqual(self.question.has_answer, False)
        response = self.client.post(self.answer.get_mark_url())
        self.assertEqual(Question.objects.get(pk=self.question.pk).has_answer, True)
        response = self.client.post(self.answer.get_mark_url())
        self.assertEqual(Question.objects.get(pk=self.question.pk).has_answer, False)

    def test_question_author_can_mark_other_answer(self):
        self.client.login(username=self.question_author.username,
                          password=self.password)

        self.answer2 = Answer.objects.create(
            text='Useful Answer',
            author=self.answer_author,
            question=self.question
        )

        self.assertEqual(self.question.has_answer, False)
        response = self.client.post(self.answer.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True)
        self.assertEqual(question.correct_answer, self.answer)

        response = self.client.post(self.answer2.get_mark_url())
        question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(question.has_answer, True)
        self.assertEqual(question.correct_answer, self.answer2)
