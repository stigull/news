#coding: utf-8
import django.forms as forms

from news.models import Entry

class EntryForm(forms.ModelForm):

    def clean(self):
        data = self.cleaned_data

        if 'is_important' in data and data['is_important']:
            if 'important_until' not in data or data['important_until'] is None:
                raise forms.ValidationError(u"Ef fréttin er merkt sem mikilvægari en aðrar þá þarf að tilgreina hvenær hún hættir að verða mikilvæg")

        return data


    class Meta:
        model = Entry