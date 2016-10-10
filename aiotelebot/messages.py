from mimetypes import guess_type

from os.path import split

from dirty_models.fields import StringIdField, StringField, ModelField, DateTimeField, ArrayField, IntegerField, \
    BooleanField, FloatField, MultiTypeField, BaseField, BlobField
from dirty_models.models import BaseModel


class StreamField(BaseField):
    """
    Field type used to send streams (files) to Telegram.
    """

    def convert_value(self, value):
        return open(value, 'rb')

    def check_value(self, value):
        return hasattr(value, 'read')

    def can_use_value(self, value):
        return isinstance(value, str)


class FileModel(BaseModel):
    """
    File model which contains an stream and some metadata avout stream.
    """

    name = StringIdField()
    mime_type = StringIdField()
    stream = StreamField()

    @classmethod
    def from_filename(cls, filename):
        try:
            mime_type = guess_type(filename)[0]
        except IndexError:  # pragma: no cover
            mime_type = None

        return FileModel(stream=filename,
                         name=split(filename)[-1],
                         mime_type=mime_type)


class PersistentModel(BaseModel):
    """
    Base model for entities with identifier.
    """

    id = MultiTypeField(field_types=[IntegerField(), StringIdField()])


class BaseActor(PersistentModel):
    """
    Base model for telegram actors.
    """

    first_name = StringIdField()
    last_name = StringIdField()
    username = StringIdField()


class User(BaseActor):
    """
    This object represents a Telegram user or bot.

    .. seealso:: https://core.telegram.org/bots/api#user
    """
    pass


class Chat(BaseActor):
    """
    This object represents a chat.

    .. seealso:: https://core.telegram.org/bots/api#chat
    """

    TYPE_PRIVATE = 'private'
    TYPE_GROUP = 'group'
    TYPE_SUPERGROUP = 'supergroup'
    TYPE_CHANNEL = 'channel'

    type = StringIdField()
    title = StringField()


class ChatMember(BaseModel):
    """
    This object contains information about one member of the chat.

    .. seealso:: https://core.telegram.org/bots/api#chatmember
    """

    STATUS_CREATOR = 'creator'
    STATUS_ADMINISTRATOR = 'administrator'
    STATUS_MEMBER = 'member'
    STATUS_LEFT = 'left'
    STATUS_KICKED = 'kicked'

    user = ModelField(model_class=User)
    status = StringIdField()


class MessageEntity(BaseModel):
    """
    This object represents one special entity in a text message. For example, hashtags, usernames, URLs, etc.

    .. seealso:: https://core.telegram.org/bots/api#messageentity
    """

    type = StringIdField()
    offset = IntegerField()
    length = IntegerField()
    url = StringIdField()
    user = ModelField(model_class=User)


class ParseModeMixin(BaseModel):
    """
    Mixin model with parse mode definition.
    """

    PARSE_MODE_MARKDOWN = 'Markdown'
    PARSE_MODE_HTML = 'HTML'

    parse_mode = StringField(default=PARSE_MODE_MARKDOWN)


class BaseAttachment(BaseModel):
    """
    Base model for attachments.
    """

    file_id = StringIdField()
    file_size = IntegerField()


class ImageMixin(BaseModel):
    """
    Mixin model with common fields for image attachments.
    """

    width = IntegerField()
    height = IntegerField()


class FileMixin(BaseModel):
    """
    Mixin model with common fields for file attachments.
    """

    title = StringField()
    mime_type = StringField()


class StreamMixin(FileMixin):
    """
    Mixin model with common fields for stream attachments.
    """

    duration = IntegerField()


class PhotoSize(BaseAttachment, ImageMixin):
    """
    This object represents one size of a photo or a file / sticker thumbnail.

    .. seealso:: https://core.telegram.org/bots/api#photosize
    """

    pass


class PreviewFileMixin(BaseModel):
    """
    Mixin model with common fields for file previews.
    """

    thumb = ModelField(model_class=PhotoSize)


