import asyncio
from asyncio import get_event_loop, Task
from typing import List, Optional, Callable, Any, Union

from dirty_models.models import BaseModel
from functools import wraps
from logging import getLogger

from service_client import ServiceClient
from service_client.plugins import PathTokens, Headers

from .formatters import telegram_encoder, telegram_decoder
from .messages import Update, SendMessageRequest, GetUpdatesRequest, SendLocationRequest, AnswerInlineQueryRequest, \
    AnswerCallbackQueryRequest, SendPhotoRequest, Message, User, File, UserProfilePhotos, Chat, ChatMember, \
    GetFileRequest, GetUserProfilePhotoRequest, SetWebhookRequest, SendVideoRequest, SendAudioRequest, \
    SendDocumentRequest, SendStickerRequest, SendVoiceRequest, SendVenueRequest, SendContactRequest, \
    SendChatActionRequest, EditMessageTextRequest, EditMessageCaptionRequest, EditMessageReplyMarkupRequest, \
    KickChatMemberRequest, LeaveChatRequest, UnbanChatMemberRequest, GetChatRequest, GetChatAdministratorsRequest,\
    GetChatCountRequest, GetChatMemberRequest


TELEGRAM_BOT_API_BASEPATH = 'https://api.telegram.org/{prefix}bot{token}'


