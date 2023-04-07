import requests
from django.core.exceptions import ObjectDoesNotExist
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
            proxy = f"{form.cleaned_data['address']}:{form.cleaned_data['port']}"
            proxies = {
                'http': proxy,
                'https': proxy
            }
            data = requests.get(url, params=payload, proxies=proxies).json()
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
                    total=context['total'],
                    address=form.cleaned_data['address'],
                    port=form.cleaned_data['port']
                )
            else:
                return HttpResponse(data['message'])
    else:
        initial = {'page_num': 1, 'channel_id': 10}
        try:
            q = Update.objects.latest('update_time')
            initial['address'] = q.address
            initial['port'] = q.port
        except ObjectDoesNotExist:
            print('需要初始化')
        context['form'] = UpdateContentForm(initial=initial)
    return render(request, 'update.html', context)


def select_content_list(request):
    context = {}
    if request.method == 'POST':
        form = SelectContentForm(request.POST)
        context['form'] = form
        if form.is_valid():
            context['list'] = Content.objects.filter(title__contains=form.cleaned_data['title'])[::-1]
    else:
        context['form'] = SelectContentForm()
    context['total'], context['update_time'] = get_latest_update_info()
    return render(request, 'index.html', context)


def show_all_content_list(request):
    context = {}
    context['total'], context['update_time'] = get_latest_update_info()
    context['list'] = Content.objects.all()[::-1]
    return render(request, 'all.html', context)


def get_latest_update_info():
    try:
        q = Update.objects.latest('update_time')
        return q.total, q.update_time
    except ObjectDoesNotExist:
        print('需要初始化')
