import datetime

import os
from asynctest.case import TestCase
from service_client.mocks import Mock, mock_manager

from aiotelebot import Bot
from aiotelebot.messages import User, Update, GetFileRequest, File, GetUserProfilePhotoRequest, UserProfilePhotos, \
    SendMessageRequest, Message, Chat
from tests.telegram_api_mock_spec import MOCK_DIR
from .telegram_api_mock_spec import mock_spec


class TelegramModelFormatterIterTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.bot = Bot('testtoken',
                       client_plugins=[Mock()],
                       spec=mock_spec,
                       loop=self.loop)

    async def test_get_me(self):
        user = await self.bot.get_me()
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 1000000001)
        self.assertEqual(user.first_name, "telebot")
        self.assertEqual(user.username, "telebot")

    async def test_get_updates_empty(self):
        updates = await self.bot.get_updates()
        self.assertEqual(updates, [])

    @mock_manager.patch_mock_desc({'file': os.path.join(MOCK_DIR, 'get_updates_text.json')})
    async def test_get_updates_text(self):
        updates = await self.bot.get_updates()
        self.assertEqual(len(updates), 1)
        self.assertIsInstance(updates[0], Update)
        self.assertEqual(updates[0].export_data(), {"update_id": 100000001,
                                                    "message": {"message_id": 1001,
                                                                "from": {"id": 10000002,
                                                                         "first_name": "Telebot",
                                                                         "username": "telebotuser"},
                                                                "chat": {"id": 10000001,
                                                                         "first_name": "Telebot",
                                                                         "username": "telebotuser",
                                                                         "type": Chat.Type.PRIVATE},
                                                                "date": datetime.datetime(2016, 9, 29, 21, 53, 34,
                                                                                          tzinfo=datetime.timezone.utc),
                                                                "text": "test"}})

    @mock_manager.patch_mock_desc({'file': os.path.join(MOCK_DIR, 'get_updates_image.json')})
    async def test_get_updates_image(self):
        updates = await self.bot.get_updates()
        self.assertEqual(len(updates), 1)
        self.assertIsInstance(updates[0], Update)
        self.assertEqual(updates[0].export_data(), {"update_id": 100000001,
                                                    "message": {"message_id": 1002,
                                                                "from": {"id": 10000002,
                                                                         "first_name": "Telebot",
                                                                         "username": "telebotuser"},
                                                                "chat": {"id": 10000001,
                                                                         "first_name": "Telebot",
                                                                         "username": "telebotuser",
                                                                         "type": Chat.Type.PRIVATE},
                                                                "date": datetime.datetime(2016, 9, 29, 21, 53, 34,
                                                                                          tzinfo=datetime.timezone.utc),
                                                                "photo": [{"file_id": "aaAAbb1",
                                                                           "file_size": 565,
                                                                           "width": 90,
                                                                           "height": 25},
                                                                          {"file_id": "aaAAbb2",
                                                                           "file_size": 3134,
                                                                           "width": 320,
                                                                           "height": 90},
                                                                          {"file_id": "aaAAbb3",
                                                                           "file_size": 6533,
                                                                           "width": 580,
                                                                           "height": 164}]}})

    async def test_get_file(self):
        file_path = await self.bot.get_file(GetFileRequest(file_id="aaAAbb1"))
        self.assertIsInstance(file_path, File)
        self.assertEqual(file_path.export_data(), {"file_id": "aaAAbb1",
                                                   "file_size": 6533,
                                                   "file_path": "photo/file_1.jpg"})

    async def test_download_file(self):
        response = await self.bot.download_file("photo/file_1.jpg")

        with open(os.path.join(MOCK_DIR, 'python-logo.png'), 'rb') as mock_file:
            self.assertEqual(await response.read(), mock_file.read())

    async def test_get_user_profile_photos(self):
        response = await self.bot.get_user_profile_photos(GetUserProfilePhotoRequest(user_id=10000001))
        self.assertIsInstance(response, UserProfilePhotos)
        self.assertEqual(response.export_data(), {"total_count": 1,
                                                  "photos": [[{"file_id": "aaAAbb1",
                                                               "file_size": 14511,
                                                               "width": 160,
                                                               "height": 160},
                                                              {"file_id": "aaAAbb2",
                                                               "file_size": 48458,
                                                               "width": 320,
                                                               "height": 320},
                                                              {"file_id": "aaAAbb3",
                                                               "file_size": 161155,
                                                               "width": 640,
                                                               "height": 640},
                                                              {"file_id": "aaAAbb4",
                                                               "file_size": 173081,
                                                               "width": 799,
                                                               "height": 799}]]})

    async def test_send_message(self):
        response = await self.bot.send_message(SendMessageRequest(chat_id=10000001, text='test'))
        self.assertIsInstance(response, Message)
        self.assertEqual(response.export_data(), {"message_id": 101,
                                                  "from": {"id": 10000001,
                                                           "first_name": "telebot",
                                                           "username": "telebot"},
                                                  "chat": {"id": 10000002,
                                                           "first_name": "telebot_user",
                                                           "username": "telebot_user",
                                                           "type": Chat.Type.PRIVATE},
                                                  "date": datetime.datetime(2016, 10, 3, 20, 46, 31,
                                                                            tzinfo=datetime.timezone.utc),
                                                  "text": "test",
                                                  "entities": [{"type": "bold",
                                                                "offset": 0,
                                                                "length": 4}]})
