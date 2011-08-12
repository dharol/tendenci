from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel
from invoices.models import Invoice
from discounts.managers import DiscountManager

class Discount(TendenciBaseModel):
    class Meta:
        permissions = (("view_discount","Can view discount"),)
        
    discount_code = models.CharField(max_length=100, unique=True, help_text=_('Discount codes must be unique.'))
    start_dt = models.DateTimeField(_('Start Date/Time'))
    end_dt = models.DateTimeField(_('Start Date/Time'))
    never_expires = models.BooleanField(_('Never Expires'), help_text=_('Check this box to make the discount code never expire.'))
    value = models.DecimalField(_('Discount Value'), max_digits=10, decimal_places=2, help_text=_('Enter discount value as a positive number.'))
    cap = models.IntegerField(_('Maximum Uses'), help_text=_('Enter 0 for unlimited discount code uses.'))
    
    objects = DiscountManager()
    
    def num_of_uses(self):
        return self.discountuse_set.count()
    
    def available(self):
        """
        Determines if this discount has is still usable based on its
        cap.
        """
        if self.num_of_uses() >= cap:
            return False
        return True
    
    def __unicode__(self):
        return self.discount_code
        
    @models.permalink
    def get_absolute_url(self):
        return('discount.detail', [self.pk])
    
class DiscountUse(models.Model):
    invoice = models.ForeignKey(Invoice)
    discount = models.ForeignKey(Discount)
    create_dt = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s:%s" % (self.invoice, self.discount)
