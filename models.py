#! /usr/bin/env python
# -*- coding: utf8 -*-

import datetime
import operator

from markdown import markdown

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import truncatewords_html

from utils.stringformatting import slugify

DEFAULT_LANGUAGE = getattr(settings, 'LANGUAGE_CODE', 'is')
LANGUAGES = list(settings.LANGUAGES)
LANGUAGES.sort(key = operator.itemgetter(1))

class LiveEntriesManager(models.Manager):
    def get_query_set(self):
        return super(LiveEntriesManager, self).get_query_set().filter(status = Entry.LIVE_STATUS)

class ImportantEntriesManager(LiveEntriesManager):
    def get_query_set(self):
        return super(ImportantEntriesManager, self).get_query_set().filter(is_important = True).filter(important_until__gte = datetime.datetime.now())

class EntryChange(models.Model):
    changed_when = models.DateTimeField(_(u"Breytingardagur og tími"), default=datetime.datetime.now)
    changed_by = models.ForeignKey(User, editable = False, verbose_name = _(u"Breytt af"))

class Entry(models.Model):
    LIVE_STATUS = 1
    HIDDEN_STATUS = 3
    STATUS_CHOICES = (
        (LIVE_STATUS, _(u"Til birtingar")),
        (HIDDEN_STATUS, _(u"Ekki til birtingar")),
    )

    publish_date = models.DateTimeField(_(u"Birtingardagur og tími"),
                                        default = datetime.datetime.now,
                                        help_text = _(u"Fréttin mun fyrst birtast þennan dag á þessum ákveðna tíma ef hún er á annað borð merkt 'Til birtingar'"))
    author = models.ForeignKey(User, editable = False, verbose_name = _(u"Höfundur"))


    is_important = models.BooleanField(_(u"Er mikilvægari en aðrar fréttir"),
                                        default=False,
                                        help_text = _(u"Fréttin mun birtast efst á forsíðu þangað til hún hættir að vera mikilvæg")
                                )
    important_until = models.DateField(_(u"Hættir að vera mikilvæg þann"), null= True, blank = True)
    enable_comments = models.BooleanField(_(u"Leyfa athugasemdir"), default=True)

    status = models.IntegerField(_(u"Staða"),
                                        choices=STATUS_CHOICES,
                                        default=LIVE_STATUS,
                                        help_text = _(u"Frétt birtist ekki á síðunni nema að hún sé merkt 'Til birtingar'"))
    slug = models.SlugField(unique_for_date='publish_date', editable = False, blank = True)
    excerpt = models.TextField(editable = False, blank=True)
    changes = models.ManyToManyField(EntryChange, editable = False)

    objects = models.Manager()
    live_entries = LiveEntriesManager()
    important_entries = ImportantEntriesManager()

    class Meta:
        ordering = ['-publish_date']
        verbose_name = _(u"Frétt")
        verbose_name_plural = _(u"Fréttir")

    def __unicode__(self):
        return u"%s: %s" % (self.default_title, self.author)

    def get_absolute_url(self):
        return ('news_entry_detail', (), { 'year': self.publish_date.strftime("%Y"),
                                           'month': self.publish_date.strftime("%m"),
                                           'day': self.publish_date.strftime("%d"),
                                           'slug': self.slug })
    get_absolute_url = models.permalink(get_absolute_url)

    def get_title(self, language = DEFAULT_LANGUAGE):
        content = self.get_default_content(language = language)
        if content is not None:
            return content.title
        else:
            return str(self.id)
    default_title = property(get_title)

    def get_default_content(self, language = DEFAULT_LANGUAGE):
        try:
            content = self.content.get(language = language)
            return content
        except Content.DoesNotExist:
            try:
                content = self.content.all()[0]
                return content
            except IndexError:
                return None

    def get_body(self, language = DEFAULT_LANGUAGE):
        content = self.get_default_content(language = language)
        if content is not None:
            return content.body
        else:
            return u""
    default_body = property(get_body)

    def get_body_html(self, language = DEFAULT_LANGUAGE):
        content = self.get_default_content(language = language)
        if content is not None:
            return content.body_html
        else:
            return u""
    default_body_html = property(get_body_html)

    def has_multiple_content(self):
        return self.content.all().count() > 1

    def get_contents(self):
        return self.content.filter(language = DEFAULT_LANGUAGE) | self.content.exclude(language = DEFAULT_LANGUAGE)

    def has_changes(self):
        return self.changes.all().count() > 0


class Content(models.Model):
    entry = models.ForeignKey("news.Entry", related_name = 'content')
    language  = models.CharField(_(u"Tungumál"), choices = LANGUAGES, max_length = 2)
    title = models.CharField(_(u"Titill"), max_length=250)
    body = models.TextField(_(u"Meginmál"))
    body_html = models.TextField(editable = False, blank=True)

    class Meta:
        verbose_name = _(u"Meginmál")
        verbose_name_plural = _(u"Meginmál")

    def save(self):
        self.body_html = markdown(self.body)
        super(Content, self).save()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "%s?language=%s" % ( self.entry.get_absolute_url(), self.language)

    def get_id(self):
        """ Gets the canonical id for this content for use as an javascript anchor """
        return "content-%s" % self.language


def add_slug(sender, instance, created, **kwargs):
    if instance.language == DEFAULT_LANGUAGE:
        instance.entry.slug = slugify(instance.title)
        if instance.entry.excerpt == "":
            instance.entry.excerpt = truncatewords_html(instance.body_html, 30)
        instance.entry.save()

models.signals.post_save.connect(add_slug, sender=Content)


