from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include

from . import views


router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='area')  # base_name为路由名称前缀

urlpatterns = [
    # url(r'areas', include(router.urls)),
]

urlpatterns += router.urls

