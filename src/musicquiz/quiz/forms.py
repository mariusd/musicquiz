from django import forms

class StrippedCharField(forms.CharField):
     r"""CharField that strips trailing and leading whitespace.
     
     >>> field = StrippedCharField()
     >>> field.clean('   value\t ')
     u'value'
     >>> field = StrippedCharField(min_length=5)
     >>> field.clean('    1234')
     Traceback (most recent call last):
     ...
     ValidationError: [u'Ensure this value has at least 5 characters (it has 4).']
     """
     def clean(self, value):
         if value is not None:
             value = value.strip()
         return forms.CharField.clean(self, value)

class WelcomeForm(forms.Form):
    name = StrippedCharField(label="Your name", min_length=2, max_length=20)
        
