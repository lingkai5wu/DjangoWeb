import requests
from django import forms

from ys.models import Content


class UpdateContentForm(forms.Form):
    page_size = forms.IntegerField(label='pageSize', min_value=1)
    page_num = forms.IntegerField(label='pageNum', min_value=1)
    channel_id = forms.IntegerField(label='channelId')

    def get_content_list(self):
        page_size = self.cleaned_data['page_size']
        page_num = self.cleaned_data['page_num']
        channel_id = self.cleaned_data['channel_id']
        url = 'https://content-static.mihoyo.com/content/ysCn/getContentList'
        payload = {'pageSize': page_size, 'pageNum': page_num, 'channelId': channel_id}
        data = requests.get(url, params=payload).json()
        if data['retcode'] == 0:
            content_list = data['data']['list']
            total = data['data']['total']
            return content_list, total
        else:
            raise ValueError(data['message'])

    @staticmethod
    def update_content(content):
        obj, created = Content.objects.update_or_create(
            content_id=content['contentId'],
            defaults={'content_id': content['contentId'],
                      'title': content['title'],
                      'start_time': content['start_time'] + '+08:00'}
        )
        return f'{"添加" if created else "覆盖"}\t{obj.title}'


class SelectContentForm(forms.Form):
    title = forms.CharField()
