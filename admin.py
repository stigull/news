#coding: utf-8
from django.contrib import admin
import django.forms as forms
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from news.models import Entry, EntryChange, Content, DEFAULT_LANGUAGE
from utils.stringformatting import slugify

LANGUAGES = dict(settings.LANGUAGES)

class ContentFormset(BaseInlineFormSet):
    def clean(self):
        languages = []
        for form in self.forms:
            if 'language' in form.cleaned_data:
                language = form.cleaned_data['language']
                if language in languages:
                    raise forms.ValidationError(_(u"Hver frétt má í mesta lagi hafa eitt meginmál á hverju tungumáli"))
                else:
                    languages.append(language)

        if DEFAULT_LANGUAGE not in languages:
            raise forms.ValidationError(_(u"Frétt verður að hafa eitt meginmál á tungumálinu: %s" % LANGUAGES[DEFAULT_LANGUAGE] ))

class ContentInline(admin.StackedInline):
    model = Content
    formset = ContentFormset
    extra = 2
    max_num = 3


def show_author(entry):
    author = entry.author
    try:
        profile = author.get_profile()
    except:
        return author.username
    else:
        return profile.get_short_fullname()
show_author.short_description = _(u"Höfundur")

def show_title(entry):
    return entry.default_title
show_title.short_description = _(u"Titill")

class EntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'publish_date'

    fieldsets = (
        (_(u"Almennt"), {
            'fields': ('publish_date', 'status','enable_comments')
        }),
        (_(u"Mikilvægi fréttarinnar"), {
            'fields': ('is_important', 'important_until',)
        }),
    )

    inlines = [ContentInline]

    list_display = (show_title,  'publish_date', show_author,  'enable_comments', 'is_important', 'status')
    search_fields = ('content__title', 'content__body', 'publish_date')

    def save_model(self, request, obj, form, change):
        if change:
            if obj.author != request.user:
                change = EntryChange(changed_by = request.user)
                change.save()
                obj.changes.add(change)
        else:
            obj.author = request.user
        obj.save()

admin.site.register(Content)
admin.site.register(Entry, EntryAdmin)