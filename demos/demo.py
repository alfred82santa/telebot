import asyncio
import logging
import sys
from logging.handlers import WatchedFileHandler
from math import ceil

import click
import os
from service_client.formatters import ServiceClientFormatter
from service_client.plugins import InnerLogger, Elapsed


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')

from aiotelebot import Bot
from aiotelebot.messages import GetFileRequest, GetUserProfilePhotoRequest, SendMessageRequest, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, SendPhotoRequest, FileModel, GetUpdatesRequest


def prepare_root_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def prepare_service_logger():
    logger = logging.getLogger('TelegramBot')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    ch = WatchedFileHandler(filename=os.path.join(LOG_DIR, 'service.log'))
    ch.setFormatter(ServiceClientFormatter(fmt="{asctime} | {action} | {method} {full_url} | {message}",
                                           request_fmt="\nHeaders:\n{headers}\nBody:\n{body}",
                                           response_fmt=" | {status_code} {status_text} | "
                                                        "{headers_elapsed}\nHeaders:\n{headers}\nBody:\n{body}",
                                           exception_fmt=" | {exception_repr}",
                                           parse_exception_fmt=" | {status_code} {status_text} | "
                                                               "{headers_elapsed} | {exception_repr}\nHeaders:\n"
                                                               "{headers}\nBody:\n{body}",
                                           headers_fmt="\t{name}: {value}",
                                           headers_sep="\n",
                                           datefmt="%Y-%m-%dT%H:%M:%S%z",
                                           style='{'))
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    return logger


async def echo_result(fut):
    click.echo(repr(await fut))


@click.group()
@click.option('--token', prompt='Your bot token', required=True,
              help='Token for already registered bot.')
@click.pass_context
def cli(ctx, token):
    ctx.obj['logger'] = prepare_root_logger()
    ctx.obj['loop'] = asyncio.get_event_loop()
    ctx.obj['bot'] = Bot(token,
                         client_plugins=[InnerLogger(logger=prepare_service_logger(),
                                                     max_body_length=10000),
                                         Elapsed()],
                         logger=ctx.obj['logger'],
                         loop=ctx.obj['loop'])


@cli.command()
@click.pass_context
def get_me(ctx):
    bot = ctx.obj['bot']

    ctx.obj['loop'].run_until_complete(echo_result(bot.get_me()))


@cli.command()
@click.pass_context
@click.option('--offset', '-o', default=0)
@click.option('--timeout', '-t', default=100)
def get_updates(ctx, offset, timeout):
    bot = ctx.obj['bot']
    ctx.obj['loop'].run_until_complete(echo_result(bot.get_updates(GetUpdatesRequest(offset=offset, timeout=timeout))))


@cli.command()
@click.pass_context
@click.argument('file_id', required=True)
def get_file(ctx, file_id):
    bot = ctx.obj['bot']

    ctx.obj['loop'].run_until_complete(echo_result(bot.get_file(GetFileRequest(file_id=file_id))))


@cli.command()
@click.pass_context
@click.argument('file_path', required=True)
def download_file(ctx, file_path):
    bot = ctx.obj['bot']

    async def write_on_file():
        response = await bot.download_file(file_path)
        click.echo(os.path.join(DOWNLOAD_DIR, os.path.basename(file_path)))
        with open(os.path.join(DOWNLOAD_DIR, os.path.basename(file_path)), 'wb') as out:
            out.write(await response.read())

    ctx.obj['loop'].run_until_complete(write_on_file())


@cli.command()
@click.pass_context
@click.argument('user_id', required=True)
@click.option('--offset', '-o', default=0)
@click.option('--limit', '-l', default=100)
def get_user_profile_photos(ctx, user_id, offset, limit):
    bot = ctx.obj['bot']

    ctx.obj['loop'].run_until_complete(echo_result(bot.get_user_profile_photos(
        GetUserProfilePhotoRequest(user_id=user_id, offset=offset, limit=limit)
    )))


available_reply_markups = ['inline', 'reply', 'hide', 'force']


def build_reply_markups(markup, replies):
    if not len(replies):
        return None

    if markup == 'inline':

        reply_markup = InlineKeyboardMarkup()

        rows = ceil(len(replies) / 3)

        for r in range(0, rows):
            row = []
            for reply_idx in range(r * 3, (r + 1) * 3):
                try:
                    row.append(InlineKeyboardButton(text=replies[reply_idx],
                                                    callback_data=replies[reply_idx]))
                except IndexError:
                    break
            reply_markup.inline_keyboard.append(row)

    if markup == 'reply':

        reply_markup = ReplyKeyboardMarkup()

        rows = ceil(len(replies) / 3)

        for r in range(0, rows):
            row = []
            for reply_idx in range(r * 3, (r + 1) * 3):
                try:
                    row.append(KeyboardButton(text=replies[reply_idx]))
                except IndexError:
                    break
            reply_markup.keyboard.append(row)

    return reply_markup


def parse_text(ctx, text):
    return text.replace('\\n', '\n')


@cli.command()
@click.pass_context
@click.argument('chat_id', required=True)
@click.argument('text', required=True, callback=parse_text)
@click.option('--reply-markup', '-m', type=click.Choice(available_reply_markups))
@click.option('--reply', '-r', multiple=True)
def send_message(ctx, chat_id, text, reply_markup, reply):
    bot = ctx.obj['bot']

    reply_markup = build_reply_markups(reply_markup, reply)

    ctx.obj['loop'].run_until_complete(echo_result(bot.send_message(
        SendMessageRequest(chat_id=chat_id,
                           text=text,
                           reply_markup=reply_markup)
    )))


@cli.command()
@click.pass_context
@click.argument('chat_id', required=True)
@click.argument('file_path', required=True)
@click.option('--reply-markup', '-m', type=click.Choice(available_reply_markups))
@click.option('--reply', '-r', multiple=True)
def send_photo(ctx, chat_id, file_path, reply_markup, reply):
    bot = ctx.obj['bot']

    reply_markup = build_reply_markups(reply_markup, reply)

    ctx.obj['loop'].run_until_complete(echo_result(bot.send_photo(
        SendPhotoRequest(chat_id=chat_id,
                         photo=FileModel.from_filename(file_path),
                         reply_markup=reply_markup)
    )))

if __name__ == '__main__':
    cli(obj={})
