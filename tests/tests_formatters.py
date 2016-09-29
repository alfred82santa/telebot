import re

import io
import os
from json import loads, dumps
from unittest.case import TestCase

from aiohttp import hdrs
from aiohttp.multipart import MultipartWriter

from aiotelebot.formatters import TelegramModelFormatterIter, TelegramJsonEncoder, ContainsFileError, telegram_encoder, \
    telegram_decoder
from aiotelebot.messages import SendPhotoRequest, InlineKeyboardMarkup, AnswerInlineQueryRequest, InlineQueryResultArticle, \
    InputTextMessageContent, FileModel, Response

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TelegramModelFormatterIterTests(TestCase):

    def test_simple(self):

        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption'})

        data = {k: v for k, v in TelegramModelFormatterIter(request)}
        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption'})

    def test_over_serialized_structure(self):

        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        data = {k: v for k, v in TelegramModelFormatterIter(request)}
        self.assertIsInstance(data['reply_markup'], str)
        data['reply_markup'] = loads(data['reply_markup'])
        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption',
                          'reply_markup': {'inline_keyboard': [[{'text': 'but1_1',
                                                                 'callback_data': 'callback_data_1_1'},
                                                                {'text': 'but1_2',
                                                                 'callback_data': 'callback_data_1_2'},
                                                                {'text': 'but1_3',
                                                                 'callback_data': 'callback_data_1_3'}],
                                                               [{'text': 'but2_1',
                                                                 'callback_data': 'callback_data_2_1'},
                                                                {'text': 'but2_2',
                                                                 'callback_data': 'callback_data_2_2'},
                                                                {'text': 'but2_3',
                                                                   'callback_data': 'callback_data_2_3'}]]}},
                         data)

    def test_over_serialized_array(self):

        request = AnswerInlineQueryRequest({'inline_query_id': 'inline_query_id_tests',
                                     'cache_time': 300,
                                     'results': [
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text1'}),
                                              'id': 'test_id_1',
                                              'title': 'test title',
                                              'description': 'description'}),
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text2'}),
                                              'id': 'test_id_2',
                                              'title': 'test title',
                                              'description': 'description'}),
                                     ]})

        data = {k: v for k, v in TelegramModelFormatterIter(request)}

        self.assertIsInstance(data['results'], str)
        data['results'] = loads(data['results'])

        self.assertEqual(data,
                         {'inline_query_id': 'inline_query_id_tests',
                          'cache_time': 300,
                          'is_personal': False,
                          'results': [{'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text1'},
                                       'title': 'test title',
                                       'id': 'test_id_1',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'},
                                      {'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text2'},
                                       'title': 'test title',
                                       'id': 'test_id_2',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'}]},
                         data)

    def test_with_file(self):
        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': FileModel.from_filename(os.path.join(DATA_DIR, 'python-logo.png')),
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        data = {k: v for k, v in TelegramModelFormatterIter(request)}

        self.assertIsInstance(data['photo'], FileModel)
        self.assertIsInstance(data['photo'].stream, io.IOBase)
        del data['photo'].stream
        data['photo'] = data['photo'].export_data()
        data['reply_markup'] = loads(data['reply_markup'])

        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': {'name': 'python-logo.png',
                                    'mime_type': 'image/png'},
                          'disable_notification': False,
                          'caption': 'photo caption',
                          'reply_markup': {'inline_keyboard': [[{'text': 'but1_1',
                                                                 'callback_data': 'callback_data_1_1'},
                                                                {'text': 'but1_2',
                                                                 'callback_data': 'callback_data_1_2'},
                                                                {'text': 'but1_3',
                                                                 'callback_data': 'callback_data_1_3'}],
                                                               [{'text': 'but2_1',
                                                                 'callback_data': 'callback_data_2_1'},
                                                                {'text': 'but2_2',
                                                                 'callback_data': 'callback_data_2_2'},
                                                                {'text': 'but2_3',
                                                                 'callback_data': 'callback_data_2_3'}]]}},
                         data)


