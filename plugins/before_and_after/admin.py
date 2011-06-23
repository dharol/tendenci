from django.contrib import admin
from django.conf import settings

from before_and_after.models import BeforeAndAfter, Category, \
    Subcategory, PhotoSet
from before_and_after.forms import BnAForm

class PhotoSetAdmin(admin.StackedInline):
    model = PhotoSet
    extra = 1
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "warning"]
    list_filter = ["category", "warning"]

class BnAAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "subcategory"]
    list_filter = ["category", "subcategory"]
    form = BnAForm
    inlines = [PhotoSetAdmin,]
    
    fieldsets = (
        (None, {'fields': (
            'title',
            'category',
            'subcategory',
            'description',
            'tags',
        )}),
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'status',
            'status_detail',
            'group_perms',
            'user_perms',
            'admin_notes',
        )}),
    )
            
    class Media:
        js = (
            '%sjs/admin/sortable_inline/jquery-1.5.1.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/jquery-ui-1.8.13.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/stacked-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(BnAAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
    
admin.site.register(BeforeAndAfter, BnAAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)