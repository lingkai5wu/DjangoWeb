import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from ys.forms import UpdateContentForm, SelectContentForm
from ys.models import Content, Update


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
                                  'start_time': content['start_time'],
                                  'create_time': timezone.now()}
                    )
                    if created:
                        context['list'].append(f'填加\t{obj.title}')
                    else:
                        context['list'].append(f'覆盖\t{obj.title}')
                Update.objects.create(
                    last_time=timezone.now(),
                    last_total=context['total']
                )
            else:
                return HttpResponse(data['message'])
    else:
        context['form'] = UpdateContentForm(initial={'channel_id': 10})
    return render(request, 'update.html', context)


def select_content_list(request):
    context = {}
    if request.method == 'POST':
        form = SelectContentForm(request.POST)
        context['form'] = form
        if form.is_valid():
            context['list'] = Content.objects.filter(title__contains=form.cleaned_data['title'])
            context['total'] = Update.objects.latest('last_time').last_total
    else:
        context['form'] = SelectContentForm()
    return render(request, 'index.html', context)
