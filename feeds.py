#coding: utf-8
from django.contrib.syndication.feeds import Feed
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from news.models import Entry


try:
    current_site = Site.objects.get_current()
    sitename = current_site.name
except:
    sitename = ""

class LatestEntries(Feed):
    title = _(u"%(sitename)s: Nýjustu fréttir" % {'sitename' : sitename })
    title_template = "news/feeds/latest_title.html"
    link = "/frettir/"
    description = _(u"Nýjustu fréttirnar frá %(sitename)s" % {'sitename': sitename })
    description_template = "news/feeds/latest_description.html"

    def items(self):
        return Entry.live_entries.all()[:5]
