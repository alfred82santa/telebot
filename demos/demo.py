import asyncio
import logging
import sys
from logging.handlers import WatchedFileHandler

import click
import os
from service_client.formatters import ServiceClientFormatter
from service_client.plugins import InnerLogger, Elapsed


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')

from aiotelebot import Bot
from aiotelebot.messages import GetFileRequest


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
@click.option('--token', prompt='Your bot token',
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
def get_updates(ctx):
    bot = ctx.obj['bot']

    ctx.obj['loop'].run_until_complete(echo_result(bot.get_updates()))


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


if __name__ == '__main__':
    cli(obj={})
