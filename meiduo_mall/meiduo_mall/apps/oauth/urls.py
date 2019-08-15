from django.conf.urls import url
from .views import QQAuthURLView

urlpatterns = [
    url(r'^oauth/qq/authorization/$', QQAuthURLView.as_view())
]