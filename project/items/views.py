# from django.http import HttpResponse
import csv

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from items.forms import ItemCreateForm, ImportItemsCSVForm
from items.models import Item
from django.contrib import messages
from django.views.generic import ListView, View
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


class ItemsListView(ListView):
    model = Item
    template_name = 'items/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


class ItemCreateView(View):
    def get(self, request):
        form = ItemCreateForm()
        context = {'form': form}
        return render(request, 'items/item_create.html', context)

    def post(self, request):
        form = ItemCreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item has been created successfully')
            return redirect('items_list')
        else:
            messages.error(request, 'Error creating item')
            context = {'form': form}
            return render(request, 'items/item_create.html', context=context)


class MainPage(ItemsListView):
    paginate_by = 8
    paginator = Paginator
    template_name = 'products_index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class ImportItemsListView(View):
    def get(self, request, *args, **kwargs):
        form = ImportItemsCSVForm()
        saved_items = []
        return render(request, 'items/import_csv.html', {'form': form, 'saved_items': saved_items})

    @method_decorator(staff_member_required(login_url=reverse_lazy('accounts_login')))
    def post(self, request, *args):
        form = ImportItemsCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            dict_reader = csv.DictReader(decoded_file)
            on_duplicate = form.cleaned_data['on_duplicate']
            upload_items = []
            for row in dict_reader:
                try:
                    if Item.objects.filter(caption=row['caption']).exists():
                        if on_duplicate == 'update':
                            # item = Item.objects.filter(caption=row['caption']).first()
                            item_qs = Item.objects.filter(caption=row['caption'])
                            item_qs.update(
                                caption=row['caption'], sku=row['sku'], price=row['price'],
                                is_active=row['is_active'], description=row['description']
                            )
                            item = Item.objects.filter(caption=row['caption']).first()
                            item.upload_result = 'upload'
                            upload_items.append(item)
                        elif on_duplicate == 'ignore':
                            item = Item.objects.filter(caption=row['caption']).first()
                            item.upload_result = 'ignore'
                            upload_items.append(item)
                    else:
                        item = Item.objects.create(caption=row['caption'], sku=row['sku'], price=row['price'],
                                                   is_active=row['is_active'], description=row['description'])
                        item.upload_result = 'upload'
                        upload_items.append(item)
                except ValidationError:
                    item = dict(row)
                    item['upload_result'] = 'error'
                    upload_items.append(item)

            return render(request, 'items/import_csv.html', context={'form': form, 'upload_items': upload_items, }, )

        else:  # not form.is_valid():
            return render(request, 'items/import_csv.html', context={'form': form})


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class ExportItemsListView(View):
    def get(self, request, *args, **kwargs):
        headers = {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="items.csv"'
        }
        response = HttpResponse(headers=headers)
        fields_name = ['caption', 'image', 'sku', 'price', 'is_active', 'description']
        writer = csv.DictWriter(response, fieldnames=fields_name)
        writer.writeheader()
        for item in Item.objects.iterator():
            writer.writerow(
                {
                    'caption': item.caption,
                    'image': item.image.name if item.image else 'no image',
                    'sku': item.sku,
                    'price': item.price,
                    'is_active': item.is_active,
                    'description': item.description,
                }
            )
        return response
