from mimetypes import guess_type

from dirty_models.fields import StringIdField, StringField, ModelField, DateTimeField, ArrayField, IntegerField, \
    BooleanField, FloatField, MultiTypeField, BaseField, BlobField
from dirty_models.models import BaseModel
from os.path import split


class StreamField(BaseField):

    def convert_value(self, value):
        return open(value, 'rb')

    def check_value(self, value):
        return hasattr(value, 'read')

    def can_use_value(self, value):
        return isinstance(value, str)


class FileModel(BaseModel):
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

    id = StringIdField()


class BaseActor(PersistentModel):

    first_name = StringIdField()
    last_name = StringIdField()
    username = StringIdField()


class User(BaseActor):
    pass


class Chat(BaseActor):

    type = StringIdField()
    title = StringField()


class ChatMember(BaseModel):

    user = ModelField(model_class=User)
    status = StringIdField()


class MessageEntity(BaseModel):

    type = StringIdField()
    offset = IntegerField()
    length = IntegerField()
    url = StringIdField()
    user = ModelField(model_class=User)


class BaseAttachment(BaseModel):

    file_id = StringIdField()
    file_size = IntegerField()


class ImageMixin(BaseModel):
    width = IntegerField()
    height = IntegerField()


class FileMixin(BaseModel):

    title = StringField()
    mime_type = StringField()


class StreamMixin(FileMixin):
    duration = IntegerField()


class PhotoSize(BaseAttachment, ImageMixin):
    pass


class PreviewFileMixin(BaseModel):
    thumb = ModelField(model_class=PhotoSize)


class Audio(BaseAttachment, StreamMixin):

    performer = StringField()


class Document(BaseAttachment, PreviewFileMixin):
    pass


class Sticker(PhotoSize, PreviewFileMixin):

    emoji = StringIdField()


class Video(BaseAttachment, ImageMixin, StreamMixin,
            PreviewFileMixin):
    pass


class Voice(BaseAttachment, StreamMixin):
    pass


class Contact(BaseModel):

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()
    user_id = IntegerField()


class Location(BaseModel):

    longitude = FloatField()
    latitude = FloatField()


class Venue(BaseModel):

    location = ModelField(model_class=Location)
    title = StringField()
    address = StringIdField()
    foursquare_id = StringIdField()


class UserProfilePhotos(BaseModel):

    total_count = IntegerField()
    photos = ArrayField(field_type=ModelField(model_class=PhotoSize))


class Message(BaseModel):

    message_id = StringIdField()
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

    file_id = StringIdField()
    file_size = IntegerField()
    file_path = StringIdField()


class KeyboardButton(BaseModel):

    text = StringField()
    request_contact = BooleanField(default=False)
    request_location = BooleanField(default=False)


class BaseKeyboardMarkup(BaseModel):
    pass


class ReplyKeyboardHide(BaseKeyboardMarkup):

    hide_keyboard = BooleanField(default=True)
    selective = BooleanField(default=False)


class InlineKeyboardButton(BaseModel):

    text = StringField()
    url = StringIdField()
    callback_data = StringIdField()
    switch_inline_query = StringIdField()


class InlineKeyboardMarkup(BaseKeyboardMarkup):

    inline_keyboard = ArrayField(field_type=ArrayField(field_type=ModelField(model_class=InlineKeyboardButton)))


class ReplyKeyboardMarkup(BaseKeyboardMarkup):

    keyboard = ArrayField(field_type=ArrayField(field_type=ModelField(model_class=KeyboardButton)))
    resize_keyboard = BooleanField(default=False)
    one_time_keyboard = BooleanField(default=False)
    selective = BooleanField(default=False)


class CallbackQuery(PersistentModel):

    user_from = ModelField(name='from', model_class=User)
    message = ModelField(model_class=Message)
    inline_message_id = StringIdField()
    data = StringIdField()


class ForceReply(BaseKeyboardMarkup):

    force_reply = BooleanField(default=True)
    selective = BooleanField(default=False)


class BaseChatRequest(BaseModel):

    chat_id = MultiTypeField(field_types=[IntegerField(), StringIdField()])


class BaseChatMessageRequest(BaseChatRequest):

    disable_notification = BooleanField(default=False)
    reply_to_message_id = IntegerField()
    reply_markup = MultiTypeField(field_types=[ModelField(model_class=InlineKeyboardMarkup),
                                               ModelField(model_class=ReplyKeyboardMarkup),
                                               ModelField(model_class=ReplyKeyboardHide),
                                               ModelField(model_class=ForceReply)])


class SendMessageRequest(BaseChatMessageRequest):

    text = StringField()
    parse_mode = StringField()
    disable_web_page_preview = BooleanField(default=False)


class SendPhotoRequest(BaseChatMessageRequest):

    photo = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    caption = StringField()


