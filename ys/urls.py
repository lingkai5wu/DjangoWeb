from django.urls import path

import ys.views

urlpatterns = [
    path('', ys.views.select_content_list, name='select_content_list'),
    path('update/', ys.views.update_content_list, name='update_content_list'),
    path('all/', ys.views.show_all_content_list, name='show_all_content_list'),
]