class Audio(BaseAttachment, StreamMixin):
    """
    This object represents an audio file to be treated as music by the Telegram clients.

    .. seealso:: https://core.telegram.org/bots/api#audio
    """

    performer = StringField()


class Document(BaseAttachment, PreviewFileMixin):
    """
    This object represents a general file (as opposed to photos, voice messages and audio files).

    .. seealso:: https://core.telegram.org/bots/api#document
    """
    pass


class Sticker(PhotoSize, PreviewFileMixin):
    """
    This object represents a sticker.

    .. seealso:: https://core.telegram.org/bots/api#sticker
    """

    emoji = StringIdField()


class Video(BaseAttachment, ImageMixin, StreamMixin,
            PreviewFileMixin):
    """
    This object represents a video file.

    .. seealso:: https://core.telegram.org/bots/api#video
    """
    pass


class Voice(BaseAttachment, StreamMixin):
    """
    This object represents a voice note.

    .. seealso:: https://core.telegram.org/bots/api#video
    """
    pass


class Contact(BaseModel):
    """
    This object represents a phone contact.

    .. seealso:: https://core.telegram.org/bots/api#contact
    """

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()
    user_id = IntegerField()


class Location(BaseModel):
    """
    This object represents a point on the map.

    .. seealso:: https://core.telegram.org/bots/api#location
    """

    longitude = FloatField()
    latitude = FloatField()


class Venue(BaseModel):
    """
    This object represents a venue.

    .. seealso:: https://core.telegram.org/bots/api#venue
    """

    location = ModelField(model_class=Location)
    title = StringField()
    address = StringIdField()
    foursquare_id = StringIdField()


class UserProfilePhotos(BaseModel):
    """
    This object represent a user's profile pictures.

    .. seealso:: https://core.telegram.org/bots/api#userprofilephotos
    """

    total_count = IntegerField()
    photos = ArrayField(field_type=ArrayField(field_type=ModelField(model_class=PhotoSize)))


class Message(BaseModel):
    """
    This object represents a message.

    .. seealso:: https://core.telegram.org/bots/api#message
    """

    message_id = MultiTypeField(field_types=[IntegerField(), StringIdField()])
    message_from = ModelField(name="from", model_class=User)
    date = DateTimeField()
    edit_date = DateTimeField()
    chat = ModelField(model_class=Chat)
    forward_from = ModelField(model_class=User)
    forward_date = DateTimeField()
    forward_from_chat = ModelField(model_class=Chat)
    reply_to_message = ModelField()
    text = StringField()
    entities = ArrayField(field_type=ModelField(model_class=MessageEntity))
    audio = ModelField(model_class=Audio)
    document = ModelField(model_class=Document)
    photo = ArrayField(field_type=ModelField(model_class=PhotoSize))
    sticker = ModelField(model_class=Sticker)
    video = ModelField(model_class=Video)
    voice = ModelField(model_class=Voice)
    caption = StringField()
    contact = ModelField(model_class=Contact)
    location = ModelField(model_class=Location)
    venue = ModelField(model_class=Venue)
    new_chat_member = ModelField(model_class=User)
    left_chat_member = ModelField(model_class=User)
    new_chat_title = StringField()
    new_chat_photo = ArrayField(field_type=ModelField(model_class=PhotoSize))
    delete_chat_photo = BooleanField()
    group_chat_create = BooleanField()
    supergroup_chat_created = BooleanField()
    channel_chat_created = BooleanField()
    migrate_to_chat_id = IntegerField()
    migrate_from_chat_id = IntegerField()
    pinned_message = ModelField()


class File(BaseModel):
    """
    This object represents a file ready to be downloaded. The file can be downloaded via the link
    https://api.telegram.org/file/bot<token>/<file_path>. It is guaranteed that the link will be
    valid for at least 1 hour. When the link expires, a new one can be requested by calling getFile.

    .. note::
        Maximum file size to download is 20 MB

    .. seealso:: https://core.telegram.org/bots/api#file
    """

    file_id = StringIdField()
    file_size = IntegerField()
    file_path = StringIdField()


