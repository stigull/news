#coding: utf-8
from django.conf.urls.defaults import *

from news.models import Entry

entry_info_dict = {
    'queryset': Entry.live_entries.all(),
    'date_field': 'publish_date',
    }
    
entry_object_info_dict = {'month_format' :'%m' , 'template_object_name': 'entry' }
entry_object_info_dict.update(entry_info_dict)
    
    
urlpatterns = patterns('django.views.generic.date_based',
      (r'^$', 'archive_index', entry_info_dict, 'news_entry_archive_index'),
      (r'^(?P<year>\d{4})/$', 'archive_year', entry_info_dict, 'news_entry_archive_year'),
      (r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'archive_month', entry_info_dict, 'news_entry_archive_month'),
      (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'archive_day', entry_info_dict, 'news_entry_archive_day'),
      (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 'object_detail', entry_object_info_dict, 'news_entry_detail')
 )
