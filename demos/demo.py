import asyncio
import sys
from asyncio.coroutines import coroutine

import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telebot import Bot
from telebot.messages import SendMessageRequest, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle

BOT_TOKEN = '134190358:AAEaCP-qqF8ZI8T1dKByQOKvI4b0_gG_rL0'

bot = Bot(BOT_TOKEN)


@bot.register_message_processor
@coroutine
def location_received(message):
    if not message.location:
        return

    req = SendMessageRequest()
    req.chat_id = message.chat.id
    req.text = '{0} has sent a localization'.format(message.message_from.first_name)
    req.reply_markup = bot.build_reply_keyboard(
        keyboard=[[KeyboardButton(text='aaaaa'), KeyboardButton(text='bbbbb')]],
        resize_keyboard=False,
        one_time_keyboard=True
    )
    yield from bot.send_message(req)


@bot.register_command('whoiam')
@coroutine
def whoiam_command(message):
    req = SendMessageRequest()
    req.chat_id = message.chat.id
    req.parse_mode = 'Markdown'
    req.text = "\n".join(['*UserID:* {}'.format(message.message_from.id),
                          '*Username:* {}'.format(message.message_from.username),
                          '*First name:* {}'.format(message.message_from.first_name),
                          '*Last name:* {}'.format(message.message_from.last_name)])

    req.reply_markup = bot.build_reply_keyboard(
        keyboard=[[KeyboardButton(text='aaaaa'), KeyboardButton(text='bbbbb'), KeyboardButton(text='ccccc')],
                  [KeyboardButton(text='Qaaaaa'), KeyboardButton(text='Qbbbbb'), KeyboardButton(text='Qccccc')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    yield from bot.send_message(req)


@bot.register_inline_provider(name='options')
@coroutine
def options_provider(query=None, chosen_inline_result=None):
    """
    :param query: telebot.messages.InlineQuery
    :param chosen_inline_result: telebot.messages.ChosenInlineResult
    :return:
    """
    if query:
        return [InlineQueryResultArticle(
                type='article',
                id='1',
                title="Would you like a beer?",
                description="Ask for a beer",
                input_message_content=InputTextMessageContent(message_text="Would you like a beer?"),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Yes, I would!!",
                                                                                         callback_data="beer_yes"),
                                                                    InlineKeyboardButton(text="No, I can't",
                                                                                         callback_data="beer_no")]]))]


asyncio.get_event_loop().run_until_complete(bot.start_get_updates())
