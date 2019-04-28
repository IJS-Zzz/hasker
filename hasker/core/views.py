from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def handler403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


@requires_csrf_token
def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


@requires_csrf_token
def handler500(request):
    return render(request, 'errors/500.html', status=500)
