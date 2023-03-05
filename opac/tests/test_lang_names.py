# coding: utf-8

from webapp.config.lang_names import display_original_lang_name, get_original_lang_name

from .base import BaseTestCase


class LangNamesTestCase(BaseTestCase):
    def test_get_original_lang_name(self):
        self.assertEqual(get_original_lang_name("pt"), "Português")
        self.assertEqual(get_original_lang_name("en"), "English")
        self.assertEqual(get_original_lang_name("es"), "Español")
        self.assertEqual(get_original_lang_name("fr"), "français, langue française")
        self.assertEqual(get_original_lang_name("de"), "Deutsch")
        self.assertEqual(get_original_lang_name("it"), "Italiano")
        self.assertEqual(get_original_lang_name("zh"), "中文 (Zhōngwén), 汉语, 漢語")
        self.assertEqual(get_original_lang_name("ar"), "العربية")

    def test_get_original_lang_name_inexisting(self):
        self.assertEqual(get_original_lang_name("bla"), None)

    def test_display_original_lang_name(self):
        self.assertEqual(display_original_lang_name("pt"), "Português")
        self.assertEqual(display_original_lang_name("en"), "English")
        self.assertEqual(display_original_lang_name("es"), "Español")
        self.assertEqual(display_original_lang_name("fr"), "Français")
        self.assertEqual(display_original_lang_name("de"), "Deutsch")
        self.assertEqual(display_original_lang_name("it"), "Italiano")
        self.assertEqual(display_original_lang_name("zh"), "中文 (zhōngwén)")
        self.assertEqual(display_original_lang_name("ar"), "العربية")

    def test_display_original_lang_name_inexisting(self):
        self.assertEqual(display_original_lang_name("bla"), "bla")
