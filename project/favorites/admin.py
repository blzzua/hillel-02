from django.contrib import admin

# Register your models here.
from favorites.models import FavoriteItem


@admin.register(FavoriteItem)
class AdminFavoriteItem(admin.ModelAdmin):
    pass
