from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

import ys.views

urlpatterns = [
    path('search/<str:search_keyword>/', ys.views.ContentSearchListView.as_view(), name='search'),
    path('search/', ys.views.SearchRedirectView.as_view(), name='search_redirect'),
    path('haystack_search/', include('haystack.urls'), name='haystack_search'),
    path('all/', ys.views.ContentListView.as_view(), name='all'),
    path('form_update/', ys.views.FormUpdateView.as_view(), name='form_update'),
    path('json_update/', csrf_exempt(ys.views.JsonUpdateView.as_view()), name='json_update'),
    path('', ys.views.IndexView.as_view(), name='index'),
]
