from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

def new_answer_email_notify(request, question, answer):
    absolute_url = request.build_absolute_uri(question.url)
    subject = _('You have new answer for your question')
    message = _('{} answered to your question `{}`.\nYou can read answer by link: {}').format(
        answer.author.username,
        question.title,
        absolute_url
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [question.author.email])
