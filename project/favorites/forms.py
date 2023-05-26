from django import forms
from favorites.models import FavoriteItem


class AddToFavoritesForm(forms.ModelForm):

    class Meta:
        model = FavoriteItem
        fields = ('item_id',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        self.user = user


class RemoveFromFavoritesForm(forms.ModelForm):
    class Meta:
        model = FavoriteItem
        fields = ('item_id',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        self.user = user
