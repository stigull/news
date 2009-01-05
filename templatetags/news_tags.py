#coding: utf-8
from datetime import datetime

from django import template
from django.db.models import Q

from news.models import Entry

register = template.Library()

def display_latest_entries(context, first = 0, last = 5):
    """
    Usage:  {% display_latest_entries i j %}
    Pre:    i and j are positive integers and i < j
    Post:   A list of less important live entries has been rendered starting at the ith entry and ending at the jth entry,
            with the entries ordered descending by the publish date
    """
    list_of_entries = Entry.live_entries.exclude(Q(is_important = True) &
                            Q(important_until__gte = datetime.now())).all()[first:last]
    has_important_entry = Entry.live_entries.filter(Q(is_important = True)).count() > 0
    return {'list_of_entries' : list_of_entries, 'is_first_batch' : first == 0, 'has_important_entry': has_important_entry }
register.inclusion_tag('news/latest_entries.html', takes_context = True)(display_latest_entries)

def display_latest_important_entries():
    """
    Usage:  {% display_latest_important_entries %}
    Post:   A list of important entries has been rendered
    """
    important_entries = Entry.important_entries.all()
    return {'important_entries' : important_entries }
register.inclusion_tag('news/important_entries.html')(display_latest_important_entries)