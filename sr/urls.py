from django.urls import path

import sr.views


urlpatterns = [
    path('', sr.views.IndexView.as_view(), name='index'),
]
