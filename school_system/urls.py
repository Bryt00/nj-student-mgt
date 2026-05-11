from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('portal/', admin.site.urls),
    path('', include('students.urls')),
]
