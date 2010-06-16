from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class MakePayment(models.Model):
    guid = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(_('address line 2'), max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    referral_source = models.CharField(_('referred by'), max_length=200, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_count = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='cc', choices=(('check', 'Check'), 
                                                              ('cc', 'Make Online Payment'),))
    invoice_id = models.IntegerField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True,  related_name="make_payment_creator")
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, null=True, related_name="make_payment_owner")
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    