class KeyboardButton(BaseModel):
    """
    This object represents one button of the reply keyboard. For simple text buttons String can be
    used instead of this object to specify text of the button. Optional fields are mutually exclusive.

    .. seealso:: https://core.telegram.org/bots/api#keyboardbutton
    """
    text = StringField()
    request_contact = BooleanField(default=False)
    request_location = BooleanField(default=False)


class BaseKeyboardMarkup(BaseModel):
    """
    Parent model of keyboard markups.
    """
    pass


class ReplyKeyboardHide(BaseKeyboardMarkup):
    """
    Upon receiving a message with this object, Telegram clients will hide the current custom keyboard
    and display the default letter-keyboard. By default, custom keyboards are displayed until a new
    keyboard is sent by a bot. An exception is made for one-time keyboards that are hidden immediately
    after the user presses a button (see :class:`~ReplyKeyboardMarkup`).

    .. seealso:: https://core.telegram.org/bots/api#replykeyboardhide
    """

    hide_keyboard = BooleanField(default=True)
    selective = BooleanField(default=False)


class InlineKeyboardButton(BaseModel):
    """
    This object represents one button of an inline keyboard. You must use exactly one of the optional fields.

    .. seealso:: https://core.telegram.org/bots/api#inlinekeyboardbutton
    """

    text = StringField()
    url = StringIdField()
    callback_data = StringIdField()
    switch_inline_query = StringIdField()


class InlineKeyboardMarkup(BaseKeyboardMarkup):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.

    .. warning::
        Inline keyboards are currently being tested and are not available in channels yet.
        For now, feel free to use them in one-on-one chats or groups.

    .. seealso:: https://core.telegram.org/bots/api#inlinekeyboardmarkup

    """

    inline_keyboard = ArrayField(field_type=ArrayField(field_type=ModelField(model_class=InlineKeyboardButton)),
                                 default=[])


class ReplyKeyboardMarkup(BaseKeyboardMarkup):
    """
    This object represents a custom keyboard with reply options.

    .. seealso:: https://core.telegram.org/bots/api#replykeyboardmarkup
    """

    keyboard = ArrayField(field_type=ArrayField(field_type=ModelField(model_class=KeyboardButton)),
                          default=[])
    resize_keyboard = BooleanField(default=False)
    one_time_keyboard = BooleanField(default=False)
    selective = BooleanField(default=False)


class CallbackQuery(PersistentModel):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.
    If the button that originated the query was attached to a message sent by the bot, the field
    message will be presented. If the button was attached to a message sent via the bot (in inline mode),
    the field inline_message_id will be presented.

    .. seealso:: https://core.telegram.org/bots/api#callbackquery
    """
    callback_query_from = ModelField(name='from', model_class=User)
    message = ModelField(model_class=Message)
    inline_message_id = StringIdField()
    data = StringIdField()


class ForceReply(BaseKeyboardMarkup):
    """
    Upon receiving a message with this object, Telegram clients will display a reply interface to
    the user (act as if the user has selected the bot‘s message and tapped ’Reply'). This can be
    extremely useful if you want to create user-friendly step-by-step interfaces without having
    to sacrifice privacy mode.

    .. seealso:: https://core.telegram.org/bots/api#forcereply
    """

    force_reply = BooleanField(default=True)
    selective = BooleanField(default=False)


class BaseChatRequest(BaseModel):
    """
    Base model of chat request types.
    """

    chat_id = MultiTypeField(field_types=[IntegerField(), StringIdField()])


class GetChatRequest(BaseChatRequest):
    """
    Get chat request model.

    .. seealso:: https://core.telegram.org/bots/api#getchat
    """

    pass


class GetChatAdministratorsRequest(BaseChatRequest):
    """
    Get chat administrators request model.

    .. seealso:: https://core.telegram.org/bots/api#getchatadministrators
    """

    pass


