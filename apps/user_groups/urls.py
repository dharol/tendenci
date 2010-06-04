from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('user_groups.views',
    url(r'^$',                              'group_search',     name='groups'),
    url(r'^add/$',                          'group_add_edit', name='group.add_edit'),
    url(r'^search/$',                       'group_search',   name='group.search'),
    url(r'^edit_perms/(?P<id>\d+)/$',       'group_edit_perms', name="group.edit_perms"),
    url(r'^(?P<group_slug>[-.\w]+)/$',      'group_detail',   name='group.detail'),
    url(r'^(?P<group_slug>[-.\w]+)/edit/$', 'group_add_edit', name='group.edit'),
    url(r'^(?P<group_slug>[-.\w]+)/adduser/$', 'groupmembership_add_edit', name='group.adduser'),
    url(r'^(?P<group_slug>[-.\w]+)/edituser/(?P<user_id>\d+)/$', 'groupmembership_add_edit', name='group.edituser'),
    url(r'^(?P<group_slug>[-.\w]+)/deleteuser/(?P<user_id>\d+)/$', 'groupmembership_delete', name='group.deleteuser'),
)