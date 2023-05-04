from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('sr/', include('sr.urls')),
    path('', include('ys.urls')),
]