class SendAudioRequest(BaseChatMessageRequest):

    audio = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()
    performer = StringIdField()
    title = StringField()


class SendDocumentRequest(BaseChatMessageRequest):

    document = MultiTypeField(field_types=[StringIdField(),
                                           ModelField(model_class=FileModel)])
    caption = StringField()


class SendStickerRequest(BaseChatMessageRequest):

    sticker = MultiTypeField(field_types=[StringIdField(),
                                          ModelField(model_class=FileModel)])


class SendVideoRequest(BaseChatMessageRequest):

    video = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()
    width = IntegerField()
    height = IntegerField()
    caption = StringField()


class SendVoiceRequest(BaseChatMessageRequest):

    voice = MultiTypeField(field_types=[StringIdField(),
                                        ModelField(model_class=FileModel)])
    duration = IntegerField()


class SendLocationRequest(BaseChatMessageRequest):

    latitude = FloatField()
    longitude = FloatField()


class SendVenueRequest(SendLocationRequest):

    title = StringField()
    address = StringIdField()
    foursquare_id = StringIdField()


class SendContactRequest(BaseChatMessageRequest):

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class SendChatActionRequest(BaseChatRequest):

    action = StringIdField()


class KickChatMemberRequest(BaseChatRequest):

    user_id = StringIdField()


class UnbanChatMemberRequest(KickChatMemberRequest):
    pass


class LeaveChatRequest(BaseChatRequest):
    pass


class BaseEditMessageRequest(BaseChatRequest):
    message_id = StringIdField()
    inline_message_id = StringIdField()
    reply_markup = ModelField(model_class=InlineKeyboardMarkup)


class EditMessageReplyMarkupRequest(BaseEditMessageRequest):
    pass


class EditMessageCaptionRequest(BaseEditMessageRequest):

    caption = StringField()


class EditMessageTextRequest(BaseEditMessageRequest):

    text = StringField()
    parse_mode = StringIdField()
    disable_web_page_preview = BooleanField(default=False)


class GetUserProfilePhotoRequest(BaseModel):

    user_id = StringIdField()
    offset = IntegerField()
    limit = IntegerField()


class GetFileRequest(BaseModel):

    file_id = StringIdField()


class AnswerCallbackQueryRequest(BaseModel):

    callback_query_id = StringIdField()
    text = StringField()
    show_alert = BooleanField(default=False)


class InlineQuery(PersistentModel):

    user_from = ModelField(name='from', model_class=User)
    location = ModelField(model_class=Location)
    query = StringField()
    offset = IntegerField()


class InputMessageContent(BaseModel):
    pass


class InlineQueryResult(PersistentModel):

    input_message_content = ModelField(model_class=InputMessageContent)
    reply_markup = ModelField(model_class=InlineKeyboardMarkup)


class AnswerInlineQuery(BaseModel):

    inline_query_id = StringIdField()
    results = ArrayField(field_type=ModelField(model_class=InlineQueryResult))
    cache_time = IntegerField()
    is_personal = BooleanField(default=False)
    next_offset = StringIdField()
    switch_pm_text = StringField()
    switch_pm_parameter = StringField()


class ThumbMixin(BaseModel):

    thumb_url = StringIdField()


class ThumbSizedMixin(ThumbMixin):

    thumb_width = IntegerField()
    thumb_height = IntegerField()


class TitledMixin(BaseModel):

    title = StringField()


class CaptionMixin(BaseModel):

    caption = StringField()


class DescriptionMixin(BaseModel):

    description = StringField()


class InlineQueryResultArticle(InlineQueryResult, ThumbSizedMixin, DescriptionMixin, TitledMixin):
    type = StringIdField(default='article', read_only=True)
    url = StringIdField()
    hide_url = BooleanField(default=False)


class BaseInlineQueryResultPhoto(InlineQueryResult):

    type = StringIdField(default='photo', read_only=True)


class InlineQueryResultPhoto(BaseInlineQueryResultPhoto, ThumbMixin, DescriptionMixin, TitledMixin, CaptionMixin):

    type = StringIdField(default='photo', read_only=True)
    photo_width = IntegerField()
    photo_height = IntegerField()
    photo_url = StringIdField()


class InlineQueryResultCachedPhoto(BaseInlineQueryResultPhoto, DescriptionMixin, TitledMixin, CaptionMixin):

    photo_file_id = StringIdField()


class BaseInlineQueryResultGif(InlineQueryResult):

    type = StringIdField(default='gif', read_only=True)


class InlineQueryResultGif(BaseInlineQueryResultGif, ThumbMixin, TitledMixin, CaptionMixin):

    gif_width = IntegerField()
    gif_height = IntegerField()
    gif_url = StringIdField()


class InlineQueryResultCachedGif(BaseInlineQueryResultGif, TitledMixin, CaptionMixin):

    gif_file_id = StringIdField()


