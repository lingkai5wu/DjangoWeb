import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic.base import ContextMixin, TemplateView, RedirectView, View
from django.views.generic.list import ListView, MultipleObjectMixin
from haystack.generic_views import SearchView
from haystack.management.commands import update_index

from ys.forms import UpdateContentForm, SelectContentForm
from ys.models import Content, Update


class FormUpdateView(FormView):
    template_name = 'ys/update.html'
    form_class = UpdateContentForm

    def form_valid(self, form):
        try:
            content_list, total = form.get_content_list()
        except ValueError as e:
            return HttpResponse(str(e))
        context = self.get_context_data()
        context['total'] = total
        context['list'] = [form.update_content(content) for content in content_list]
        Update.objects.create(update_time=timezone.now(), total=total)
        return self.render_to_response(context)

    def get_initial(self):
        return {
            'iAppId': 43,
            'iChanId': 719,
            'iPageSize': 100,
            'iPage': 1,
            'sLangKey': 'zh-cn'
        }


class UpdateInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = Update.objects.latest('update_time')
        context['total'], context['update_time_diff'] = q.total, q.get_update_time_diff()
        return context


class SelectFieldsMixin(MultipleObjectMixin):
    model = Content
    ordering = '-start_time'
    select_fields = ['content_id', 'title', 'start_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.only(*self.select_fields)


class ContentSearchListView(SearchView, UpdateInfoMixin, SelectFieldsMixin):
    template_name = 'ys/search.html'
    paginate_by = 20

    def get_queryset(self):
        s = self.kwargs['search_keyword']
        queryset = super().get_queryset()
        return queryset.filter(Q(title__icontains=s))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = self.kwargs['search_keyword']
        context['form'] = SelectContentForm(initial={'title': s})
        return context


class ContentListView(ListView, SelectFieldsMixin):
    template_name = 'ys/all.html'
    paginate_by = 50


class SearchRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        search_keyword = self.request.GET.get('title', '')
        return reverse('search', args=[search_keyword])


class IndexView(TemplateView, UpdateInfoMixin):
    template_name = 'ys/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SelectContentForm()
        return context


class JsonUpdateView(View):

    @staticmethod
    def get(request):
        latest = Update.objects.latest('update_time')
        data = {
            'update_time': latest.update_time,
            'total': latest.total
        }
        return JsonResponse(data)

    @staticmethod
    @csrf_exempt
    def post(request):
        json_data = json.loads(request.body)
        token = 'temp'
        if json_data['token'] != token:
            return
        result = [UpdateContentForm.update_content(content) for content in json_data['content_list']]
        Update.objects.create(update_time=timezone.now(), total=json_data['total'])
        update_index.Command().handle(age=24)
        return JsonResponse(result, safe=False)
