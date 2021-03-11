#!/usr/bin/python3.7
import re
import logging
from sys import path as syspath
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, \
    InlineKeyboardButton
from configparser import ConfigParser
from stathat import StatHat
from sentry_sdk import init, capture_message
from clean import output
from gtrans import trans, trans_auto
from termcolor import cprint

# 初始化 bot
try:
    cfg = ConfigParser()
    cfg.read(syspath[0] + '/config.ini')
    API_TOKEN = cfg.get('bot', 'token')
    ADMIN_ID = cfg.get('bot', 'admin')
    STAT = cfg.get('stat', 'enabled')  # 不启用则不使用统计
    STAT_ACCOUNT = cfg.get('stat', 'account')
    STAT_INSTANCE = cfg.get('stat', 'instance')
    SENTRY_SDK = cfg.get('sentry', 'sdk')
    GROUP_LIST = cfg.get('group', 'enabled')
    LANG = cfg.get('lang', 'destination')  # 暂时没有使用

except Exception:
    cprint('Config file error, exit...', 'white', 'on_red')
    capture_message('Config file error, exit...')
    print(Exception)
    exit()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
init(SENTRY_SDK, traces_sample_rate=1.0)


delete_btn = types.InlineKeyboardMarkup(resize_keyboard=True, selective=True)
# delete_btn.insert(InlineKeyboardButton(text='👍', callback_data='vote'))
delete_btn.insert(InlineKeyboardButton(text='🗑️', callback_data='delete'))

# 定义函数



