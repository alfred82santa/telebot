from json import dumps

from aiohttp.hdrs import CONTENT_TYPE
from aiohttp.multipart import MultipartWriter
from aiohttp.payload import get_payload
from multidict import CIMultiDict

from dirty_models.fields import ArrayField, ModelField
from dirty_models.models import BaseModel
from dirty_models.utils import ModelFormatterIter, JSONEncoder, ListFormatterIter
from service_client.json import json_decoder

from .messages import FileModel, Response


class ContainsFileError(Exception):
    pass


class TelegramModelFormatterIter(ModelFormatterIter):

    def format_field(self, field, value):
        if isinstance(field, ModelField):
            if isinstance(value, FileModel):
                return value
            return dumps(value, cls=JSONEncoder)
        elif isinstance(field, ArrayField):
            return dumps(ListFormatterIter(obj=value,
                                           field=value.get_field_type(),
                                           parent_formatter=ModelFormatterIter(model=self.model)),
                         cls=JSONEncoder)

        return super(TelegramModelFormatterIter, self).format_field(field, value)


class TelegramJsonEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, FileModel):
            raise ContainsFileError()
        elif isinstance(obj, BaseModel):
            obj = TelegramModelFormatterIter(obj)
        return super(TelegramJsonEncoder, self).default(obj)


def telegram_encoder(content, *args, **kwargs):
    try:
        return dumps(content, cls=TelegramJsonEncoder)
    except ContainsFileError:
        pass

    formatter = TelegramModelFormatterIter(content)

    kwargs['endpoint_desc']['stream_request'] = True

    mp = MultipartWriter('form-data')

    for field, value in formatter:
        content_dispositon = {'name': field}
        if isinstance(value, FileModel):
            part = get_payload(value.stream, headers=CIMultiDict())
            if value.name:
                content_dispositon['filename'] = value.name
            if value.mime_type:
                part.headers[CONTENT_TYPE] = value.mime_type
        else:
            part = get_payload(str(value), headers=CIMultiDict())

        part.set_content_disposition("form-data", **content_dispositon)
        mp.append_payload(part)

    try:
        kwargs['request_params']['headers'].update(mp.headers)
    except KeyError:
        kwargs['request_params']['headers'] = mp.headers

    return mp


def telegram_decoder(content, *args, **kwargs):
    return Response(json_decoder(content, *args, **kwargs))
