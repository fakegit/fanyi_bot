#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2022-04-04 18:41:57
# @Author  : Reynard (rey@pku.edu.cn)
# @Link    : https://github.com/reycn/fanyi-bot
# @Version : 2.0.0

import json
import random
import time

import requests
from itranslate import itranslate as itrans
# from google_trans_new_modified.google_trans_new import google_translator # for module test
from api.google_trans_new_modified.google_trans_new import \
    google_translator
from tool.clean import clean
from tool.config import config_init
from tool.detect import lang
from loguru import logger
from sentry_sdk import capture_message, init

ID = 10000000
STAT = config_init(None, 'stat.enabled')  # type: ignore # 不启用则不使用统计
STAT_ACCOUNT = config_init(None, 'stat.account')  # type: ignore
STAT_INSTANCE = config_init(None, 'stat.instance')  # type: ignore
SENTRY_SDK = config_init(None, 'sentry.sdk')  # type: ignore
SLEEP = config_init(None, 'bot.sleep')  # type: ignore
DEEPLR = config_init(None, 'deepl.remote_headless')  # type: ignore
DEEPLRU = config_init(None, 'deepl.remote_docker_rust')  # type: ignore
init(SENTRY_SDK, traces_sample_rate=1.0)  # type: ignore


def trans(text: str, to_lang: str, SLEEP: float = 0.3) -> str:
    text = clean(text)
    if STAT:
        try:
            requests.get(
                f'http://api.stathat.com/ez?ezkey={STAT_ACCOUNT}&stat={STAT_INSTANCE}&count=1'
            )
            # logger.info('OK' if r.text == '' else 'Error')
        except Exception as e:
            logger.exception("Stat: ")
            capture_message('Stat: ' + str(e))
    result = None
    while result == None or result == 'API Error':
        try:
            result = balancer(text, to_lang=to_lang)
        except Exception as e:
            logger.exception("Trans:" + str(e))
            capture_message('Trans: ' + str(e))
            pass
    return result


def balancer(text='Test', to_lang='zh') -> str:
    apis = {
        0: it,  # iTranslator
        1: gg_tw,  # Google Taiwan
        2: gg_hk,  # Google Hong Kong
        3: gg_us,  # Google United States
        4: gg_jp,  # Google Japan
        5: dl_r,  # DeepL Web Headless Remote
        6: dl_ru,  # DeepL Rust Docker Local
        7: dl_api  # DeepL Python API Local
    }
    api = apis[random.randint(0, 7)]
    if text != None:
        logger.info("[>>] " + text)
        result = api(text, to_lang)
        logger.info("[<<] [" + api.__name__ + "/" + str(to_lang) + "] " +
                    result)
    else:
        result = "API Error"
    return result


def it(text: str, to_lang: str = 'zh') -> str:
    # tgt = to_lang['to_lang']
    try:
        result = itrans(text, from_lang='auto', to_lang=to_lang)
    except Exception as e:
        logger.error('API-it: ' + str(e))
        capture_message('API-it: ' + str(e))
        result = 'API Error'
    return result


