from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.generic import FormView, ListView
from django.http import HttpResponseNotAllowed, HttpResponse

from favorites.models import FavoriteItem
from favorites.forms import AddToFavoritesForm, RemoveFromFavoritesForm

User = get_user_model()


class AddToFavoritesView(FormView):
    model = FavoriteItem
    form_class = AddToFavoritesForm

    def post(self, request):
        form = AddToFavoritesForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data['item_id']
            user = request.user
            favorite_item, action = FavoriteItem.objects.get_or_create(user_id=user, item_id=item_id)
            if action:
                return HttpResponse('Item added', 200)
            else:
                return HttpResponse('Item already added', 200)
        else:
            return HttpResponse('Bad Request', status=400)

    def get(self, request):
        return HttpResponseNotAllowed('GET prohibited')


class RemoveFromFavoritesView(FormView):
    model = RemoveFromFavoritesForm

    def post(self, request):
        form = RemoveFromFavoritesForm(request.POST, session=request)
        if form.is_valid():
            item_id = form.cleaned_data['item_id']
            queryset = FavoriteItem.objects.filter(user_id=request.user, item_id=item_id).all()
            for fi in queryset:
                fi.delete()
        return redirect('favorite_list')


class FavoritesListView(ListView):
    model = FavoriteItem
    template_name = 'favorites/list.html'

    def get_queryset(self, request):
        queryset = super().get_queryset()
        queryset = queryset.filter(user_id=request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        return self.render_to_response(context)
