from django.contrib import admin

# Register your models here.
from .models import Item, Category, Discount
# admin.site.register(Item)

admin.site.register(Discount)


class ItemsInLine(admin.StackedInline):
    model = Item.categories.through
    extra = 1


@admin.register(Item)
class AdminItem(admin.ModelAdmin):

    inlines = [ItemsInLine]

    @admin.display(description='cats')
    def list_of_categories(self, categories):
        #  return self.caption
        return categories.get_categories_names()

    fieldsets = (
        (None, {
            'fields': ('id', 'sku', 'caption', 'price', 'is_active')
        }),
        ('Image & Description', {
            'classes': ('collapse',),
            'fields': ('description', 'image'),
        }),
    )
    list_display = ('id', 'is_active', 'sku', 'caption', 'img_preview')
    list_editable = ('caption', )


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name', 'img_preview']

    @admin.display(description='img_preview')
    def show_img(self, instance):
        return instance.img_preview()

    readonly_fields = ['img_preview']