@dp.callback_query_handler(text='delete')
async def _(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer(text="该消息已删除")

    
def translate_text(text, lang='zh-CN', detect=1, type=0):
    if type == 0:  # Specific language
        translated_cleaned = output(trans(text, lang))
    elif type == 1:  # Auto Translation
        translated_cleaned = output(trans_auto(text))
    else:  # To Chinese
        translated_cleaned = output(trans(text, lang))
    if STAT:
        try:
            stathat = StatHat()
            stathat.ez_post_count(STAT_ACCOUNT, STAT_INSTANCE, 1)
        except Exception as e:
            cprint('Request susceed but stat failed!' + str(e), 'white', 'on_red')
            capture_message('Request susceed but stat failed!')
    return translated_cleaned


def translate_msg(message: types.Message,
                  offset: int = 0,
                  lang: str = None,
                  reg: str = None):
    if message.reply_to_message:  # 如果是回复则取所回复消息文本
        text = message.reply_to_message.text
    else:  # 如果不是回复则取命令后文本
        text = message.text[offset:]  # 去除命令文本
    try:
        text = text.replace('@fanyi_bot', '').strip()
    except:
        pass
    if reg:
        text = re.sub(reg, '', text)
    if len(text) == 0:
        if message.reply_to_message:
            clog(message)
            capture_message(message)
            result = translate_text(text, lang)
            return result
        else:
            result = '''忘记添加需要翻译的文本？请在命令后添加需要翻译的话，例如：

/en 你好
'''
            return \
                result
    else:
        clog(message)
        capture_message(message)
        result = translate_text(text, lang)
        print(result)
        return \
            result


def translate_auto(message: types.Message,
                   offset: int = 0,
                   lang: str = None,
                   reg: str = None):
    if message.reply_to_message and (len(
            re.sub(
                r'^(translate|trans|tran|翻译|中文|Chinese|zh|英文|英语|English|en)',
                "", message.text)) <= 1):  # 如果是回复则取所回复消息文本
        text = message.reply_to_message.text
    else:  # 如果不是回复则取命令后文本
        text = message.text[offset:]  # 去除命令文本
    text = text.replace('@fanyi_bot', '').strip()
    if reg:
        text = re.sub(reg, '', text)
    if len(text) == 0:
        if message.reply_to_message:
            clog(message)
            capture_message(message)
            result = translate_text(text)
            return result
        else:
            result = '''忘记添加需要翻译的文本？请在命令后添加需要翻译的话，例如：

/en 你好
'''
            return \
                result
    else:
        clog(message)
        capture_message(message)
        result = trans_auto(text)
        print(result)
        return result


def clog(message):
    chat_type = message.chat.type
    user = message.from_user.username
    user_id = message.from_user.id
    group = message.chat.title
    group_id = message.chat.id
    chat_name = message.chat.username or message.from_user.username
    if group:
        log_msg = f'[{chat_type}, %{group}, %{group_id}, &{chat_name}, \@{user}, #{user_id}] {message.text}'
        cprint(log_msg, 'white', 'on_cyan')
        capture_message(log_msg)
    else:
        log_msg = f'[{chat_type}, @{chat_name}, #{user_id}] {message.text} '
        cprint(log_msg, 'white', 'on_cyan')
        capture_message(log_msg)


####################################################################################################
# 欢迎词
@dp.message_handler(commands=['start', 'welcome', 'about', 'help'])
async def command_start(message: types.Message):
    intro = '''使用说明：
- 私聊机器人，自动翻译文字消息；
- 群聊中添加机器人，使用命令翻译指定消息；
- 任意聊天框，输入 @fanyi_bot 实时翻译。

使用样例：
/fy 检测语言并翻译
/zh Translate a sentence into Chinese.
/en 翻译到英文

最近更新
- [2020.11.14] 修复了一个上游引起的 BUG

加入群组 @fanyi_group 参与讨论。'''
    await bot.send_chat_action(message.chat.id, action="typing")
    await message.answer(intro)


####################################################################################################
# 翻译命令
####################################################################################################
# 中英文
@dp.message_handler(commands=['fy', 'tr', '翻译'])
async def command_fy(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    result = translate_msg(message, 3)  # None -> Chinese + English
    await message.reply(result, reply_markup=delete_btn)


# 中文
@dp.message_handler(commands=['zh'])
async def command_zh(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    result = translate_msg(message, 3, 'zh')
    await message.reply(result, reply_markup=delete_btn)


# 英文
@dp.message_handler(commands=['en'])
async def command_en(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    result = translate_msg(message, 3, 'en')
    await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(commands=['id'])
async def command_id(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    result = message.chat.id
    await message.reply(result, reply_markup=delete_btn)


####################################################################################################
# 自然指令
####################################################################################################
@dp.message_handler(regexp='^(translate|trans|tran|翻译) ')
async def keyword_fy(message: types.Message):
    result = translate_msg(message, reg='^(translate|trans|tran|翻译) ')
    await bot.send_chat_action(message.chat.id, action="typing")
    await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(regexp='^(英文|英语|English|en) ')
async def keyword_en(message: types.Message):
    result = translate_msg(message, lang='en', reg='^(英文|英语|English|en) ')
    await bot.send_chat_action(message.chat.id, action="typing")
    await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(regexp='^(中文|Chinese|zh) ')
async def keyword_zh(message: types.Message):
    result = translate_msg(message, lang='zh', reg='^(中文|Chinese|zh) ')
    await bot.send_chat_action(message.chat.id, action="typing")
    await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(regexp='^(translate|trans|tran|翻译)')
async def reply_keyword_fy(message: types.Message):
    if message.reply_to_message:
        result = translate_msg(message, reg='^(translate|trans|tran|翻译)')
        await bot.send_chat_action(message.chat.id, action="typing")
        await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(regexp='^(英文|English|en)')
async def reply_keyword_en(message: types.Message):
    if message.reply_to_message:
        result = translate_msg(message, lang='en', reg='^(英文|English|en)')
        await bot.send_chat_action(message.chat.id, action="typing")
        await message.reply(result, reply_markup=delete_btn)


@dp.message_handler(regexp='^(中文|Chinese|zh)')
async def reply_keyword_zh(message: types.Message):
    if message.reply_to_message:
        result = translate_msg(message, lang='zh', reg='^(中文|Chinese|zh)')
        await bot.send_chat_action(message.chat.id, action="typing")
        await message.reply(result, reply_markup=delete_btn)


####################################################################################################
# 私聊自动检测语言并翻译
####################################################################################################


@dp.callback_query_handler(text='translate')
async def query_translate(call: types.CallbackQuery):
    origin_msg = call.message.text.split('▸')[1].split('\n')[0]
    translated_msg = call.message.text.split('▸')[-1]
    # await bot.send_chat_action(message.chat.id, action="typing")
    await call.answer(text="消息已翻译 Message translated")
    await bot.edit_message_text("`" + call.message.text.split('▸')[0] + "`" + \
        output(trans_auto(translated_msg)), call.message.chat.id, call.message.message_id,
        parse_mode="markdown")


@dp.callback_query_handler(text=['zh', 'en', 'ja', 'ru', 'vi'])
async def query_specify(call: types.CallbackQuery):
    languages = {'zh': '🇨🇳', 'en': '🇺🇸', 'ja': '🇯🇵', 'ru': '🇷🇺', 'vi': '🇻🇳'}
    # await bot.send_chat_action(message.chat.id, action="typing")
    reply_message = call.message.reply_to_message
    reply_text = reply_message.text
    action_btn = types.InlineKeyboardMarkup(resize_keyboard=True,
                                            selective=True)
    action_btn.insert(
        InlineKeyboardButton(text=f'{languages[call.data]}',
                             callback_data='select'))
    action_btn.insert(InlineKeyboardButton(text='🗑️', callback_data='del'))
    await call.answer(text=f"{languages[call.data]} 正在翻译 Translating...")
    await bot.edit_message_text(output(translate_text(reply_text, call.data)), call.message.chat.id,
                                call.message.message_id, parse_mode="markdown", reply_markup=action_btn)

    # await call.answer(text="消息已翻译 Message translated")


@dp.callback_query_handler(text='del')
async def query_delete(call: types.CallbackQuery):
    # await bot.send_chat_action(message.chat.id, action="typing")
    await call.answer(text="消息已删除 Message deleted")
    await call.message.delete()


@dp.callback_query_handler(text='select')
async def query_select(call: types.CallbackQuery):
    # await bot.send_chat_action(message.chat.id, action="typing")
    action_btn = types.InlineKeyboardMarkup(resize_keyboard=True,
                                            selective=True)
    action_btn.insert(InlineKeyboardButton(text='🇨🇳', callback_data='zh'))
    action_btn.insert(InlineKeyboardButton(text='🇺🇸', callback_data='en'))
    action_btn.insert(InlineKeyboardButton(text='🇯🇵', callback_data='ja'))
    action_btn.insert(InlineKeyboardButton(text='🇷🇺', callback_data='ru'))
    action_btn.insert(InlineKeyboardButton(text='🇻🇳', callback_data='vi'))
    action_btn.insert(InlineKeyboardButton(text='🗑️', callback_data='del'))
    await call.answer(text="请选择一种语言 Please select a language")
    await bot.edit_message_text(call.message.text, call.message.chat.id,
                                call.message.message_id, parse_mode="markdown",
                                disable_web_page_preview=True, reply_markup=action_btn)


@dp.callback_query_handler(text='mute')
async def query_mute(call: types.CallbackQuery):
    origin_msg = call.message.text.split('▸')[1].split('\n')[0]
    # await bot.send_chat_action(message.chat.id, action="typing")
    await call.answer(text="显示原消息 Original message showed")
    await bot.edit_message_text(origin_msg, call.message.chat.id, call.message.message_id,
                                parse_mode="markdown")


@dp.message_handler(content_types=types.message.ContentType.TEXT)
async def text_translate(message: types.Message):
    chat_type = message.chat.type
    chat_id = message.chat.id
    action_btn = types.InlineKeyboardMarkup(resize_keyboard=True,
                                            selective=True)

    action_btn.insert(
        InlineKeyboardButton(text='🇨🇳🇺🇸🇯🇵', callback_data='select'))
    action_btn.insert(InlineKeyboardButton(text='🗑️', callback_data='del'))
    if chat_type == 'private':
        
        await bot.send_chat_action(message.chat.id, action="typing")
        capture_message(
            f'[{chat_type}, @{message.from_user.id}, #{message.from_user.first_name}] {message.text} '
        )
        result = translate_text(message.text)
        await message.reply(result, disable_notification=True)
    elif ((chat_type == 'group') or
          (chat_type == 'supergroup')) and (str(chat_id) in GROUP_LIST):
        cprint(f"{chat_id} 自动翻译 {message.text}", 'white', 'on_cyan')
        capture_message(
            f'[{chat_type}, @{message.from_user.id}, #{message.from_user.first_name}] {message.text} '
        )
        await bot.send_chat_action(message.chat.id, action="typing")
        result = output(trans_auto(message.text))
        await message.reply( result, parse_mode='markdown', disable_notification=True,
                             disable_web_page_preview=True, reply_markup=action_btn)
    else:  # 过滤所有群聊、频道
        # print(str(message.chat.id) in GROUP_LIST)
        pass


@dp.message_handler()
async def text_others(message: types.Message):
    print('Other types')
    capture_message('Other types')
    try:
        # clog(message)
        capture_message(message)

        await bot.send_chat_action(message.chat.id, action="typing")
        result = translate_text(message.text)
    except Exception as e:
        print('Exception', e)
        capture_message('Exception', e)
        result = '? ? ?'
    await message.answer(result)


# 行内查询
@dp.inline_handler()
async def inline(inline_query: InlineQuery):
    text = inline_query.query or '输入以翻译 Input to Translate...'
    user = inline_query.from_user.username
    user_id = inline_query.from_user.id
    end_str = ''
    if len(text) >= 256:
        end_str = '\n\n(达到长度限制，请私聊翻译全文）'
    if text == '输入以翻译 Input to Translate...':
        pass
    else:
        cprint(f'[inline, @{user}, #{user_id}] {text} ', 'white', 'on_cyan')
        capture_message(f'[inline, @{user}, #{user_id}] {text} ')
        zh_str = translate_text(text, 'zh')
        en_str = translate_text(text, 'en')
        jp_str = translate_text(text, 'ja')
<<<<<<< HEAD
        pt_str = translate_text(text, 'pt')
=======
>>>>>>> ba7c48ab6ebc951069e909751025729ee74925a0
        items = [
            InlineQueryResultArticle(
                id=0,
                title=f'{en_str}'.strip(),
                description='🇺🇸 English',
                thumb_width=0,
                input_message_content=InputTextMessageContent(
                    f'{en_str}{end_str}', disable_web_page_preview=True),
            ),
            InlineQueryResultArticle(
                id=1,
                title=f'{zh_str}'.strip(),
                description='🇨🇳 中文',
                thumb_width=0,
                input_message_content=InputTextMessageContent(
                    f'{zh_str}{end_str}', disable_web_page_preview=True),
            ),
            InlineQueryResultArticle(
                id=2,
                title=f'{jp_str}'.strip(),
                description='🇯🇵 にほんご',
                thumb_width=0,
                input_message_content=InputTextMessageContent(
                    f'{jp_str}{end_str}', disable_web_page_preview=True),
            ),
            InlineQueryResultArticle(
                id=3,
                title=f'{pt_str}'.strip(),
                description='🇵🇹 Português',
                thumb_width=0,
                input_message_content=InputTextMessageContent(
                    f'{pt_str}{end_str}', disable_web_page_preview=True),
            )
        ]
        await bot.answer_inline_query(inline_query.id,
                                      results=items,
                                      cache_time=300)


if __name__ == '__main__':
    cprint('I\'m working now...', 'white', 'on_green')
    # capture_message('I\'m working now...')
    executor.start_polling(dp, skip_updates=True)
