import asyncio
from asyncio import get_event_loop, Task
from typing import List, Optional

from functools import wraps
from logging import getLogger

from service_client import ServiceClient
from service_client.plugins import PathTokens, Headers

from .formatters import telegram_encoder, telegram_decoder
from .messages import Update, SendMessageRequest, GetUpdateRequest, SendLocationRequest, AnswerInlineQuery, \
    AnswerCallbackQueryRequest, SendPhotoRequest, Message, User, File, UserProfilePhotos, Chat, ChatMember, \
    GetFileRequest, GetUserProfilePhotoRequest, SetWebhookRequest, SendVideoRequest, SendAudioRequest, \
    SendDocumentRequest, SendStickerRequest, SendVoiceRequest, SendVenueRequest, SendContactRequest, \
    SendChatActionRequest, EditMessageTextRequest, EditMessageCaptionRequest, EditMessageReplyMarkupRequest, \
    KickChatMemberRequest, LeaveChatRequest, UnbanChatMemberRequest
from .telegram_api_spec import spec

TELEGRAM_BOT_API_BASEPATH = 'https://api.telegram.org/{prefix}bot{token}'


class TelegramError(Exception):

    def __init__(self, msg, code):
        super(TelegramError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return "CODE {}: {}".format(self.code, super(TelegramError, self).__str__())


def array_of(message_cls):

    def factory(lst):
        return list(map(message_cls, lst))

    return factory


def check_result(func=None, message_cls=Message):

    def wrapper(func):
        @wraps(func)
        async def inner(self, *args, **kwargs):
            try:
                response = await func(self, *args, **kwargs)
                if response.ok:
                    if response.result is not None:
                        return message_cls(response.result)
                    else:
                        return True
                raise TelegramError(response.description, response.error_code)
            except Exception as ex:
                self.logger.exception(ex)
                raise ex
    if func:
        return wrapper(func)
    return wrapper


class Bot:

    def __init__(self, token, base_path=TELEGRAM_BOT_API_BASEPATH,
                 client_name='TelegramBot', client_plugins=None, logger=None, loop=None):
        self.loop = loop or get_event_loop()
        self.logger = logger or getLogger('telegram-bot')
        plugins = [PathTokens(default_tokens={'token': token, 'prefix': ''}),
                   Headers(default_headers={'content-type': 'application/json'})]

        try:
            plugins.append(client_plugins)
        except TypeError:
            pass

        self.service_client = ServiceClient(name=client_name,
                                            spec=spec, parser=telegram_decoder, serializer=telegram_encoder,
                                            base_path=base_path,
                                            plugins=plugins)

        self.update_offset = 0
        self.me = None

        self.registered_message_processor = []
        self.registered_commands = {}
        self.registered_inline_providers = {}

    @check_result(message_cls=User)
    async def get_me(self) -> User:
        user = await self.service_client.get_me()
        self.me = user
        return user

    @check_result(message_cls=array_of(Update))
    async def get_updates(self, query: Optional[GetUpdateRequest]=None) -> List[Update]:
        if not query:
            query = GetUpdateRequest()
            query.offset = self.update_offset
            query.timeout = 100
        return await self.service_client.get_updates(query)

    @check_result(message_cls=File)
    async def get_file(self, request: GetFileRequest) -> File:
        return await self.service_client.get_file(request)

    async def download_file(self, file_path: str):
        return await self.service_client.download_file(file_path=file_path)

    @check_result(message_cls=UserProfilePhotos)
    async def get_user_profile_photos(self, request: GetUserProfilePhotoRequest) -> UserProfilePhotos:
        return await self.service_client.get_user_profile_photos(request)

    @check_result
    async def set_webhook(self, request: SetWebhookRequest) -> bool:
        return await self.service_client.set_webhook(request)

    @check_result
    async def send_message(self, request: SendMessageRequest) -> Message:
        return await self.service_client.send_message(request)

    @check_result
    async def send_photo(self, request: SendPhotoRequest) -> Message:
        return await self.service_client.send_photo(request)

    @check_result
    async def send_video(self, request: SendVideoRequest) -> Message:
        return await self.service_client.send_video(request)

    @check_result
    async def send_audio(self, request: SendAudioRequest) -> Message:
        return await self.service_client.send_audio(request)

    @check_result
    async def send_document(self, request: SendDocumentRequest) -> Message:
        return await self.service_client.send_document(request)

    @check_result
    async def send_sticker(self, request: SendStickerRequest) -> Message:
        return await self.service_client.send_sticker(request)

    @check_result
    async def send_voice(self, request: SendVoiceRequest) -> Message:
        return await self.service_client.send_voice(request)

    @check_result
    async def send_location(self, request: SendLocationRequest) -> Message:
        return await self.service_client.send_location(request)

    @check_result
    async def send_venue(self, request: SendVenueRequest) -> Message:
        return await self.service_client.send_venue(request)

    @check_result
    async def send_contact(self, request: SendContactRequest) -> Message:
        return await self.service_client.send_contact(request)

    @check_result
    async def send_chat_action(self, request: SendChatActionRequest) -> bool:
        return await self.service_client.send_chat_action(request)

    @check_result
    async def answer_inline_query(self, request: AnswerInlineQuery) -> bool:
        return await self.service_client.answer_inline_query(request)

    @check_result
    async def answer_callback_query(self, request: AnswerCallbackQueryRequest) -> bool:
        return await self.service_client.answer_callback_query(request)

    @check_result
    async def edit_message_text(self, request: EditMessageTextRequest) -> bool:
        return await self.service_client.edit_message_text(request)

    @check_result
    async def edit_message_caption(self, request: EditMessageCaptionRequest) -> bool:
        return await self.service_client.edit_message_caption(request)

    @check_result
    async def edit_message_reply_markup(self, request: EditMessageReplyMarkupRequest) -> bool:
        return await self.service_client.edit_message_reply_markup(request)

    @check_result
    async def kick_chat_member(self, request: KickChatMemberRequest) -> bool:
        return await self.service_client.kick_chat_member(request)

    @check_result
    async def leave_chat(self, request: LeaveChatRequest) -> bool:
        return await self.service_client.leave_chat(request)

    @check_result
    async def unban_chat_member(self, request: UnbanChatMemberRequest) -> bool:
        return await self.service_client.unban_chat_member(request)

    @check_result(message_cls=Chat)
    async def get_chat(self, request) -> Chat:
        return await self.service_client.get_chat(request)

    @check_result(message_cls=array_of(User))
    async def get_chat_administrators(self, request):
        return await self.service_client.get_chat_administrators(request)

    @check_result(message_cls=int)
    async def get_chat_members_count(self, request) -> int:
        return await self.service_client.get_chat_members_count(request)

    @check_result(message_cls=ChatMember)
    async def get_chat_member(self, request) -> ChatMember:
        return await self.service_client.get_chat_member(request)

    async def start_get_updates(self):
        await self.get_me()
        while not Task.current_task(self.loop).cancelled():
            await self.get_updates()

    async def process_update(self, update):
        """
        :param update: Update message
        :type update: Update
        """
        if update.message:
            asyncio.ensure(self.process_message(update.message))
        elif update.inline_query:
            asyncio.ensure(self.process_inline_query(update.inline_query))
        elif update.chose_inline_result:
            asyncio.ensure(self.process_chosen_inline_result(update.chose_inline_result))
        elif update.callback_query:
            asyncio.ensure(self.process_callback_query(update.callback_query))

    async def process_message(self, message):
        """

        :param message:
        :type message: telebot.messages.Message
        :return:
        """
        try:
            if message.message_from.id == self.me.id:
                return
        except AttributeError:
            pass

        try:
            for entity in message.entities:
                if entity.type == 'bot_command' and entity.offset == 0:
                    await self.execute_command(message)
                    return
        except TypeError:
            pass

        for processor in self.registered_message_processor:
            asyncio.ensure(processor(message), loop=self.loop)

    def register_message_processor(self, func):
        self.registered_message_processor.append(func)
        return func

    async def execute_command(self, message):
        for entity in message.entities:
            if entity.type == 'bot_command' and entity.offset == 0:
                command = message.text[1:entity.length]
                print("Command: " + command)
                break
        try:
            await self.registered_commands[command](message)
        except KeyError:
            req = SendMessageRequest()
            req.chat_id = message.chat.id
            req.text = 'Unknown command'
            await self.send_message(req)
        except Exception as ex:
            print(repr(ex))

    def register_command(self, command, func=None):

        def inner(func):
            self.registered_commands[command] = func

        if func:
            inner(func)
            return func

        return inner

    def register_inline_provider(self, name, func=None):

        def inner(func):
            self.registered_inline_providers[name] = func

        if func:
            inner(func)
            return func

        return inner

    async def get_inline_results(self, inline_query):
        results = []
        for name, provider in self.registered_inline_providers.items():
            p_results = await provider(query=inline_query)
            for r in p_results:
                r.id = "{}:{}".format(name, r.id)
                results.append(r)
                if len(results) >= 50:
                    return results

    async def process_inline_query(self, inline_query):
        """
        :param inline_query:
        :type inline_query: telebot.messages.InlineQuery
        :return:
        """
        req = AnswerInlineQuery()
        req.inline_query_id = inline_query.id
        req.cache_time = 60

        req.results = await self.get_inline_results(inline_query)
        await self.service_client.answer_inline_query(req)

    async def process_chosen_inline_result(self, chosen_inline_result):
        """

        :param chosen_inline_result:
        :type chosen_inline_result: telebot.messages.ChosenInlineResult
        :return:
        """

        provider, result_id = chosen_inline_result.result_id.split(':', 1)
        chosen_inline_result.result_id = result_id
        await self.registered_inline_providers[provider](chosen_inline_result=chosen_inline_result)

    async def process_callback_query(self, callback_query):
        """

        :param callback_query:
        :type callback_query: telebot.messages.CallbackQuery
        :return:
        """
        req = AnswerCallbackQueryRequest()
        req.text = ("{} ha elegido bien"
                    if callback_query.data == 'birra_si'
                    else "{} ha elegido mal").format(callback_query.user_from.first_name)
        req.callback_query_id = callback_query.id
        req.show_alert = True

        await self.service_client.answer_callback_query(req)
