"""
The central "URL dispatcher" that controls routing and flow of user interactions.
See https://docs.djangoproject.com/en/1.10/topics/http/urls/
"""

from django.conf.urls import url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^fingerprint/submit/$', views.FingerprintSubmit.as_view()),
    url(r'^admin/', admin.site.urls),
]

urlpatterns = format_suffix_patterns(urlpatterns)
