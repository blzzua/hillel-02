import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from django.views.generic import ListView
from django.views import View

from feedback.forms import FeedbackForm
from feedback.models import Feedback
from django.core.cache import caches
from project.constants import CACHE_KEY

# from django.core.cache import cache
cache = caches['feedback']


class FeedbackView(View):
    @method_decorator(login_required(login_url=reverse_lazy('accounts_login')))
    def post(self, request):
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            form.save(fill_name=request.user.username)
            cache.clear()
            return redirect(reverse('feedback_list'))
        else:
            return render(request, 'feedback/feedback_index.html', context={'form': form})

    def get(self, request):  # feedback_index
        form = FeedbackForm()
        return render(request, 'feedback/feedback_index.html', context={'form': form})


class FeedbackListView(ListView):
    model = Feedback
    paginate_by = 5
    paginator = Paginator
    template_name = 'feedback/list.html'

    def get_queryset(self):
        qs = cache.get(CACHE_KEY['feedback'])
        if not qs:
            logging.warning("cache miss: feedback")
            qs = super().get_queryset().order_by('-created_at')
            cache.set(CACHE_KEY['feedback'], qs)
        return qs

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