class GetChatCountRequest(BaseChatRequest):
    """
    Get chat count request model.

    .. seealso:: https://core.telegram.org/bots/api#getchatmemberscount
    """

    pass


class GetChatMemberRequest(BaseChatRequest):
    """
    Get chat count request model.

    .. seealso:: https://core.telegram.org/bots/api#getchatmember
    """

    user_id = IntegerField()


class BaseChatMessageRequest(BaseChatRequest):
    """
    Base model of message chat request types.
    """

    disable_notification = BooleanField(default=False)
    reply_to_message_id = IntegerField()
    reply_markup = MultiTypeField(field_types=[ModelField(model_class=InlineKeyboardMarkup),
                                               ModelField(model_class=ReplyKeyboardMarkup),
                                               ModelField(model_class=ReplyKeyboardHide),
                                               ModelField(model_class=ForceReply)])


class SendMessageRequest(BaseChatMessageRequest, ParseModeMixin):
    """
    Text message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendmessage
    """

    text = StringField()
    disable_web_page_preview = BooleanField(default=False)


class SendPhotoRequest(BaseChatMessageRequest):
    """
    Photo message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendphoto
    """

    photo = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    caption = StringField()


class SendAudioRequest(BaseChatMessageRequest):
    """
    Audio message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendaudio
    """

    audio = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()
    performer = StringIdField()
    title = StringField()


class SendDocumentRequest(BaseChatMessageRequest):
    """
    Document message request model.

    .. seealso:: https://core.telegram.org/bots/api#senddocument
    """

    document = MultiTypeField(field_types=[StringIdField(),
                                           ModelField(model_class=FileModel)])
    caption = StringField()


class SendStickerRequest(BaseChatMessageRequest):
    """
    Sticker message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendsticker
    """

    sticker = MultiTypeField(field_types=[StringIdField(),
                                          ModelField(model_class=FileModel)])


class SendVideoRequest(BaseChatMessageRequest):
    """
    Video message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendvideo
    """

    video = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()
    width = IntegerField()
    height = IntegerField()
    caption = StringField()


class SendVoiceRequest(BaseChatMessageRequest):
    """
    Voice message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendvoice
    """

    voice = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()


class SendLocationRequest(BaseChatMessageRequest):
    """
    Location message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendlocation
    """
    latitude = FloatField()
    longitude = FloatField()


class SendVenueRequest(SendLocationRequest):
    """
    Venue message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendvenue
    """

    title = StringField()
    address = StringIdField()
    foursquare_id = StringIdField()


class SendContactRequest(BaseChatMessageRequest):
    """
    Contact message request model.

    .. seealso:: https://core.telegram.org/bots/api#sendcontact
    """

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class SendChatActionRequest(BaseChatRequest):
    """
    Chat action request model.

    .. seealso:: https://core.telegram.org/bots/api#sendchataction
    """
    ACTION_TYPING = 'typing'
    ACTION_UPLOAD_PHOTO = 'upload_photo'
    ACTION_RECORD_VIDEO = 'record_video'
    ACTION_UPLOAD_VIDEO = 'upload_video'
    ACTION_RECORD_AUDIO = 'record_audio'
    ACTION_UPLOAD_AUDIO = 'upload_audio'
    ACTION_UPLOAD_DOCUMENT = 'upload_document'
    ACTION_FIND_LOCATION = 'find_location'

    action = StringIdField()


class KickChatMemberRequest(BaseChatRequest):
    """
    Kick chat member request model.

    .. seealso:: https://core.telegram.org/bots/api#kickchatmember
    """

    user_id = StringIdField()


class UnbanChatMemberRequest(KickChatMemberRequest):
    """
    Unban chat member request model.

    .. seealso:: https://core.telegram.org/bots/api#unbanchatmember
    """

    pass


class LeaveChatRequest(BaseChatRequest):
    """
    Leave chat request model.

    .. seealso:: https://core.telegram.org/bots/api#leavechat
    """

    pass