class TelegramJsonEncoderIterTests(TestCase):

    def test_simple(self):

        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption'})

        data = loads(dumps(request, cls=TelegramJsonEncoder))

        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption'})

    def test_over_serialized_structure(self):
        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        data = loads(dumps(request, cls=TelegramJsonEncoder))
        self.assertIsInstance(data['reply_markup'], str)
        data['reply_markup'] = loads(data['reply_markup'])
        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption',
                          'reply_markup': {'inline_keyboard': [[{'text': 'but1_1',
                                                                 'callback_data': 'callback_data_1_1'},
                                                                {'text': 'but1_2',
                                                                 'callback_data': 'callback_data_1_2'},
                                                                {'text': 'but1_3',
                                                                 'callback_data': 'callback_data_1_3'}],
                                                               [{'text': 'but2_1',
                                                                 'callback_data': 'callback_data_2_1'},
                                                                {'text': 'but2_2',
                                                                 'callback_data': 'callback_data_2_2'},
                                                                {'text': 'but2_3',
                                                                 'callback_data': 'callback_data_2_3'}]]}},
                         data)

    def test_over_serialized_array(self):

        request = AnswerInlineQueryRequest({'inline_query_id': 'inline_query_id_tests',
                                     'cache_time': 300,
                                     'results': [
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text1'}),
                                              'id': 'test_id_1',
                                              'title': 'test title',
                                              'description': 'description'}),
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text2'}),
                                              'id': 'test_id_2',
                                              'title': 'test title',
                                              'description': 'description'}),
                                     ]})

        data = loads(dumps(request, cls=TelegramJsonEncoder))

        self.assertIsInstance(data['results'], str)
        data['results'] = loads(data['results'])

        self.assertEqual(data,
                         {'inline_query_id': 'inline_query_id_tests',
                          'cache_time': 300,
                          'is_personal': False,
                          'results': [{'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text1'},
                                       'title': 'test title',
                                       'id': 'test_id_1',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'},
                                      {'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text2'},
                                       'title': 'test title',
                                       'id': 'test_id_2',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'}]},
                         data)

    def test_with_file(self):
        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': FileModel.from_filename(os.path.join(DATA_DIR, 'python-logo.png')),
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        with self.assertRaises(ContainsFileError):
            dumps(request, cls=TelegramJsonEncoder)


class TelegramEncoderTests(TestCase):

    def test_simple(self):

        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption'})

        data = loads(telegram_encoder(request))

        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption'})

    def test_over_serialized_structure(self):
        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': 'photoId',
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        data = loads(telegram_encoder(request))
        self.assertIsInstance(data['reply_markup'], str)
        data['reply_markup'] = loads(data['reply_markup'])
        self.assertEqual(data,
                         {'chat_id': 'chat_id_tests',
                          'photo': 'photoId',
                          'disable_notification': False,
                          'caption': 'photo caption',
                          'reply_markup': {'inline_keyboard': [[{'text': 'but1_1',
                                                                 'callback_data': 'callback_data_1_1'},
                                                                {'text': 'but1_2',
                                                                 'callback_data': 'callback_data_1_2'},
                                                                {'text': 'but1_3',
                                                                 'callback_data': 'callback_data_1_3'}],
                                                               [{'text': 'but2_1',
                                                                 'callback_data': 'callback_data_2_1'},
                                                                {'text': 'but2_2',
                                                                 'callback_data': 'callback_data_2_2'},
                                                                {'text': 'but2_3',
                                                                 'callback_data': 'callback_data_2_3'}]]}},
                         data)

    def test_over_serialized_array(self):

        request = AnswerInlineQueryRequest({'inline_query_id': 'inline_query_id_tests',
                                     'cache_time': 300,
                                     'results': [
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text1'}),
                                              'id': 'test_id_1',
                                              'title': 'test title',
                                              'description': 'description'}),
                                         InlineQueryResultArticle(
                                             {'input_message_content': InputTextMessageContent(
                                                 {'message_text': 'test text2'}),
                                              'id': 'test_id_2',
                                              'title': 'test title',
                                              'description': 'description'}),
                                     ]})

        data = loads(telegram_encoder(request))

        self.assertIsInstance(data['results'], str)
        data['results'] = loads(data['results'])

        self.assertEqual(data,
                         {'inline_query_id': 'inline_query_id_tests',
                          'cache_time': 300,
                          'is_personal': False,
                          'results': [{'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text1'},
                                       'title': 'test title',
                                       'id': 'test_id_1',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'},
                                      {'input_message_content': {'disable_web_page_preview': False,
                                                                 'message_text': 'test text2'},
                                       'title': 'test title',
                                       'id': 'test_id_2',
                                       'hide_url': False,
                                       'type': 'article',
                                       'description': 'description'}]},
                         data)

    def test_with_file(self):
        request = SendPhotoRequest({'chat_id': 'chat_id_tests',
                                    'photo': FileModel.from_filename(os.path.join(DATA_DIR, 'python-logo.png')),
                                    'caption': 'photo caption',
                                    'reply_markup': InlineKeyboardMarkup(
                                        {'inline_keyboard': [[{'text': 'but1_1',
                                                               'callback_data': 'callback_data_1_1'},
                                                              {'text': 'but1_2',
                                                               'callback_data': 'callback_data_1_2'},
                                                              {'text': 'but1_3',
                                                               'callback_data': 'callback_data_1_3'}],
                                                             [{'text': 'but2_1',
                                                               'callback_data': 'callback_data_2_1'},
                                                              {'text': 'but2_2',
                                                               'callback_data': 'callback_data_2_2'},
                                                              {'text': 'but2_3',
                                                               'callback_data': 'callback_data_2_3'}]]}
                                    )})

        data = telegram_encoder(request)
        self.assertIsInstance(data, MultipartWriter)

        self.assertTrue(data.headers[hdrs.CONTENT_TYPE].startswith('multipart/form-data'))

        flat_data = {'chat_id': 'chat_id_tests',
                     'disable_notification': 'False',
                     'caption': 'photo caption'}

        name_regex = re.compile('^.*\sname=\"([^"]+)\".*$')
        filename_regex = re.compile('^.*\sfilename=\"([^"]+)\".*$')

        for part in data.parts:
            name = name_regex.match(part.headers[hdrs.CONTENT_DISPOSITION]).group(1)
            self.assertTrue(part.headers[hdrs.CONTENT_DISPOSITION].startswith('form-data'))

            if name in flat_data:
                self.assertEqual(part.obj, flat_data[name])
            elif name == 'reply_markup':
                markup = loads(part.obj)
                self.assertEqual(markup,  {'inline_keyboard': [[{'text': 'but1_1',
                                                                 'callback_data': 'callback_data_1_1'},
                                                                {'text': 'but1_2',
                                                                 'callback_data': 'callback_data_1_2'},
                                                                {'text': 'but1_3',
                                                                 'callback_data': 'callback_data_1_3'}],
                                                               [{'text': 'but2_1',
                                                                 'callback_data': 'callback_data_2_1'},
                                                                {'text': 'but2_2',
                                                                 'callback_data': 'callback_data_2_2'},
                                                                {'text': 'but2_3',
                                                                 'callback_data': 'callback_data_2_3'}]]},
                                 markup)
            elif name == 'photo':
                self.assertEqual(part.filename, 'python-logo.png')
                filename = filename_regex.match(part.headers[hdrs.CONTENT_DISPOSITION]).group(1)
                self.assertEqual(filename, 'python-logo.png')
                self.assertTrue(part.headers[hdrs.CONTENT_TYPE].startswith('image/png'))
            else:
                raise Exception('Unknown field')


class TelegramDecoderTests(TestCase):

    def test_simple(self):
        data = {'ok': True,
                'result': {'any': 'thing'},
                'description': 'description text',
                'error_code': 32}

        resp = telegram_decoder(dumps(data).encode())

        self.assertIsInstance(resp, Response)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.result, {'any': 'thing'})
        self.assertEqual(resp.description, 'description text')
        self.assertEqual(resp.error_code, 32)
