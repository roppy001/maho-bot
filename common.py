from os import stat_result
import json
import datetime

import discord

import messages

class CommandError(Exception):
    pass

# 1日は3凸まで
ATTACK_MAX = 3

# クラン最大人数 30人
MEMBER_MAX = 30

LAP_CURRENT = -1
LAP_NEXT = -2
ATTACK_MAIN = -1
ATTACK_CARRY_OVER = -2

DATA_CONFIG_KEY = 'config'
DATA_SERVER_KEY = 'server'
DATA_MEMBER_KEY = 'member'
DATA_BOSS_KEY = 'boss'
DATA_DAILY_KEY = 'daily'

DATA_CONFIG_PATH = 'config/config.txt'
DATA_SERVER_PATH = 'data/server.txt'
DATA_MEMBER_PATH = 'data/member.txt'
DATA_BOSS_PATH = 'data/boss.txt'
DATA_DAILY_PATH = 'data/daily.txt'

CONFIG_PHASE_KEY = 'phase'
CONFIG_BOSS_KEY = 'boss'

BOSS_NAME_KEY = 'name'
BOSS_LAP_NO_KEY = 'lap_no'
BOSS_MAX_HP_KEY = 'max_hp'
BOSS_HP_KEY = 'hp'
BOSS_STATUS_KEY = 'status'
BOSS_STATUS_ALIVE = 0
BOSS_STATUS_DEFEATED = 1

DAILY_DATE_KEY = 'date'
DAILY_MEMBER_KEY = 'member'
DAILY_MEMBER_ATTACK_KEY = 'attack'
DAILY_MEMBER_ATTACK_STATUS_KEY = 'status'
DAILY_MEMBER_ATTACK_CARRY_OVER_KEY = 'carry_over'
DAILY_MEMBER_RESERVATION_KEY = 'reservation'
DAILY_MEMBER_RESERVATION_STATUS_KEY = 'status'
DAILY_MEMBER_RESERVATION_LAP_NO_KEY = 'lap_no'
DAILY_MEMBER_RESERVATION_BOSS_ID_KEY = 'boss_id'
DAILY_MEMBER_RESERVATION_DAMAGE_KEY = 'damage'
DAILY_MEMBER_RESERVATION_COMMENT_KEY = 'comment'
DAILY_MEMBER_RESERVATION_DATETIME_KEY = 'datetime'

DAILY_ATTACK_STATUS_NONE = 0 
DAILY_ATTACK_STATUS_CARRY_OVER = 1
DAILY_ATTACK_STATUS_DONE = 2 

DAILY_RESERVE_STATUS_NONE = 0 
DAILY_RESERVE_STATUS_RESERVED = 1
DAILY_RESERVE_STATUS_DONE = 2 

SERVER_GUILD_ID_KEY = 'guild_id'
SERVER_CATEGORY_CHANNEL_KEY = 'category_channel'
SERVER_COMMAND_CHANNEL_KEY = 'command_channel'
SERVER_RESERVATION_CHANNEL_KEY = 'reservation_channel'
SERVER_REST_DETAIL_CHANNEL_KEY = 'rest_detail_channel'

SERVER_RESERVATION_MESSAGE_KEY = 'reservation_message'
SERVER_REST_DETAIL_MESSAGE_KEY = 'rest_detail_message'

MEMBER_ID_KEY = 'id'

async def reply_author(message, str):
    reply = f'{message.author.mention} {str}'
    await message.channel.send(reply)
    return


def get_target_id(mention_ids):
    if len(mention_ids) > 1:
        raise CommandError(messages.error_multi_mention)
    
    return mention_ids[0]

# boss_noを数値に変換するとともに、0-originとなるよう1引く
def convert_boss_no(boss_no):
    try:
        r = int(boss_no)
        if r<1 or r>5 :
            raise CommandError(messages.error_boss_no)
        return r-1
    except ValueError:
        raise CommandError(messages.error_boss_no)

# lap_noを数値に変換する
def convert_lap_no(lap_no):
    try:
        r = int(lap_no)
        if r<0 or r>180:
            raise CommandError(messages.error_lap_no)
        return r
    except ValueError:
        raise CommandError(messages.error_lap_no)

# attack_noを数値に変換するとともに、0-originとなるよう1引く
def convert_attack_no(attack_no):
    try:
        r = int(attack_no)
        if r<1 or r>3:
            raise CommandError(messages.error_attack_no)
        return r-1
    except ValueError:
        raise CommandError(messages.error_attack_no)

def convert_damage(damage):
    try:
        r = int(damage)
        if r<0 or r>=100000:
            raise CommandError(messages.error_damage)
        return r
    except ValueError:
        raise CommandError(messages.error_damage)

def convert_carry_over(carry_over):
    try:
        r = int(carry_over)
        if r<21 or r>90:
            raise CommandError(messages.error_carry_over)
        return r
    except ValueError:
        raise CommandError(messages.error_carry_over)

def convert_boss_no_with_lap_no(str):
    try:
        if str.endswith('+'):
            return (convert_boss_no(str[:len(str)-1]), LAP_NEXT)

        strs = str.split('@')
        if len(strs)==1:
            return (convert_boss_no(str), LAP_CURRENT)
        elif len(strs)==2:
            return (convert_boss_no(strs[0]), convert_boss_no(strs[1]))
        else:
            raise CommandError()
    except CommandError:
        raise CommandError(messages.error_boss_no_with_lap_no)

