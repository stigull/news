#coding: utf-8
import unittest

from utils.stringformatting import slugify

class TestCreateNews(unittest.TestCase): 
    
    def test_create_news_single_language(self):
        """ Creates a news with a single language """
        #TODO: How to test the admin forms?
        pass
   
    def test_slugify(self):
        """ Tests the slugify function """
        self.assertEqual(slugify(u"aábeéfghiíjklmnoópqrstuúvwxyýzþæö[]()+\\/;,.#"), u"aabeefghiijklmnoopqrstuuvwxyyzthaeo----")
    