class BaseEditMessageRequest(BaseChatRequest):
    """
    Base request model for editing messages.
    """

    message_id = StringIdField()
    inline_message_id = StringIdField()
    reply_markup = ModelField(model_class=InlineKeyboardMarkup)


class EditMessageReplyMarkupRequest(BaseEditMessageRequest):
    """
    Edit message reply markup request model.

    .. seealso:: https://core.telegram.org/bots/api#editmessagereplymarkup
    """
    pass


class EditMessageCaptionRequest(BaseEditMessageRequest):
    """
    Edit message caption request model.

    .. seealso:: https://core.telegram.org/bots/api#editmessagecaption
    """

    caption = StringField()


class EditMessageTextRequest(BaseEditMessageRequest, ParseModeMixin):
    """
    Edit message text request model.

    .. seealso:: https://core.telegram.org/bots/api#editmessagetext
    """

    text = StringField()
    disable_web_page_preview = BooleanField(default=False)


class GetUserProfilePhotoRequest(BaseModel):
    """
    Get user profile photo request model.

    .. seealso:: https://core.telegram.org/bots/api#getuserprofilephotos
    """

    user_id = StringIdField()
    offset = IntegerField(default=0)
    limit = IntegerField(default=100)


class GetFileRequest(BaseModel):
    """
    Get file request model.

    .. seealso:: https://core.telegram.org/bots/api#getfile
    """

    file_id = StringIdField()


class AnswerCallbackQueryRequest(BaseModel):
    """
    Answer callback query request model.

    .. seealso:: https://core.telegram.org/bots/api#answercallbackquery
    """

    callback_query_id = StringIdField()
    text = StringField()
    show_alert = BooleanField(default=False)


class InlineQuery(PersistentModel):
    """
    This object represents an incoming inline query. When the user sends an empty query,
    your bot could return some default or trending results.

    .. seealso:: https://core.telegram.org/bots/api#inlinequery
    """

    inline_query_from = ModelField(name='from', model_class=User)
    location = ModelField(model_class=Location)
    query = StringField()
    offset = IntegerField()


class BaseInputMessageContent(BaseModel):
    """
    Base model for input message content types.
    """
    pass


class BaseInlineQueryResult(PersistentModel):
    """
    Base model for inline query result types.
    """

    input_message_content = ModelField(model_class=BaseInputMessageContent)
    reply_markup = ModelField(model_class=InlineKeyboardMarkup)


class AnswerInlineQueryRequest(BaseModel):
    """
    Answer inline query result request model.

    .. seealso:: https://core.telegram.org/bots/api#answerinlinequery
    """

    inline_query_id = StringIdField()
    results = ArrayField(field_type=ModelField(model_class=BaseInlineQueryResult))
    cache_time = IntegerField()
    is_personal = BooleanField(default=False)
    next_offset = StringIdField()
    switch_pm_text = StringField()
    switch_pm_parameter = StringField()


class ThumbMixin(BaseModel):
    """
    Mixin for inline query results with thumbnail image.
    """

    thumb_url = StringIdField()


class ThumbSizedMixin(ThumbMixin):
    """
    Mixin for inline query results with sized thumbnail image.
    """

    thumb_width = IntegerField()
    thumb_height = IntegerField()


class TitledMixin(BaseModel):
    """
    Mixin for inline query results with title.
    """

    title = StringField()


class CaptionMixin(BaseModel):
    """
    Mixin for inline query results with caption.
    """

    caption = StringField()


class DescriptionMixin(BaseModel):
    """
    Mixin for inline query results with description.
    """

    description = StringField()


class InlineQueryResultArticle(BaseInlineQueryResult, ThumbSizedMixin, DescriptionMixin, TitledMixin):
    """
    Represents a link to an article or web page.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultarticle
    """

    TYPE_ARTICLE = 'article'

    type = StringIdField(default=TYPE_ARTICLE, read_only=True)
    url = StringIdField()
    hide_url = BooleanField(default=False)


