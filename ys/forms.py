from django import forms


class UpdateContentForm(forms.Form):
    page_size = forms.IntegerField(label='pageSize', min_value=1)
    page_num = forms.IntegerField(label='pageNum', min_value=1)
    channel_id = forms.IntegerField(label='channelId')
    address = forms.GenericIPAddressField()
    port = forms.IntegerField(min_value=0, max_value=65535)


class SelectContentForm(forms.Form):
    title = forms.CharField()
