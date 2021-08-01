from os import stat_result
import json

import messages

class CommandError(Exception):
    pass

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

SERVER_GUILD_ID_KEY = 'guild_id'
SERVER_CATEGORY_CHANNEL_KEY = 'category_channel'
SERVER_COMMAND_CHANNEL_KEY = 'command_channel'
SERVER_RESERVATION_CHANNEL_KEY = 'reservation_channel'
SERVER_REST_DETAIL_CHANNEL_KEY = 'rest_detail_channel'

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

