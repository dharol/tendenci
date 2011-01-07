from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from memberships.forms import MembershipTypeForm
from user_groups.models import Group
from event_logs.models import EventLog
from perms.models import ObjectPermission 
from memberships.models import  MembershipType, App, AppField
from memberships.forms import AppForm, AppFieldForm, AppEntryForm
from memberships.utils import get_default_membership_fields


class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'allow_renewal', 'renewal_price', 'renewal',  
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price', 'status_detail']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description')}),
        ('Expiration Method', {'fields': ('never_expires', 'type_exp_method',)}),
        ('Renewal Options', {'fields': (('allow_renewal','renewal'), 'renewal_price', 
                                        'renewal_period_start', 
                                        'renewal_period_end',)}),

        ('Other Options', {'fields': (
            'expiration_grace_period', ('require_approval', 
            'admin_only'), 'order', 'status', 'status_detail')}),
    )

    form = MembershipTypeForm
    
    class Media:
        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
              "%sjs/membtype.js" % settings.STATIC_URL,)
        
    def log_deletion(self, request, object, object_repr):
        super(MembershipTypeAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 475300,
            'event_data': '%s %s(%d) deleted by %s' % (object._meta.object_name, 
                                                    object.name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(MembershipTypeAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 475200,
            'event_data': '%s %s(%d) edited by %s' % (object._meta.object_name, 
                                                    object.name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(MembershipTypeAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 475100,
            'event_data': '%s %s(%d) added by %s' % (object._meta.object_name, 
                                                   object.name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
        
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        # save the expiration method fields
        type_exp_method = form.cleaned_data['type_exp_method']
        type_exp_method_list = type_exp_method.split(",")
        for i, field in enumerate(form.type_exp_method_fields):
            if field=='fixed_expiration_rollover':
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = ''
            else:
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = "0"

            exec('instance.%s="%s"' % (field, type_exp_method_list[i]))
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            
            # create a group for this type
            group = Group()
            group.name = 'Membership: %s' % instance.name
            group.slug = slugify(group.name)
            # just in case, check if this slug already exists in group. 
            # if it does, make a unique slug
            tmp_groups = Group.objects.filter(slug__istartswith=group.slug)
            if tmp_groups:
                t_list = [g.slug[len(group.slug):] for g in tmp_groups]
                num = 1
                while str(num) in t_list:
                    num += 1
                group.slug = '%s%s' % (group.slug, str(num))
                # group name is also a unique field
                group.name = '%s%s' % (group.name, str(num))
            
            group.label = instance.name
            group.type = 'membership'
            group.email_recipient = request.user.email
            group.show_as_option = 0
            group.allow_self_add = 0
            group.allow_self_remove = 0
            group.description = "Auto-generated with the membership type. Used for membership only"
            group.notes = "Auto-generated with the membership type. Used for membership only"
            #group.use_for_membership = 1
            group.creator = request.user
            group.creator_username = request.user.username
            group.owner = request.user
            group.owner_username = request.user.username

            group.save()
            
            instance.group = group
 
        # save the object
        instance.save()
        
        #form.save_m2m()
        
        return instance

class AppFieldAdmin(admin.StackedInline):
    fieldsets = (
        (None, {'fields': (
            ('label','field_type',),
            ('required', 'unique', 'admin_only',),
            'choices',
            'help_text',
            'default_value',
            'css_class',
            'position'
        )},),
    )
    model = AppField
    form = AppFieldForm
    extra = 0
    template = "memberships/admin/stacked.html"

class AppAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name','slug', 'description', 'confirmation_text', 'notes', 'membership_types', 'use_captcha')},),
        ('Administrative', {'fields': ('allow_anonymous_view','user_perms','group_perms','status','status_detail')}),
    )

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/dynamic-inlines-with-sort.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    inlines = (AppFieldAdmin,)
    prepopulated_fields = {'slug': ('name',)}
    form = AppForm
    add_form_template = "memberships/admin/add_form.html"

    def log_deletion(self, request, object, object_repr):
        super(AppAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 653000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(AppAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 652000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(AppAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 651000,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)


    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances = [] # clear inline instances
        return super(AppAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context={}):

#        self.inline_instances = []
#        inline_instance = AppFieldAdmin(self.model, self.admin_site)
#        self.inline_instances.append(inline_instance)

#        self.inlines = [FieldInline]
#        self.inline_instances = []
#        for inline_class in self.inlines:
#            inline_instance = inline_class(self.model, self.admin_site)
#            self.inline_instances.append(inline_instance)

        extra_context.update({
            'excluded_fields':['field_type', 'no_duplicates', 'admin_only'],
            'excluded_lines':[2, 3],
            'fields_to_check':['membership-type','payment-method']
        });

        return super(AppAdmin, self).change_view(request, object_id, extra_context)

#        self.inlines = [FieldInline]
#        self.inline_instances = []
#        for inline_class in self.inlines:
#            inline_instance = inline_class(self.model, self.admin_site)
#            self.inline_instances.append(inline_instance)
#        # exclude fields for corporate_membership_type and payment_method
#        excluded_lines = [2, 3]  # exclude lines in inline field_set - 'choices', 'field_layout', 'size'
#        excluded_fields = ['field_type', 'no_duplicates', 'admin_only']
#        fields_to_check = ['corporate_membership_type', 'payment_method']
#
#        if extra_context:
#            extra_context.update({
#                                  'excluded_lines': excluded_lines,
#                                  "excluded_fields":excluded_fields,
#                                  'fields_to_check': fields_to_check
#                                  })
#        else:
#            extra_context = {'excluded_lines': excluded_lines,
#                             "excluded_fields":excluded_fields,
#                             'fields_to_check': fields_to_check}
#
#        return super(CorpAppAdmin, self).change_view(request, object_id, extra_context)

    def get_fieldsets(self, request, instance=None):

        field_list = [
            
                    (None, {
                        'fields': ('name','slug', 'description', 'confirmation_text', 'notes', 'membership_types', 'use_captcha'),
                    }),

                    ('Administrative', {
                        'fields': ('allow_anonymous_view','user_perms','group_perms','status','status_detail'),
                    }),

                    ('Form Fields', {
                        'fields': [],
                        'description': 'You will have the chance to add or manage the form fields after saving.'
                    }),
        ]

        if instance: # editing
            field_list.pop() # removes default message (last item)

        return field_list

    def save_model(self, request, object, form, change):
        app = form.save(commit=False)
        add = not change

        # set up user permission
        app.allow_user_view, app.allow_user_edit = form.cleaned_data['user_perms']

        # set creator and owner
        if add:
            app.creator = request.user
            app.creator_username = request.user.username
            app.owner = request.user
            app.owner_username = request.user.username

        app.save()

        if add:
            # set some default fields to the app
            field_kwargs = get_default_membership_fields()
            for field_kwarg in field_kwargs:
                field_kwarg.update({'app':app})
                app_field = AppField(**field_kwarg)
                app_field.save()

        form.save_m2m()

        # TODO: Fix relational queryset (e.g. app.fields.visible()); Pull latest records

        for field in app.fields.visible():
            if 'membership-type' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(MembershipType)
                choices = [item.name for item in app.membership_types.all()]
                field.choices = ", ".join(choices)
            elif 'first-name' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)
            elif 'last-name' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)
            elif 'email-field' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)

            field.save()

        # permissions
        if add:
            # assign permissions for selected groups
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], app)
            # assign creator permissions
            ObjectPermission.objects.assign(app.creator, app)
        else:
            # assign permissions
            ObjectPermission.objects.remove_all(app)
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], app)
            ObjectPermission.objects.assign(app.creator, app)

        return app

class AppEntryAdmin(admin.ModelAdmin):
    form = AppEntryForm

admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(App, AppAdmin)










