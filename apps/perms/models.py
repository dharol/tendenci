from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from usergroups.models import Group


from perms.managers import ObjectPermissionManager

class ObjectPermission(models.Model):
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = ObjectPermissionManager()

# Abstract base class for authority fields
class AuditingBaseModel(models.Model):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'),)
    
    # authority fields
    allow_anonymous_view = models.BooleanField()
    allow_user_view = models.BooleanField()
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_user_edit = models.BooleanField()
    allow_member_edit = models.BooleanField()
    
    creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="%(class)s_owner", editable=False)    
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=STATUS_CHOICES,
                                     default='active')
    
    
    class Meta:
        abstract = True 