import requests
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.base import ContextMixin, TemplateView, RedirectView
from django.views.generic.list import ListView, MultipleObjectMixin

from ys.forms import UpdateContentForm, SelectContentForm
from ys.models import Content, Update


def get_content_list(page_size, page_num, channel_id):
    url = 'https://content-static.mihoyo.com/content/ysCn/getContentList'
    payload = {'pageSize': page_size, 'pageNum': page_num, 'channelId': channel_id}
    data = requests.get(url, params=payload).json()
    if data['retcode'] == 0:
        content_list = data['data']['list']
        total = data['data']['total']
        return content_list, total
    else:
        raise ValueError(data['message'])


def update_content(content):
    obj, created = Content.objects.update_or_create(
        content_id=content['contentId'],
        defaults={'content_id': content['contentId'],
                  'title': content['title'],
                  'start_time': content['start_time']}
    )
    return f'添加\t{obj.title}' if created else f'覆盖\t{obj.title}'


class UpdateContentView(FormView):
    template_name = 'update.html'
    form_class = UpdateContentForm
    success_url = '/update/'

    def form_valid(self, form):
        page_size = form.cleaned_data['page_size']
        page_num = form.cleaned_data['page_num']
        channel_id = form.cleaned_data['channel_id']
        try:
            content_list, total = get_content_list(page_size, page_num, channel_id)
        except ValueError as e:
            return HttpResponse(str(e))
        context = self.get_context_data()
        context['total'] = total
        context['list'] = [update_content(content) for content in content_list]
        Update.objects.create(update_time=timezone.now(), total=total)
        return self.render_to_response(context)

    def get_initial(self):
        return {'page_num': 1, 'channel_id': 10}


class UpdateInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = Update.objects.latest('update_time')
        context['total'], context['update_time'] = q.total, q.update_time
        return context


class SelectFieldsMixin(MultipleObjectMixin):
    model = Content
    ordering = '-start_time'
    select_fields = ['content_id', 'title', 'start_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.only(*self.select_fields)


class ContentSearchListView(ListView, UpdateInfoMixin, SelectFieldsMixin):
    template_name = 'search.html'
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


class ContentListView(ListView, UpdateInfoMixin, SelectFieldsMixin):
    template_name = 'all.html'
    paginate_by = 50


class SearchRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        search_keyword = self.request.GET.get('title', '')
        return reverse('search', args=[search_keyword])


class IndexView(TemplateView, UpdateInfoMixin):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SelectContentForm()
        return context
