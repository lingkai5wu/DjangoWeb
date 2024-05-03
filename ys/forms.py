import requests
from django import forms

from ys.models import Content


class UpdateContentForm(forms.Form):
    iAppId = forms.IntegerField(label='iAppId')
    iChanId = forms.IntegerField(label='iChanId')
    iPageSize = forms.IntegerField(label='iPageSize', max_value=100)
    iPage = forms.IntegerField(label='iPage')
    sLangKey = forms.CharField(label='sLangKey')

    def get_content_list(self):
        url = 'https://api-takumi-static.mihoyo.com/content_v2_user/app/16471662a82d418a/getContentList'
        data = requests.get(url, params=self.cleaned_data).json()
        if data['retcode'] == 0:
            content_list = data['data']['list']
            total = data['data']['iTotal']
            return content_list, total
        else:
            raise ValueError(data['message'])

    @staticmethod
    def update_content(content):
        obj, created = Content.objects.update_or_create(
            content_id=content['iInfoId'],
            defaults={'content_id': content['iInfoId'],
                      'title': content['sTitle'],
                      'start_time': content['dtStartTime'] + '+08:00'}
        )
        return f'{"添加" if created else "覆盖"}\t{obj.title}'


class SelectContentForm(forms.Form):
    title = forms.CharField()
