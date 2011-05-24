from datetime import datetime
import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

from haystack.query import SearchQuerySet
from perms.utils import is_admin
from perms.managers import TendenciBaseManager


class EventManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query events.
        Returns a SearchQuerySet
        """
        sqs = super(EventManager, self).search(query=query, *args, **kwargs)
        event = kwargs.get('event', None)

        if not query:
            sqs = sqs.filter(start_dt__gt=datetime.now())
            sqs = sqs.order_by('start_dt')

        if event:
            sqs = sqs.filter(event=event)

        return sqs

    def search_filter(self, filters=None, *args, **kwargs):
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        groups = []
        if user and user.is_authenticated():
            groups = [g.pk for g in user.group_set.all()]
        admin = is_admin(user)

        # permission filters
        if user:
            if not admin:
                if not user.is_anonymous():
                    # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                    anon_query = Q(allow_anonymous_view=True)
                    user_query = Q(allow_user_view=True)
                    sec1_query = Q(status=1, status_detail='active')
                    user_perm_q = Q(users_can_view__in=user.pk)
                    group_perm_q = Q(groups_can_view__in=groups)

                    query = reduce(operator.or_, [anon_query, user_query])
                    query = reduce(operator.and_, [sec1_query, query])
                    query = reduce(operator.or_, [query, user_perm_q, group_perm_q])
                else:
                    sqs = sqs.filter(allow_anonymous_view=True)
        else:
            sqs = sqs.filter(allow_anonymous_view=True)

        # custom filters
        for filter in filters:
            sqs = sqs.filter(content='"%s"' % filter)

        return sqs.models(self.model)


class EventTypeManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query events.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        return sqs.models(self.model)


class RegistrantManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query events.
        Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        event = kwargs.get('event')

        if event:
            sqs = sqs.filter(event_pk=event.pk)

        # let the parent search know that we have started a SQS
        kwargs.update({'sqs': sqs})

        sqs = super(RegistrantManager, self).search(
            query=query, *args, **kwargs)

        return sqs
