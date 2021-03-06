from django import forms
from django.utils.safestring import mark_safe

from widgets import TypeExpMethodWidget, NoticeTimeTypeWidget
from site_settings.utils import get_setting

        

class TypeExpMethodField(forms.MultiValueField):
    def __init__(self, required=True, widget=TypeExpMethodWidget(attrs=None, fields_pos_d=None),
                label=None, initial=None, help_text=None):
        myfields = ()
        super(TypeExpMethodField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)
        
    def clean(self, value):
        return self.compress(value) 
        
    def compress(self, data_list):
        for i in range(0, len(data_list)):
            if type(data_list[i]) is bool:
                if data_list[i] == False:
                    data_list[i] = ''
                else:
                    data_list[i] = '1'
            if data_list[i] == None:
                data_list[i] = ''
        
        if data_list:
            return ','.join(data_list)
        return None
    
class NoticeTimeTypeField(forms.MultiValueField):
    def __init__(self, required=True, widget=NoticeTimeTypeWidget(attrs=None),
                label=None, initial=None, help_text=None):
        myfields = ()
        super(NoticeTimeTypeField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)
        
    def clean(self, value):
        return self.compress(value) 
        
    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None
  
    
class PriceInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        if currency_symbol == '': currency_symbol = "$"
        return mark_safe('$ %s' % super(PriceInput, self).render(name, value, attrs))
        