class BaseInlineQueryResultPhoto(BaseInlineQueryResult):
    """
    Base model for inline query result photo types.
    """

    TYPE_PHOTO = 'photo'

    type = StringIdField(default=TYPE_PHOTO, read_only=True)


class InlineQueryResultPhoto(BaseInlineQueryResultPhoto, ThumbMixin, DescriptionMixin, TitledMixin, CaptionMixin):
    """
    Represents a link to a photo. By default, this photo will be sent by the user with optional caption.
    Alternatively, you can use input_message_content to send a message with the specified content instead of the photo.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultphoto
    """

    photo_width = IntegerField()
    photo_height = IntegerField()
    photo_url = StringIdField()


class InlineQueryResultCachedPhoto(BaseInlineQueryResultPhoto, DescriptionMixin, TitledMixin, CaptionMixin):
    """
    Represents a link to a photo stored on the Telegram servers. By default, this photo will be sent by
    the user with an optional caption. Alternatively, you can use input_message_content to send a message
    with the specified content instead of the photo.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedphoto
    """
    photo_file_id = StringIdField()


class BaseInlineQueryResultGif(BaseInlineQueryResult):
    """
    Base model for inline query result git picture types.
    """

    TYPE_GIF = 'gif'

    type = StringIdField(default=TYPE_GIF, read_only=True)


class InlineQueryResultGif(BaseInlineQueryResultGif, ThumbMixin, TitledMixin, CaptionMixin):
    """
    Represents a link to an animated GIF file. By default, this animated GIF file will be sent by the
    user with optional caption. Alternatively, you can use input_message_content to send a message with
    the specified content instead of the animation.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultgif
    """

    gif_width = IntegerField()
    gif_height = IntegerField()
    gif_url = StringIdField()


class InlineQueryResultCachedGif(BaseInlineQueryResultGif, TitledMixin, CaptionMixin):
    """
    Represents a link to an animated GIF file stored on the Telegram servers. By default,
    this animated GIF file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with specified content instead of the animation.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedgif
    """

    gif_file_id = StringIdField()


class BaseInlineQueryResultMpeg4Gif(BaseInlineQueryResult):
    """
    Base model for inline query result mpeg4 animation types.
    """
    TYPE_MPEG4_GIF = 'mpeg4_gif'

    type = StringIdField(default=TYPE_MPEG4_GIF, read_only=True)


class InlineQueryResultMpeg4Gif(BaseInlineQueryResultMpeg4Gif, ThumbMixin, TitledMixin, CaptionMixin):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound). By default,
    this animated MPEG-4 file will be sent by the user with optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of the animation.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultmpeg4gif
    """

    mpeg4_width = IntegerField()
    mpeg4_height = IntegerField()
    mpeg4_url = StringIdField()


class InlineQueryResultCachedMpeg4Gif(BaseInlineQueryResultMpeg4Gif, TitledMixin, CaptionMixin):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound) stored on the
    Telegram servers. By default, this animated MPEG-4 file will be sent by the user with an optional
    caption. Alternatively, you can use input_message_content to send a message with the specified
    content instead of the animation.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedmpeg4gif
    """

    mpeg4_file_id = StringIdField()


class BaseInlineQueryResultVideo(BaseInlineQueryResult):
    """
    Base model for inline query result video types.
    """
    TYPE_VIDEO = 'video'

    type = StringIdField(default=TYPE_VIDEO, read_only=True)


class InlineQueryResultVideo(BaseInlineQueryResultVideo, ThumbMixin, TitledMixin, CaptionMixin, DescriptionMixin):
    """
    Represents a link to a page containing an embedded video player or a video file. By default,
    this video file will be sent by the user with an optional caption. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the video.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultvideo
    """

    mime_type = StringIdField()
    video_width = IntegerField()
    video_height = IntegerField()
    video_url = StringIdField()
    video_duration = IntegerField()


