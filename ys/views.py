import requests
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import ContextMixin, TemplateView, RedirectView
from django.views.generic.list import ListView, MultipleObjectMixin

from ys.forms import UpdateContentForm, SelectContentForm
from ys.models import Content, Update


# 这段改日重写
def update_content_list(request):
    context = {}
    if request.method == 'POST':
        form = UpdateContentForm(request.POST)
        context['form'] = form
        if form.is_valid():
            url = 'https://content-static.mihoyo.com/content/ysCn/getContentList'
            payload = {'pageSize': form.cleaned_data['page_size'],
                       'pageNum': form.cleaned_data['page_num'],
                       'channelId': form.cleaned_data['channel_id']}
            data = requests.get(url, params=payload).json()
            if data['retcode'] == 0:
                content_list = data['data']['list']
                context['total'] = data['data']['total']
                context['list'] = []
                for content in content_list:
                    obj, created = Content.objects.update_or_create(
                        content_id=content['contentId'],
                        defaults={'content_id': content['contentId'],
                                  'title': content['title'],
                                  'start_time': content['start_time']}
                    )
                    if created:
                        context['list'].append(f'添加\t{obj.title}')
                    else:
                        context['list'].append(f'覆盖\t{obj.title}')
                Update.objects.create(
                    update_time=timezone.now(),
                    total=context['total']
                )
            else:
                return HttpResponse(data['message'])
    else:
        initial = {'page_num': 1, 'channel_id': 10}
        context['form'] = UpdateContentForm(initial=initial)
    return render(request, 'update.html', context)


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
