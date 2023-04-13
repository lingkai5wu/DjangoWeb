import requests
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.list import ListView

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


class ContentSearchListView(ListView, UpdateInfoMixin):
    model = Content
    template_name = 'search.html'
    paginate_by = 20

    def get_queryset(self):
        s = self.kwargs['search_keyword']
        queryset = super().get_queryset().order_by('-start_time').filter(title__icontains=s)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = self.kwargs['search_keyword']
        context['form'] = SelectContentForm(initial={'title': s})
        return context


class ContentListView(ListView, UpdateInfoMixin):
    model = Content
    template_name = 'all.html'
    ordering = '-start_time'
    paginate_by = 50


class SearchRedirectView(View):
    def get(self, request):
        search_keyword = request.GET.get('title', '')
        if search_keyword:
            redirect_url = reverse('search', args=[search_keyword])
            return HttpResponseRedirect(redirect_url)
        else:
            return HttpResponseBadRequest('搜索关键字不能为空！')


class IndexView(TemplateView, UpdateInfoMixin):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SelectContentForm()
        return context