def gg_jp(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'zh'
    try:
        result = google_translator(url_suffix="jp").translate(
            text, lang_tgt=lang_tgt)
    except Exception as e:
        logger.error('API-gg_jp: ' + str(e))
        capture_message('API-gg_jp: ' + str(e))
        result = 'API Error'
    return result


def gg_tw(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'zh'
    try:
        result = google_translator(url_suffix="tw").translate(
            text, lang_tgt=lang_tgt)
    except Exception as e:
        logger.error('API-gg_tw: ' + str(e))
        capture_message('API-gg_tw: ' + str(e))
        result = 'API Error'
    return result


def gg_hk(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'zh'
    try:
        result = google_translator(url_suffix="hk").translate(
            text, lang_tgt=lang_tgt)
    except Exception as e:
        logger.error('API-gg_hk: ' + str(e))
        capture_message('API-gg_hk: ' + str(e))
        result = 'API Error'
    return result


def gg_us(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'zh'
    try:
        result = google_translator(url_suffix="us").translate(
            text, lang_tgt=lang_tgt)
    except Exception as e:
        logger.error('API-gg_us: ' + str(e))
        capture_message('API-gg_us: ' + str(e))
        result = 'API Error'
    return result


def dl_r(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'ZH'
    payload = {'text': text, 'lang_tgt': lang_tgt.upper()}
    r = requests.get(DEEPLR, params=payload)  # type: ignore
    try:
        if r.status_code == 200 and 'application/json' in r.headers.get(
                'Content-Type', ''):
            try:
                result = str(r.json().get('translations')[0]['text'])
            except Exception as e:
                logger.error('API-dl_r: ' + str(e))
                capture_message('API-dl_r: ' + str(e))
                result = 'API Error'
                return result
        else:
            result = 'API Error'
    except Exception as e:
        logger.error('API-dl_r: ' + str(e))
        capture_message('API-dl_r: ' + str(e))
        return 'API Error'


def dl_ru(text: str, to_lang: str = None) -> str:  # type: ignore
    if to_lang:
        lang_tgt = to_lang
    else:
        lang_tgt = 'ZH'
    payload = {
        'text': str(text),
        'source_lang': 'auto',
        'target_lang': lang_tgt.upper()
    }
    r = requests.post(DEEPLRU, data=json.dumps(payload))  # type: ignore
    try:
        if r.status_code == 200 and 'application/json' in r.headers.get(
                'Content-Type', ''):
            if r.json()['code'] == 200:
                try:
                    result = r.json()['data']
                except Exception as e:
                    logger.error('API-dl_ru: ' + str(e))
                    capture_message('API-dl_ru: ' + str(e))
                    result = 'API Error'
                return result
            else:
                raise Exception
        else:
            raise Exception
    except Exception as e:
        logger.error('API-dl_ru: ' + str(e))
        capture_message('API-dl_ru: ' + str(e))
        return 'API Error'


def dl_api(text: str = 'Test', to_lang: str = 'ZH', ID: int = ID) -> str:
    while (ID + 3) % 13 != 0 or (ID + 5) % 29 != 0:
        ID = random.randint(10000000, 88888888)
    text = '"' + text + '"'
    # u_sentence = text.encode("unicode_escape").decode()
    i_count = text.count('i') + 1
    timestamp = int(round(time.time() * 1000))
    timestamp = str(timestamp - timestamp % i_count + i_count)
    if (ID + 3) % 13 == 0 or (ID + 5) % 29 == 0:
        method = '\"method\" : '
    else:
        method = '\"method\": '
    data = '{"jsonrpc":"2.0",' + method + '"LMT_handle_jobs","params":{"jobs":[{"kind":"default","raw_en_sentence":' + text + ',"raw_en_consentence_before":[],"raw_en_consentence_after":[],"preferred_num_beams":4,"quality":"fast"}],"lang":{"user_preferred_langs":["EN","ZH"],"source_lang_user_selected":"auto","target_lang":"' + to_lang + '"},"priority":-1,"commonJobParams":{},"timestamp":' + timestamp + '},"id":' + str(
        ID) + '}'
    r = requests.post('https://www2.deepl.com/jsonrpc',
                      headers={'content-type': 'application/json'},
                      data=data.encode())
    if 'result' in r.json():
        try:
            result = r.json()['result']['translations'][0]['beams'][0][
                'postprocessed_sentence']
        except Exception as e:
            logger.error('API-dl_api: ' + str(e))
            capture_message('API-dl_api: ' + str(e))
            result = 'API Error'
    elif 'error' in r.json():
        result = 'API Error'
        logger.error('API-dl_api: ' + r.json()['error']['message'])
        capture_message('API-dl_api: ' + r.json()['error']['message'])
    else:
        result = 'API Error'
        logger.error('API-dl_api: unknown')
        capture_message('API-dl_api: unknown')
    ID = ID + 1
    return result


if __name__ == "__main__":
    # logger.info(balancer('have a look for me', to_lang='zh'))
    pass
