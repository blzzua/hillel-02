from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.items.views import ItemListAPIView, ItemAPIView
# from authentication.views import UserAPIView, UserDetailsAPIView

app_name = 'api_v1'


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='api_v1:api-schema'),
        name='api-docs'
    ),

    path('items/', ItemListAPIView.as_view()),
    path('item/<uuid:pk>', ItemAPIView.as_view()),

]
