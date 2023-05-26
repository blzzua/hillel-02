from django.urls import path
from favorites.views import AddToFavoritesView, RemoveFromFavoritesView, FavoritesListView

urlpatterns = [
    path('add', AddToFavoritesView.as_view(), name='favorite_add'),
    path('del', RemoveFromFavoritesView.as_view(), name='favorite_del'),
    path('list', FavoritesListView.as_view(), name='favorite_list'),
]
