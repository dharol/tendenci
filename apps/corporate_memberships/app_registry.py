from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import CorporateMembership


class CorporateMembershipRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Corporate membership management application.'

    url = {
        'search': lazy_reverse('corp_memb.search'),
    }

site.register(CorporateMembership, CorporateMembershipRegistry)