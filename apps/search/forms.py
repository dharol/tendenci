from django import forms
from django.db import models
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import haystack
from haystack.query import SearchQuerySet

INCLUDED_APPS = getattr(settings,'HAYSTACK_INCLUDED_APPS',[])

def model_choices(site=None):
    if site is None:
        site = haystack.sites.site
        
    choices = []
    for m in site.get_indexed_models():
        if m._meta.module_name in INCLUDED_APPS:
            choices.append(("%s.%s" % (m._meta.app_label, m._meta.module_name), 
                            capfirst(unicode(m._meta.verbose_name_plural))))
            
    return sorted(choices, key=lambda x: x[1])


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'), max_length=255)
    
    def __init__(self, *args, **kwargs):
        self.searchqueryset = kwargs.get('searchqueryset', None)
        self.load_all = kwargs.get('load_all', False)
        self.user = kwargs.get('user', None)
        
        if self.searchqueryset is None:
            self.searchqueryset = SearchQuerySet()
        
        try:
            del(kwargs['searchqueryset'])
        except KeyError:
            pass
        
        try:
            del(kwargs['load_all'])
        except KeyError:
            pass

        try:
            del(kwargs['user'])
        except KeyError:
            pass
                
        super(SearchForm, self).__init__(*args, **kwargs)
    
    def search(self):
        self.clean()

        # check permissions and then query
        if self.user:
            if not self.user.is_authenticated():
                sqs = self.searchqueryset.filter(content=self.cleaned_data['q'])
                sqs = sqs.filter(allow_anonymous_view=True)
            else:
                if self.user.is_superuser:
                    sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
                else:
                    sqs = self.searchqueryset.filter(content=self.cleaned_data['q'])
                    sqs = sqs.filter(allow_user_view=True)
                    sqs = sqs.filter_or(creator_username=self.user.username)            
        else:
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
        
        if self.load_all:
            sqs = sqs.load_all()
        
        return sqs


class HighlightedSearchForm(SearchForm):
    def search(self):
        return super(HighlightedSearchForm, self).search().highlight()


class FacetedSearchForm(SearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def search(self):
        sqs = super(FacetedSearchForm, self).search()
        
        if self.cleaned_data['selected_facets']:
            sqs = sqs.narrow(self.cleaned_data['selected_facets'])
        
        return sqs


class ModelSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(ModelSearchForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('Search In'), widget=forms.CheckboxSelectMultiple)

    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = []
        site = haystack.sites.site
        indexed_models = site.get_indexed_models()

        if indexed_models:
            search_models = []
            for model in indexed_models:
                if model._meta.module_name in INCLUDED_APPS:
                    search_models.append(model)
#
        if self.cleaned_data['models']:
            search_models = []
            for model in self.cleaned_data['models']:
                class_model = models.get_model(*model.split('.'))
                if class_model._meta.module_name in INCLUDED_APPS:
                    search_models.append(class_model)

        return search_models
    
    def search(self):
        sqs = super(ModelSearchForm, self).search()
        return sqs.models(*self.get_models())


class HighlightedModelSearchForm(ModelSearchForm):
    def search(self):
        return super(HighlightedModelSearchForm, self).search().highlight()


class FacetedModelSearchForm(ModelSearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def search(self):
        sqs = super(FacetedModelSearchForm, self).search()
        
        if self.cleaned_data['selected_facets']:
            sqs = sqs.narrow(self.cleaned_data['selected_facets'])
        
        return sqs.models(*self.get_models())