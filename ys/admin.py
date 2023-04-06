from django.contrib import admin

from ys.models import Content


class ContentAdmin(admin.ModelAdmin):
    fields = ['title', 'banner', 'start_time', 'content_text']
    list_display = ('title', 'start_time')
    list_filter = ['start_time']


admin.site.register(Content, ContentAdmin)
