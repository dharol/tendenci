from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Membership


class MembershipRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Membership management application.'

    url = {
        'search': lazy_reverse('membership.search'),
    }

site.register(Membership, MembershipRegistry)