class BaseInlineQueryResultMpeg4Gif(InlineQueryResult):

    type = StringIdField(default='mpeg4_gif', read_only=True)


class InlineQueryResultMpeg4Gif(BaseInlineQueryResultMpeg4Gif, ThumbMixin, TitledMixin, CaptionMixin):
    mpeg4_width = IntegerField()
    mpeg4_height = IntegerField()
    mpeg4_url = StringIdField()


class InlineQueryResultCachedMpeg4Gif(BaseInlineQueryResultMpeg4Gif, TitledMixin, CaptionMixin):

    mpeg4_file_id = StringIdField()


class BaseInlineQueryResultVideo(InlineQueryResult):

    type = StringIdField(default='video', read_only=True)


class InlineQueryResultVideo(BaseInlineQueryResultVideo, ThumbMixin, TitledMixin, CaptionMixin, DescriptionMixin):
    mime_type = StringIdField()
    video_width = IntegerField()
    video_height = IntegerField()
    video_url = StringIdField()
    video_duration = IntegerField()


class InlineQueryResultCachedVideo(BaseInlineQueryResultVideo, TitledMixin, CaptionMixin, DescriptionMixin):

    video_file_id = StringIdField()


class BaseInlineQueryResultAudio(InlineQueryResult):

    type = StringIdField(default='audio', read_only=True)


class InlineQueryResultAudio(BaseInlineQueryResultAudio, TitledMixin):
    performer = StringIdField()
    audio_url = StringIdField()
    audio_duration = IntegerField()


class InlineQueryResultCachedAudio(BaseInlineQueryResultAudio, TitledMixin):

    audio_file_id = StringIdField()


class BaseInlineQueryResultVoice(InlineQueryResult):
    type = StringIdField(default='voice', read_only=True)


class InlineQueryResultVoice(BaseInlineQueryResultVoice, TitledMixin):
    voice_url = StringIdField()
    voice_duration = IntegerField()


class InlineQueryResultCachedVoice(BaseInlineQueryResultVoice, TitledMixin):

    voice_file_id = StringIdField()


class BaseInlineQueryResultDocument(InlineQueryResult):
    type = StringIdField(default='document', read_only=True)


class InlineQueryResultDocument(BaseInlineQueryResultDocument, ThumbSizedMixin, TitledMixin,
                                CaptionMixin, DescriptionMixin):
    mime_type = StringIdField()
    document_url = StringIdField()


class InlineQueryResultCachedDocument(BaseInlineQueryResultDocument, TitledMixin, CaptionMixin, DescriptionMixin):

    document_file_id = StringIdField()


class InlineQueryResultLocation(InlineQueryResult, ThumbSizedMixin, TitledMixin):

    type = StringIdField(default='location', read_only=True)
    longitude = FloatField()
    latitude = FloatField()


class InlineQueryResultVenue(InlineQueryResultLocation):

    type = StringIdField(default='venue', read_only=True)
    address = StringIdField()
    foursquare_id = StringIdField()


class InlineQueryResultContact(InlineQueryResult, ThumbSizedMixin):

    type = StringIdField(default='contact', read_only=True)
    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class InlineQueryResultCachedSticker(InlineQueryResult):

    type = StringIdField(default='sticker', read_only=True)
    sticker_file_id = StringIdField()


class InputTextMessageContent(InputMessageContent):

    message_text = StringField()
    parse_mode = StringIdField()
    disable_web_page_preview = BooleanField(default=False)


class InputLocationMessageContent(InputMessageContent):

    longitude = FloatField()
    latitude = FloatField()


class InputVenueMessageContent(InputLocationMessageContent, TitledMixin):

    address = StringIdField()
    foursquare_id = StringIdField()


class InputContactMessageContent(InputMessageContent):

    phone_number = StringIdField()
    first_name = StringField()
    last_name = StringField()


class ChosenInlineResult(BaseModel):

    result_id = StringIdField()
    user_from = ModelField(name='from', model_class=User)
    location = ModelField(model_class=Location)
    inline_message_id = StringIdField()
    query = StringIdField()


###################
# Getting updates #
###################

class Update(BaseModel):

    update_id = IntegerField()
    message = ModelField(model_class=Message)
    edited_message = ModelField(model_class=Message)
    inline_query = ModelField(model_class=InlineQuery)
    chose_inline_result = ModelField(model_class=ChosenInlineResult)
    callback_query = ModelField(model_class=CallbackQuery)


class GetUpdateRequest(BaseModel):

    offset = IntegerField()
    limit = IntegerField()
    timeout = IntegerField()


###########
# Webhook #
###########

class SetWebhookRequest(BaseModel):

    url = StringIdField()
    certificate = ModelField(model_class=FileModel)


############
# Response #
############

class Response(BaseModel):
    ok = BooleanField()
    result = BlobField()
    description = StringField()
    error_code = IntegerField()
