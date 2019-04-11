from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ..models import Question, Answer

User = get_user_model()


class TestQuestionModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            email='test1@example.com',
            password='secret'
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )

    def test_questions_with_the_same_title_have_a_different_urls(self):
        question1 = Question.objects.create(
            title='To be or not to be?',
            author=self.user)
        question2 = Question.objects.create(
            title='To be or not to be?',
            author=self.user)
        self.assertNotEqual(
            question1.slug,
            question2.slug)
        self.assertNotEqual(
            question1.get_absolute_url(),
            question2.get_absolute_url())

    def test_author_cannot_vote_for_own_question(self):
        question = Question.objects.create(
            title='To be or not to be?',
            author=self.user)
        rating_old = question.rating
        question.vote(self.user, True)
        rating_new = question.rating
        self.assertEqual(rating_old, rating_new)

    def test_user_cannot_vote_twice(self):
        question = Question.objects.create(
            title='To be or not to be?',
            author=self.user)
        question.vote(self.other_user, True)
        rating_old = question.rating
        question.vote(self.other_user, True)
        rating_new = question.rating
        self.assertEqual(rating_old, rating_new)

    def test_user_can_revote(self):
        question = Question.objects.create(
            title='To be or not to be?',
            author=self.user)
        question.vote(self.other_user, True)
        rating_old = question.rating
        question.vote(self.other_user, False)
        question.vote(self.other_user, False)
        rating_new = question.rating
        self.assertNotEqual(rating_old, rating_new)

    def test_new_questions_ordering_by_created_at(self):
        question1 = Question.objects.create(
            title='Question 1', author=self.user)
        question2 = Question.objects.create(
            title='Question 2', author=self.user)
        question3 = Question.objects.create(
            title='Question 3', author=self.user)

        self.assertEqual(
            list(Question.objects.new()),
            [question3, question2, question1]
        )

    def test_popular_questions_ordering_by_rating_and_by_created_at(self):
        question1 = Question.objects.create(
            title='Question 1', rating=2, author=self.user)
        question2 = Question.objects.create(
            title='Question 2', rating=1, author=self.user)
        question3 = Question.objects.create(
            title='Question 3', rating=3, author=self.user)
        question4 = Question.objects.create(
            title='Question 2', rating=2, author=self.user)
        self.assertEqual(
            list(Question.objects.popular()),
            [question3, question4, question1, question2]
        )


class TestAnswerModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            email='test1@example.com',
            password='secret'
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )
        self.question = Question.objects.create(
            title='To be or not to be?',
            author=self.user)

    def test_only_question_owner_can_mark_an_answer_as_correct(self):
        answer = Answer.objects.create(
            text='Answer',
            question=self.question,
            author=self.other_user)

        self.assertTrue(self.question.author, self.user)
        self.assertTrue(answer.mark(self.user))

        self.assertNotEqual(self.question.author, self.other_user)
        self.assertFalse(answer.mark(self.other_user))

    def test_question_owner_can_not_mark_self_answer_as_correct(self):
        answer = Answer.objects.create(
            text='Answer',
            question=self.question,
            author=self.user)

        self.assertTrue(self.question.author, self.user)
        self.assertFalse(answer.mark(self.user))

    def test_only_one_answer_can_be_marked(self):
        self.assertTrue(self.question.author, self.user)
        answer1 = Answer.objects.create(
            text='Answer 1',
            question=self.question,
            author=self.other_user)
        answer2 = Answer.objects.create(
            text='Answer 2',
            question=self.question,
            author=self.other_user)

        answer1.mark(self.user)
        self.assertTrue(self.question.has_answer)
        self.assertEqual(answer1, self.question.correct_answer)

        answer2.mark(self.user)
        self.assertTrue(self.question.has_answer)
        self.assertNotEqual(answer1, self.question.correct_answer)
        self.assertEqual(answer2, self.question.correct_answer)

        answer1.mark(self.user)
        self.assertTrue(self.question.has_answer)
        self.assertEqual(answer1, self.question.correct_answer)
        self.assertNotEqual(answer2, self.question.correct_answer)

        answer1.mark(self.user)
        self.assertFalse(self.question.has_answer)

        answer2.mark(self.user)
        self.assertTrue(self.question.has_answer)
        self.assertNotEqual(answer1, self.question.correct_answer)
        self.assertEqual(answer2, self.question.correct_answer)

    def test_user_cannot_vote_twice(self):
        answer = Answer.objects.create(
            text='To be',
            question=self.question,
            author=self.user)
        answer.vote(self.other_user, True)
        rating_old = answer.rating
        answer.vote(self.other_user, True)
        rating_new = answer.rating
        self.assertEqual(rating_old, rating_new)

    def test_user_can_revote(self):
        answer = Answer.objects.create(
            text='To be',
            question=self.question,
            author=self.user)
        answer.vote(self.other_user, True)
        rating_old = answer.rating
        answer.vote(self.other_user, False)
        answer.vote(self.other_user, False)
        rating_new = answer.rating
        self.assertNotEqual(rating_old, rating_new)
