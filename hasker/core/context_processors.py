from django.conf import settings


def metadata(request):
    """
    Add some generally useful metadata to the template context
    """
    return {'homepage_url': settings.HOMEPAGE_URL,}