def convert_damage_with_attack_no(str):
    try:
        strs = str.lower().split('m')
        if len(strs)==1:
            return (convert_damage(strs[0]), ATTACK_MAIN)
        elif len(strs)==2:
            if strs[1] == '':
                return (convert_damage(strs[0]), ATTACK_CARRY_OVER)
            return (convert_damage(strs[0]), convert_attack_no(strs[1]))
        else:
            raise CommandError()
    except CommandError:
        raise CommandError(messages.error_damage_with_attack_no)


def convert_carry_over_with_attack_no(str):
    try:
        str = str.lower()

        if str.startswith('m'):
            str = str[1:]
            if str == '':
                return (0, ATTACK_CARRY_OVER)
            return (0, convert_attack_no(str))
        else:
            return (convert_carry_over(str), ATTACK_MAIN)
    except CommandError:
        raise CommandError(messages.error_carry_over_with_attack_no)

def convert_cancel_attack_no(str):
    try:
        str = str.lower()

        if str.startswith('m'):
            str = str[1:]
            return (convert_attack_no(str), ATTACK_MAIN)
        else:
            return (convert_attack_no(str), ATTACK_CARRY_OVER)
    except CommandError:
        raise CommandError(messages.error_cancel_attack_no)

def check_registered_member(data, id):
    for m in data[DATA_MEMBER_KEY]:
        if id == m[MEMBER_ID_KEY]:
            return
    
    raise CommandError(messages.error_not_member)

def init_boss(data):
    boss_config = data[DATA_CONFIG_KEY][CONFIG_BOSS_KEY]

    new_boss_list = []

    for b in boss_config:
        new_boss = {}
        new_boss[BOSS_NAME_KEY] = b[BOSS_NAME_KEY]
        new_boss[BOSS_LAP_NO_KEY] = 1
        new_boss[BOSS_MAX_HP_KEY] = b[BOSS_MAX_HP_KEY][0]
        new_boss[BOSS_HP_KEY] = b[BOSS_MAX_HP_KEY][0]
        new_boss[BOSS_STATUS_KEY] = BOSS_STATUS_ALIVE

        new_boss_list.append(new_boss)

    save_boss(new_boss_list)

    data[DATA_BOSS_KEY] = new_boss_list
    
    return

#現在時刻から午前5時以降を当日とする日付を返却
def get_date(dt : datetime.datetime):
    return (dt + datetime.timedelta(hours=-5)).date()

#日次予約情報を初期化
def init_daily(data):

    new_daily = {}
    
    #現在日付を取得し格納
    new_daily[DAILY_DATE_KEY] = get_date(datetime.datetime.now()).isoformat()
    new_daily[DAILY_MEMBER_KEY] = {}
    save_daily(new_daily)

    data[DATA_BOSS_KEY] = new_daily

    return

#日次予約情報の初期化データを生成
def create_daily_member():
    new_member = {}
    atk = []

    for i in range(0, ATTACK_MAX):
        s = {}
        s[DAILY_MEMBER_ATTACK_STATUS_KEY] = DAILY_ATTACK_STATUS_NONE
        s[DAILY_MEMBER_ATTACK_CARRY_OVER_KEY] = 0
        atk.append(s)

    new_member[DAILY_MEMBER_ATTACK_KEY] = atk

    new_member[DAILY_MEMBER_RESERVATION_KEY] = []

    return new_member


# DISCORDサーバ設定を読み込む
def load_server_settings():
    fp = open(DATA_SERVER_PATH, 'r', encoding="utf-8")

    server_setting =json.load(fp)

    fp.close()

    return server_setting

# DISCORDサーバ設定を書き込む
def save_server_settings(server_setting):
    fp = open(DATA_SERVER_PATH, 'w', encoding="utf-8")

    json.dump(server_setting, fp, indent=4)

    fp.close()

    return

# メンバ設定を読み込む
def load_members():
    fp = open(DATA_MEMBER_PATH, 'r', encoding="utf-8")

    server_setting =json.load(fp)

    fp.close()

    return server_setting

# メンバ設定を書き込む
def save_members(members):
    fp = open(DATA_MEMBER_PATH, 'w', encoding="utf-8")

    json.dump(members, fp, indent=4)

    fp.close()

    return

# 各種設定を読み込む
def load_config():
    fp = open(DATA_CONFIG_PATH, 'r', encoding="utf-8")

    config =json.load(fp)

    fp.close()

    return config

# ボス情報を読み込む
def load_boss():
    fp = open(DATA_BOSS_PATH, 'r', encoding="utf-8")

    boss =json.load(fp)

    fp.close()

    return boss

# ボス情報を書き込む
def save_boss(boss):
    fp = open(DATA_BOSS_PATH, 'w', encoding="utf-8")

    json.dump(boss, fp, indent=4)

    fp.close()

    return

# 日次予約情報を読み込む
def load_daily():
    fp = open(DATA_DAILY_PATH, 'r', encoding="utf-8")

    daily =json.load(fp)

    fp.close()

    return daily

# 日次予約情報を書き込む
def save_daily(daily):
    fp = open(DATA_DAILY_PATH, 'w', encoding="utf-8")

    json.dump(daily, fp, indent=4)

    fp.close()

    return