class TelegramError(Exception):

    """
    Telegram error exception.

    .. attribute:: code

        It contains Telegram error code.

    .. attribute:: msg

        It contains Telegram error description.

    """

    def __init__(self, msg, code):
        super(TelegramError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return "CODE {}: {}".format(self.code, super(TelegramError, self).__str__())


def list_of(message_cls):
    """
    Automatic result message processor for lists.

    :param message_cls: Items class
    :return: callable
    """

    def factory(lst):
        return list(map(message_cls, lst))

    return factory


def result_bool(_) -> True:
    """
    Result factory for success requests.

    :return: :data:`True`
    """
    return True


def message_or_true(msg) -> Union[bool, Message]:
    """
    Result factory for editing requests.

    :return: :data:`True` or :class:`~messages.Message`
    """

    if msg:
        return Message(msg)
    return True


def check_result(func=None,
                 message_cls: BaseModel = Message) -> Union[bool, BaseModel]:
    """
    Decorator to process Telegram responses. It raise :class:`~TelegramError` exception when result is not successful.
    Otherwise it process :class:`~messages.Response` message using `message_cls` parameter as factory.

    :param func: Decorated function. Used in order to decorate a function using default parameters.
    :param message_cls: Message class factory. Default: :class:`~messages.Message`
    :returns: :data:`True` or :class:`~dirty_models.models.BaseModel`
    """

    def wrapper(func):
        @wraps(func)
        async def inner(self, *args, **kwargs):
            try:
                result = await func(self, *args, **kwargs)
                response = result.data
                if response.ok:
                    if response.result is not None:
                        return message_cls(response.result)
                    else:
                        return True
                raise TelegramError(response.description, response.error_code)
            except Exception as ex:
                self.logger.exception(ex)
                raise ex
        return inner
    if func:
        return wrapper(func)
    return wrapper


class Bot:

    def __init__(self, token, base_path=TELEGRAM_BOT_API_BASEPATH,
                 client_name='TelegramBot', client_plugins=None, updates_timeout=100,
                 spec=None, logger=None, loop=None):

        from .telegram_api_spec import spec as default_spec
        spec = spec or default_spec

        self.loop = loop or get_event_loop()
        self.logger = logger or getLogger('telegram-bot')
        plugins = [PathTokens(default_tokens={'token': token, 'prefix': ''}),
                   Headers(default_headers={'content-type': 'application/json'})]

        try:
            plugins.extend(client_plugins)
        except TypeError:
            pass

        self.service_client = ServiceClient(name=client_name,
                                            spec=spec, parser=telegram_decoder, serializer=telegram_encoder,
                                            base_path=base_path,
                                            plugins=plugins)

        self.update_offset = 0
        self.me = None
        self.updates_timeout = updates_timeout

        self.registered_update_processors = []
        self.registered_message_processors = []
        self.registered_commands = {}
        self.registered_inline_providers = {}

    @check_result(message_cls=User)
    async def get_me(self) -> User:
        """
        A simple method for testing your bot's auth token. Requires no parameters.
        Returns basic information about the bot in form of a :class:`~messages.User` object.

        .. seealso:: https://core.telegram.org/bots/api#getme

        :return: Bot metainfo
        """
        user = await self.service_client.get_me()
        self.me = user
        return user

    @check_result(message_cls=list_of(Update))
    async def get_updates(self, query: Optional[GetUpdatesRequest]=None) -> List[Update]:
        """
        Use this method to receive incoming updates using long polling (wiki).
        An Array of :class:`~messages.Update` objects is returned.

        .. seealso:: https://core.telegram.org/bots/api#getupdates

        :param query: Custom get updates request
        :return: List of updates
        """
        if not query:
            query = GetUpdatesRequest()
            query.offset = self.update_offset
            query.timeout = self.updates_timeout
        return await self.service_client.get_updates(query)

    @check_result(message_cls=File)
    async def get_file(self, request: GetFileRequest) -> File:
        """
        Use this method to get basic info about a file and prepare it for downloading.
        For the moment, bots can download files of up to 20MB in size. On success, a File object is returned.
        The file can then be downloaded via :meth:`~bot.download_file`, where <file_path> is taken from the response.
        It is guaranteed that the link will be valid for at least 1 hour. When the link expires,
        a new one can be requested by calling :meth:`~bot.get_file` again.

        .. seealso:: https://core.telegram.org/bots/api#getfile

        :param request: Request model
        """
        return await self.service_client.get_file(request)

    async def download_file(self, file_path: str):
        """
        Download file by file path. File path is retrieve using :meth:`~bot.get_file` method.

        It returns ClientResponse object. You could use read method in order to get file data.
        """
        return await self.service_client.download_file(file_path=file_path)

    @check_result(message_cls=UserProfilePhotos)
    async def get_user_profile_photos(self, request: GetUserProfilePhotoRequest) -> UserProfilePhotos:
        """
        Use this method to get a list of profile pictures for a user.

        .. seealso:: https://core.telegram.org/bots/api#getuserprofilephotos

        :param request: Request model
        """

        return await self.service_client.get_user_profile_photos(request)

    @check_result
    async def set_webhook(self, request: SetWebhookRequest) -> bool:
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, we will send an HTTPS POST request to the
        specified url, containing a JSON-serialized Update. In case of an unsuccessful request,
        we will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook request comes from Telegram, we recommend
        using a secret path in the URL, e.g. https://www.example.com/<token>. Since nobody
        else knows your bot‘s token, you can be pretty sure it’s us.

        .. note::

            1. You will not be able to receive updates using getUpdates
               for as long as an outgoing webhook is set up.
            2. To use a self-signed certificate, you need to upload your
               public key certificate using certificate parameter.
            3. Ports currently supported for Webhooks: 443, 80, 88, 8443.

        .. seealso:: https://core.telegram.org/bots/api#setwebhook

        :param request: Request model
        """

        return await self.service_client.set_webhook(request)

    @check_result
    async def send_message(self, request: SendMessageRequest) -> Message:

        """
        Use this method to send text messages. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendmessage

        :param request: Request model
        """

        return await self.service_client.send_message(request)

    @check_result
    async def send_photo(self, request: SendPhotoRequest) -> Message:

        """
        Use this method to send photos. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendphoto

        :param request: Request model
        """

        return await self.service_client.send_photo(request)

    @check_result
    async def send_video(self, request: SendVideoRequest) -> Message:

        """
        Use this method to send video files, Telegram clients support mp4 videos
        (other formats may be sent as Document). On success, the sent :class:`~messages.Message` is returned.
        Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

        .. seealso:: https://core.telegram.org/bots/api#sendvideo

        :param request: Request model
        """

        return await self.service_client.send_video(request)

    @check_result
    async def send_audio(self, request: SendAudioRequest) -> Message:

        """
        Use this method to send audio files, if you want Telegram clients to display
        them in the music player. Your audio must be in the .mp3 format. On success,
        the sent :class:`~messages.Message` is returned. Bots can currently send audio
        files of up to 50 MB in size, this limit may be changed in the future.

        .. note::
            For sending voice messages, use the :meth:`Bot.send_voice` method instead.

        .. seealso:: https://core.telegram.org/bots/api#sendaudio

        :param request: Request model
        """

        return await self.service_client.send_audio(request)

    @check_result
    async def send_document(self, request: SendDocumentRequest) -> Message:

        """
        Use this method to send general files. On success, the sent :class:`~messages.Message` is returned.
        Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.

        .. seealso:: https://core.telegram.org/bots/api#senddocument

        :param request: Request model
        """

        return await self.service_client.send_document(request)

    @check_result
    async def send_sticker(self, request: SendStickerRequest) -> Message:

        """
        Use this method to send .webp stickers. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendsticker
        """

        return await self.service_client.send_sticker(request)

    @check_result
    async def send_voice(self, request: SendVoiceRequest) -> Message:

        """
        Use this method to send audio files, if you want Telegram clients to display the file as
        a playable voice message. For this to work, your audio must be in an .ogg file encoded
        with OPUS (other formats may be sent as Audio or Document). On success,
        the sent :class:`~messages.Message` is returned. Bots can currently send voice messages of up
        to 50 MB in size, this limit may be changed in the future.

        .. seealso:: https://core.telegram.org/bots/api#sendvoice

        :param request: Request model
        """

        return await self.service_client.send_voice(request)

    @check_result
    async def send_location(self, request: SendLocationRequest) -> Message:

        """
        Use this method to send point on the map. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendlocation

        :param request: Request model
        """

        return await self.service_client.send_location(request)

    @check_result
    async def send_venue(self, request: SendVenueRequest) -> Message:

        """
        Use this method to send information about a venue. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendvenue

        :param request: Request model
        """

        return await self.service_client.send_venue(request)

    @check_result
    async def send_contact(self, request: SendContactRequest) -> Message:

        """
        Use this method to send phone contacts. On success, the sent :class:`~messages.Message` is returned.

        .. seealso:: https://core.telegram.org/bots/api#sendcontact

        :param request: Request model
        """

        return await self.service_client.send_contact(request)

    @check_result(message_cls=result_bool)
    async def send_chat_action(self, request: SendChatActionRequest) -> bool:

        """
        Use this method when you need to tell the user that something is happening on the bot's side.
        The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status).

        .. note::

            The ImageBot needs some time to process a request and upload the image.
            Instead of sending a text message along the lines of “Retrieving image, please wait…”,
            the bot may use :meth:`~bot.send_chat_action` with action = upload_photo.
            The user will see a “sending photo” status for the bot.


        .. seealso:: https://core.telegram.org/bots/api#sendchataction

        :param request: Request model
        """

        return await self.service_client.send_chat_action(request)

    @check_result(message_cls=result_bool)
    async def answer_inline_query(self, request: AnswerInlineQueryRequest) -> bool:

        """
        Use this method to send answers to an inline query. On success, True is returned.

        No more than 50 results per query are allowed.

        .. seealso:: https://core.telegram.org/bots/api#answerinlinequery

        :param request: Request model
        """

        return await self.service_client.answer_inline_query(request)

    @check_result(message_cls=result_bool)
    async def answer_callback_query(self, request: AnswerCallbackQueryRequest) -> bool:

        """
        Use this method to send answers to callback queries sent from inline keyboards.
        The answer will be displayed to the user as a notification at the top of the
        chat screen or as an alert. On success, True is returned.

        .. seealso:: https://core.telegram.org/bots/api#answercallbackquery

        :param request: Request model
        """

        return await self.service_client.answer_callback_query(request)

    @check_result(message_cls=message_or_true)
    async def edit_message_text(self, request: EditMessageTextRequest) -> Union[bool, Message]:

        """
        Use this method to edit text messages sent by the bot or via the bot (for inline bots).
        On success, if edited message is sent by the bot, the edited :class:`~messages.Message` is returned,
        otherwise True is returned.

        .. seealso:: https://core.telegram.org/bots/api#editmessagetext

        :param request: Request model
        """

        return await self.service_client.edit_message_text(request)

    @check_result(message_cls=message_or_true)
    async def edit_message_caption(self, request: EditMessageCaptionRequest) -> Union[bool, Message]:

        """
        Use this method to edit captions of messages sent by the bot or via the bot (for inline bots).
         On success, if edited message is sent by the bot, the edited :class:`~messages.Message` is returned,
         otherwise True is returned.

        .. seealso:: https://core.telegram.org/bots/api#editmessagecaption

        :param request: Request model
        """

        return await self.service_client.edit_message_caption(request)

    @check_result(message_cls=message_or_true)
    async def edit_message_reply_markup(self, request: EditMessageReplyMarkupRequest) -> Union[bool, Message]:

        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot (for inline bots).
        On success, if edited message is sent by the bot, the edited :class:`~messages.Message` is returned,
        otherwise True is returned.

        .. seealso:: https://core.telegram.org/bots/api#editmessagereplymarkup

        :param request: Request model
        """

        return await self.service_client.edit_message_reply_markup(request)

    @check_result(message_cls=result_bool)
    async def kick_chat_member(self, request: KickChatMemberRequest) -> bool:

        """
        Use this method to kick a user from a group or a supergroup. In the case of supergroups,
        the user will not be able to return to the group on their own using invite links, etc.,
        unless unbanned first. The bot must be an administrator in the group for this to work.
        Returns True on success.

        .. seealso:: https://core.telegram.org/bots/api#kickchatmember

        :param request: Request model
        """

        return await self.service_client.kick_chat_member(request)

    @check_result(message_cls=result_bool)
    async def leave_chat(self, request: LeaveChatRequest) -> bool:

        """
        Use this method for your bot to leave a group, supergroup or channel. Returns True on success.

        .. seealso:: https://core.telegram.org/bots/api#leavechat

        :param request: Request model
        """

        return await self.service_client.leave_chat(request)

    @check_result(message_cls=result_bool)
    async def unban_chat_member(self, request: UnbanChatMemberRequest) -> bool:

        """
        Use this method to unban a previously kicked user in a supergroup.
        The user will not return to the group automatically, but will be able to join via link, etc.
        The bot must be an administrator in the group for this to work. Returns True on success.

        .. seealso:: https://core.telegram.org/bots/api#unbanchatmember

        :param request: Request model
        """

        return await self.service_client.unban_chat_member(request)

    @check_result(message_cls=Chat)
    async def get_chat(self, request: GetChatRequest) -> Chat:

        """
        Use this method to get up to date information about the chat (current name of the user
        for one-on-one conversations, current username of a user, group or channel, etc.).
        Returns a :class:`~Chat` object on success.

        .. seealso:: https://core.telegram.org/bots/api#getchat

        :param request: Request model
        """

        return await self.service_client.get_chat(request)

    @check_result(message_cls=list_of(ChatMember))
    async def get_chat_administrators(self, request: GetChatAdministratorsRequest) -> List[ChatMember]:

        """
        Use this method to get a list of administrators in a chat. On success,
        returns an List of :class:`~ChatMember` objects that contains information about all
        chat administrators except other bots. If the chat is a group or a supergroup
        and no administrators were appointed, only the creator will be returned.

        .. seealso:: https://core.telegram.org/bots/api#getchatadministrators

        :param request: Request model
        """

        return await self.service_client.get_chat_administrators(request)

    @check_result(message_cls=int)
    async def get_chat_members_count(self, request: GetChatCountRequest) -> int:

        """
        Use this method to get the number of members in a chat. Returns :class:`int` on success.

        .. seealso:: https://core.telegram.org/bots/api#getchatmemberscount

        :param request: Request model
        """

        return await self.service_client.get_chat_members_count(request)

    @check_result(message_cls=ChatMember)
    async def get_chat_member(self, request: GetChatMemberRequest) -> ChatMember:

        """
        Use this method to get information about a member of a chat.
        Returns a :class:`~ChatMember` object on success.

        .. seealso:: https://core.telegram.org/bots/api#getchatmember

        :param request: Request model
        """

        return await self.service_client.get_chat_member(request)

    async def start_get_updates(self):

        """
        Starts get updates loop.
        """

        await self.get_me()
        while not Task.current_task(self.loop).cancelled():
            updates = await self.get_updates()
            for update in updates:
                asyncio.ensure_future(self.process_update(update), loop=self.loop)

    async def process_update(self, update: Update):

        """
        Process a new update message. It will be processed by all registered update processors and
        by all specific message processors (message, command, chosen inline result or callback query).

        :param update: Update message
        """

        self.logger.debug("New update message: {}".format(repr(update)))

        for up_processor in self.registered_update_processors:
            if up_processor(update) is True:
                self.logger.debug("Update processor dropped update message: {}".format(repr(up_processor)))
                return

        if update.message:
            asyncio.ensure(self.process_message(update.message))
        elif update.inline_query:
            asyncio.ensure(self.process_inline_query(update.inline_query))
        elif update.chose_inline_result:
            asyncio.ensure(self.process_chosen_inline_result(update.chose_inline_result))
        elif update.callback_query:
            asyncio.ensure(self.process_callback_query(update.callback_query))

    def register_update_processor(self, func: Callable[[Update],
                                                       Union[bool, None]]) -> Callable[[Update],
                                                                                       Union[bool, None]]:
        """
        Register a function in order to process any update data. If function returns `True`
        update message will be dropped. Otherwise update message will processed by other processors.

        It could be used as decorator:

        .. code-block:: python

            @bot.register_update_processor
            def new_update_processor(update: Update):
                do_some_thing(update)

                return True


        :param func: Update processor
        :return: Function registered
        """
        self.registered_update_processors.append(func)
        return func

    async def process_message(self, message: Message):
        """
        Process and route messages received by bot.

        :param message: Message to process by bot.
        """

        self.logger.debug('Processing message: {}'.format(repr(message)))
        try:
            if message.message_from.id == self.me.id:
                return
        except AttributeError:
            pass

        try:
            for entity in message.entities:
                if entity.type == 'bot_command' and entity.offset == 0:
                    asyncio.ensure(self.execute_command(message), loop=self.loop)
                    return
        except TypeError:
            pass

        for processor in self.registered_message_processors:
            asyncio.ensure(processor(message), loop=self.loop)

    def register_message_processor(self, func: Callable[[Message], Any]) -> Callable[[Message], Any]:
        """
        Register a function in order to process messages.

        It could be used as decorator:

        .. code-block:: python

            @bot.register_message_processor
            def new_message_processor(message: Message):
                do_some_thing(message)


        :param func: Message processor
        :return: Function registered
        """
        self.registered_message_processors.append(func)
        return func

    async def execute_command(self, message):
        for entity in message.entities:
            if entity.type == 'bot_command' and entity.offset == 0:
                command = message.text[1:entity.length]
                self.logger.info("Executing command: " + command)
                break
        try:
            await self.registered_commands[command](message)
        except KeyError:
            self.logger.warn('Unknown command: {}'.format(command))
            req = SendMessageRequest()
            req.chat_id = message.chat.id
            req.text = 'Unknown command'
            await self.send_message(req)
        except Exception as ex:
            self.logger.exception(ex)

    def register_command(self, command: str, func: Union[Callable[[Message], Any], None]=None):

        def inner(func: Callable[[Message]]):
            self.registered_commands[command] = func

        if func:
            inner(func)
            return func

        return inner

    def register_inline_provider(self, name: str, func: Union[Callable[[Message], Any], None]=None):

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
        req = AnswerInlineQueryRequest()
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
        provider, data = callback_query.data.split(':', 1)
