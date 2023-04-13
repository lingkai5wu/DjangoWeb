from django.urls import path

import ys.views

urlpatterns = [
    path('search/<str:search_keyword>/', ys.views.ContentSearchListView.as_view(), name='search'),
    path('search/', ys.views.SearchRedirectView.as_view(), name='search_redirect'),
    path('all/', ys.views.ContentListView.as_view(), name='all'),
    path('update/', ys.views.update_content_list, name='update'),
    path('', ys.views.IndexView.as_view(), name='index'),
]
