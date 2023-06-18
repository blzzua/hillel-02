from django.urls import path
from favorites.views import AddToFavoritesView, RemoveFromFavoritesView, FavoritesListView, AddOrRemoveToFavoritesView, FavoritesAsJsonListView

urlpatterns = [
    path('add', AddToFavoritesView.as_view(), name='favorite_add'),
    path('del', RemoveFromFavoritesView.as_view(), name='favorite_del'),
    path('list', FavoritesListView.as_view(), name='favorite_list'),
    path('add_or_remove', AddOrRemoveToFavoritesView.as_view(), name='favorite_add_or_remove'),
    path('list_as_json', FavoritesAsJsonListView.as_view(), name='favorite_as_json'),
]