class InlineQueryResultCachedVideo(BaseInlineQueryResultVideo, TitledMixin, CaptionMixin, DescriptionMixin):
    """
    Represents a link to a video file stored on the Telegram servers. By default, this video file will
    be sent by the user with an optional caption. Alternatively, you can use input_message_content to
    send a message with the specified content instead of the video.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedvideo
    """

    video_file_id = StringIdField()


class BaseInlineQueryResultAudio(BaseInlineQueryResult):
    """
    Base model for inline query result audio types.
    """
    TYPE_AUDIO = 'audio'

    type = StringIdField(default=TYPE_AUDIO, read_only=True)


class InlineQueryResultAudio(BaseInlineQueryResultAudio, TitledMixin):
    """
    Represents a link to an mp3 audio file. By default, this audio file will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the specified content
    instead of the audio.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultaudio
    """

    performer = StringIdField()
    audio_url = StringIdField()
    audio_duration = IntegerField()


class InlineQueryResultCachedAudio(BaseInlineQueryResultAudio, TitledMixin):
    """
    Represents a link to an mp3 audio file stored on the Telegram servers. By default, this audio
    file will be sent by the user. Alternatively, you can use input_message_content to send a message
    with the specified content instead of the audio.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedaudio
    """

    audio_file_id = StringIdField()


class BaseInlineQueryResultVoice(BaseInlineQueryResult):
    """
    Base model for inline query result voice types.
    """
    TYPE_VOICE = 'voice'

    type = StringIdField(default=TYPE_VOICE, read_only=True)


class InlineQueryResultVoice(BaseInlineQueryResultVoice, TitledMixin):
    """
    Represents a link to a voice recording in an .ogg container encoded with OPUS. By default,
    this voice recording will be sent by the user. Alternatively, you can use input_message_content to
    send a message with the specified content instead of the the voice message.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultvoice
    """

    voice_url = StringIdField()
    voice_duration = IntegerField()


class InlineQueryResultCachedVoice(BaseInlineQueryResultVoice, TitledMixin):
    """
    Represents a link to a voice message stored on the Telegram servers. By default, this voice message
    will be sent by the user. Alternatively, you can use input_message_content to send a message with the
    specified content instead of the voice message.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedvoice
    """

    voice_file_id = StringIdField()


class BaseInlineQueryResultDocument(BaseInlineQueryResult):
    """
    Base model for inline query result document types.
    """
    TYPE_DOCUMENT = 'document'

    type = StringIdField(default=TYPE_DOCUMENT, read_only=True)


class InlineQueryResultDocument(BaseInlineQueryResultDocument, ThumbSizedMixin, TitledMixin,
                                CaptionMixin, DescriptionMixin):
    """
    Represents a link to a file. By default, this file will be sent by the user with an optional caption.
    Alternatively, you can use input_message_content to send a message with the specified content instead
    of the file. Currently, only .PDF and .ZIP files can be sent using this method.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultdocument
    """

    mime_type = StringIdField()
    document_url = StringIdField()


class InlineQueryResultCachedDocument(BaseInlineQueryResultDocument, TitledMixin, CaptionMixin, DescriptionMixin):
    """
    Represents a link to a file stored on the Telegram servers. By default, this file will be sent by
    the user with an optional caption. Alternatively, you can use input_message_content to send a message
    with the specified content instead of the file. Currently, only pdf-files and zip archives can be
    sent using this method.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcacheddocument
    """

    document_file_id = StringIdField()


class InlineQueryResultLocation(BaseInlineQueryResult, ThumbSizedMixin, TitledMixin):
    """
    Represents a location on a map. By default, the location will be sent by the user. Alternatively,
    you can use input_message_content to send a message with the specified content instead of the location.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultlocation
    """
    TYPE_LOCATION = 'location'

    type = StringIdField(default=TYPE_LOCATION, read_only=True)
    longitude = FloatField()
    latitude = FloatField()


