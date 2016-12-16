from django import forms


class NameForm(forms.Form):
    entity = forms.CharField(label='entity', max_length=100)