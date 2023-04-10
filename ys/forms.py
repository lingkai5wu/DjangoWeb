from django import forms


class UpdateContentForm(forms.Form):
    page_size = forms.IntegerField(label='pageSize', min_value=1)
    page_num = forms.IntegerField(label='pageNum', min_value=1)
    channel_id = forms.IntegerField(label='channelId')


class SelectContentForm(forms.Form):
    title = forms.CharField()
