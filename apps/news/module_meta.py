from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from meta.utils import generate_meta_keywords

class NewsMeta():

    def get_title(self):
        return self.object.headline

    def get_description(self):
        if self.object.summary:
            return_value = self.object.summary
        elif self.object.body:
            return_value = self.object.body

        return_value = strip_tags(return_value)
        return_value = unescape_entities(return_value)
        return_value = return_value.replace("\n","")
        return_value = return_value.replace("\r","")

        return return_value

    def get_keywords(self):
        return generate_meta_keywords(self.object.body)

    def get_meta(self, object, name):

        self.object = object
        self.name = name
        
        if name == 'title':
            if object.meta: return object.meta.get_title()
            else: return self.get_title()
        elif name == 'description':
            if object.meta: return object.meta.get_description()
            else: return self.get_description()
        elif name =='keywords':
            if object.meta: return object.meta.get_keywords()
            else: return self.get_keywords()
        return ''    