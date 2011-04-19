from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.notices.views",
    url(r"^logs/search/$", "membership_notice_log_search", name="membership.notice.log.search"),
    url(r"^logs/(?P<id>\d+)/$", "membership_notice_log_view", name="membership.notice.log.view"),
)