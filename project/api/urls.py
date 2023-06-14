from django.urls import path, re_path
from api.items.views import ItemListAPIView, ItemAPIView
from project.urls import schema_view

app_name = 'api_v1'

urlpatterns = [
    #  swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #  items
    path('items/', ItemListAPIView.as_view()),
    path('item/<uuid:pk>', ItemAPIView.as_view()),
]
