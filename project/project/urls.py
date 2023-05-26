"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
# TODO: move MainPage from items.views to main.views
from items.views import MainPage, ImportItemsListView, ExportItemsListView
from main.views import ContactView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', ItemsListView.as_view(), name='items_list'),
    path('', MainPage.as_view(), name='main_page'),
    path('contacts/', ContactView.as_view(), name='main_contacts'),
    path('items/', include('items.urls')),
    path('order/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('feedback/', include('feedback.urls')),
    path('favorites/', include('favorites.urls')),
    path('import/items', ImportItemsListView.as_view(), name='import_items_csv'),
    path('export/items.csv', ExportItemsListView.as_view(), name='export_items_csv'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
