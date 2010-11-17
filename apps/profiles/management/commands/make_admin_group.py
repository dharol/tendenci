from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group as Auth_Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    # create an admin auth group, and assign all permissions 
    # (except 4 auth permission the auth_user, auth_groups..) to this group
    # command to run: python manage.py make_admin_group
    def handle(self, *args, **options):
        out = ''
        name = 'Admin'
        try:
            auth_group = Auth_Group.objects.get(name=name)
        except Auth_Group.DoesNotExist:
            auth_group = Auth_Group(name=name)
            auth_group.save()
            #self.stdout.write('Successfully created an auth group "Admin".')
            out = 'Successfully created an auth group "Admin".\n'
        
        # assign permission to group, but exclude the auth content
        content_to_exclude = ContentType.objects.filter(app_label='auth')    
        permissions = Permission.objects.all().exclude(content_type__in=content_to_exclude)
        auth_group.permissions = permissions
        auth_group.save()
        
        #self.stdout.write('Successfully added all permissions to group "Admin".')
        out += 'Successfully added all permissions to group "Admin".'
        print out