class InlineQueryResultVenue(InlineQueryResultLocation):
    """
    Represents a venue. By default, the venue will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the venue.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultvenue
    """
    TYPE_VENUE = 'venue'

    type = StringIdField(default=TYPE_VENUE, read_only=True)
    address = StringIdField()
    foursquare_id = StringIdField()


class InlineQueryResultContact(BaseInlineQueryResult, ThumbSizedMixin):
    """
    Represents a contact with a phone number. By default, this contact will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the specified content
    instead of the contact.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcontact
    """
    TYPE_CONTACT = 'contact'

    type = StringIdField(default=TYPE_CONTACT, read_only=True)
    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class InlineQueryResultCachedSticker(BaseInlineQueryResult):
    """
    Represents a link to a sticker stored on the Telegram servers. By default, this sticker will be
    sent by the user. Alternatively, you can use input_message_content to send a message with the
    specified content instead of the sticker.

    .. seealso:: https://core.telegram.org/bots/api#inlinequeryresultcachedsticker
    """
    TYPE_STICKER = 'sticker'

    type = StringIdField(default=TYPE_STICKER, read_only=True)
    sticker_file_id = StringIdField()


class InputTextMessageContent(BaseInputMessageContent, ParseModeMixin):
    """
    Represents the content of a text message to be sent as the result of an inline query.

    .. seealso:: https://core.telegram.org/bots/api#inputtextmessagecontent
    """

    message_text = StringField()
    disable_web_page_preview = BooleanField(default=False)


class InputLocationMessageContent(BaseInputMessageContent):
    """
    Represents the content of a location message to be sent as the result of an inline query.

    .. seealso:: https://core.telegram.org/bots/api#inputlocationmessagecontent
    """

    longitude = FloatField()
    latitude = FloatField()


class InputVenueMessageContent(InputLocationMessageContent, TitledMixin):
    """
    Represents the content of a venue message to be sent as the result of an inline query.

    .. seealso:: https://core.telegram.org/bots/api#inputvenuemessagecontent
    """

    address = StringIdField()
    foursquare_id = StringIdField()


class InputContactMessageContent(BaseInputMessageContent):
    """
    Represents the content of a contact message to be sent as the result of an inline query.

    .. seealso:: https://core.telegram.org/bots/api#inputcontactmessagecontent
    """

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class ChosenInlineResult(BaseModel):
    """
    Represents a result of an inline query that was chosen by the user and sent to their chat partner.

    .. seealso:: https://core.telegram.org/bots/api#choseninlineresult
    """

    result_id = StringIdField()
    chosen_inline_result_from = ModelField(name='from', model_class=User)
    location = ModelField(model_class=Location)
    inline_message_id = StringIdField()
    query = StringIdField()


###################
# Getting updates #
###################

class Update(BaseModel):
    """
    This object represents an incoming update.

    Only one of the optional parameters can be present in any given update.

    .. seealso:: https://core.telegram.org/bots/api#update
    """

    update_id = IntegerField()
    message = ModelField(model_class=Message)
    edited_message = ModelField(model_class=Message)
    inline_query = ModelField(model_class=InlineQuery)
    chose_inline_result = ModelField(model_class=ChosenInlineResult)
    callback_query = ModelField(model_class=CallbackQuery)


class GetUpdatesRequest(BaseModel):
    """
    Get updates request model.

    .. seealso:: https://core.telegram.org/bots/api#getupdates
    """

    offset = IntegerField()
    limit = IntegerField()
    timeout = IntegerField()


###########
# Webhook #
###########

class SetWebhookRequest(BaseModel):
    """
    Set webhook request model.

    .. seealso:: https://core.telegram.org/bots/api#getupdates
    """

    url = StringIdField()
    certificate = ModelField(model_class=FileModel)


############
# Response #
############
class Response(BaseModel):
    """
    Response model.
    """

    ok = BooleanField()
    result = BlobField()
    description = StringField()
    error_code = IntegerField()
