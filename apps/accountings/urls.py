from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('accountings.views',                  
    url(r'^account_numbers/$', 'account_numbers', name="accounting.account_numbers"),
)