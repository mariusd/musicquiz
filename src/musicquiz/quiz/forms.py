from django import forms

class StrippedCharField(forms.CharField):
     """CharField that strips trailing and leading whitespace."""
     
     def clean(self, value):
         if value is not None:
             value = value.strip()
         return forms.CharField.clean(self, value)
