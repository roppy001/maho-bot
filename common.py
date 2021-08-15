import os
import json
import datetime
import asyncio

import discord

import messages

class CommandError(Exception):
    pass

# 1日は3凸まで
ATTACK_MAX = 3

# クラン最大人数 30人
MEMBER_MAX = 30

# ボス5匹
BOSS_MAX = 5

LAP_CURRENT = -1
LAP_NEXT = -2
ATTACK_MAIN = -1
ATTACK_CARRY_OVER = -2

# メッセージ消去時間
REPLY_DISPLAY_TIME = 60

DATA_CONFIG_KEY = 'config'
DATA_SERVER_KEY = 'server'
DATA_MEMBER_KEY = 'member'
DATA_BOSS_KEY = 'boss'
DATA_DAILY_KEY = 'daily'

DATA_LOCK_PATH = 'data/lock.loc'
DATA_CONFIG_PATH = 'config/config.txt'
DATA_HELP_PATH = 'config/help.txt'
DATA_SERVER_PATH = 'data/server.txt'
DATA_MEMBER_PATH = 'data/member.txt'
DATA_BOSS_PATH = 'data/boss.txt'
DATA_DAILY_PATH = 'data/daily.txt'

CONFIG_PHASE_KEY = 'phase'
CONFIG_BOSS_KEY = 'boss'
CONFIG_RESERVATION_LIMIT_KEY = 'reservation_limit'
CONFIG_DEPUTY_LIMITED_KEY = 'deputy_limited'
CONFIG_INVALID_RESERVATION_MOVE_NEXT = 'invalid_reservation_move_next'

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
RESERVATION_STATUS_KEY = 'status'
RESERVATION_LAP_NO_KEY = 'lap_no'
RESERVATION_BOSS_ID_KEY = 'boss_id'
RESERVATION_DAMAGE_KEY = 'damage'
RESERVATION_COMMENT_KEY = 'comment'
RESERVATION_DATETIME_KEY = 'datetime'
RESERVATION_ID_KEY = 'id'
RESERVATION_SEQ_KEY = 'seq'
RESERVATION_BRANCH_KEY = 'branch'


DAILY_ATTACK_STATUS_NONE = 0 
DAILY_ATTACK_STATUS_CARRY_OVER = 1
DAILY_ATTACK_STATUS_DONE = 2 

RESERVE_STATUS_NONE = 0 
RESERVE_STATUS_RESERVED = 1
RESERVE_STATUS_DONE = 2 

SERVER_GUILD_ID_KEY = 'guild_id'
SERVER_CATEGORY_CHANNEL_KEY = 'category_channel'
SERVER_COMMAND_CHANNEL_KEY = 'command_channel'
SERVER_RESERVATION_CHANNEL_KEY = 'reservation_channel'
SERVER_REST_DETAIL_CHANNEL_KEY = 'rest_detail_channel'
SERVER_ADMIN_COMMAND_CHANNEL_KEY = 'admin_command_channel'
SERVER_HELP_CHANNEL_KEY = 'rest_help_channel'

SERVER_RESERVATION_MESSAGE_KEY = 'reservation_message'
SERVER_REST_DETAIL_MESSAGE_KEY = 'rest_detail_message'
SERVER_HELP_MESSAGE_KEY = 'help_message'

MEMBER_ID_KEY = 'id'

STATUS_LIST = ['000', '100', '110', '111', '112', '120', '121', '122', '200', '210', '211', '212', '220', '221', '222']

async def reply_author(message, str):
    reply = f'{message.author.mention} {str}'
    new_message = await message.channel.send(reply)

    await new_message.delete(delay = REPLY_DISPLAY_TIME)
    return


def get_target_id(mention_ids):
    if len(mention_ids) > 1:
        raise CommandError(messages.error_multi_mention)
    
    return mention_ids[0]

# boss_noを数値に変換するとともに、0-originとなるよう1引く
def convert_boss_no(boss_no):
    try:
        r = int(boss_no)
        if r<1 or r>BOSS_MAX :
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
            return (convert_boss_no(strs[0]), convert_lap_no(strs[1]))
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

def convert_status(str):
    st = str.replace('０','0').replace('１','1').replace('２','2').strip()

    if not st in STATUS_LIST:
        raise CommandError(messages.error_status)

    result = []
    for s in st:
        if s == '0':
            result.append(DAILY_ATTACK_STATUS_NONE)
        elif s == '1':
            result.append(DAILY_ATTACK_STATUS_CARRY_OVER)
        else:
            result.append(DAILY_ATTACK_STATUS_DONE)
        
    return result

def convert_lap_no_with_status(str):
    try:
        if str.endswith('+'):
            return (convert_lap_no(str[:len(str)-1]), BOSS_STATUS_DEFEATED)
        
        return (convert_lap_no(str), BOSS_STATUS_ALIVE)
    except CommandError:
        raise CommandError(messages.error_lap_no_with_status)

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

#全ボスの中で最もlap_noが小さい値を得る
def get_min_lap_no(data):
    boss = data[DATA_BOSS_KEY]

    min_lap = 9999

    for b in boss:
        min_lap = min(min_lap, b[BOSS_LAP_NO_KEY])

    return min_lap

# 周から段階を取得
def get_phase(data, lap_no):
    l = data[DATA_CONFIG_KEY][CONFIG_PHASE_KEY]

    for i in range(0, len(l)):
        if lap_no < l[i]:
            return i

    return len(l)

# 凸可能な周の最大値を算出
def get_max_attack_lap_no(data):
    l = data[DATA_CONFIG_KEY][CONFIG_PHASE_KEY]

    min_lap = get_min_lap_no(data)
    phase = get_phase(data, min_lap)

    if phase == len(l):
        return min_lap+1
    
    return min(min_lap+1, l[phase]-1)



#日次予約情報を初期化
def init_daily(data):

    new_daily = {}
    
    #現在日付を取得し格納
    new_daily[DAILY_DATE_KEY] = get_date(datetime.datetime.now()).isoformat()
    new_daily[DAILY_MEMBER_KEY] = {}
    save_daily(new_daily)

    data[DATA_DAILY_KEY] = new_daily

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

# 予約情報を周、ボスごとに集計しなおし、登録時間でソートしたデータを生成
def generate_reservation_dict(data):
    def datetime_compare(d):
        return datetime.datetime.fromisoformat(d[RESERVATION_DATETIME_KEY])

    dic = {}

    # 登録メンバのみを抽出
    member_list = data[DATA_MEMBER_KEY]

    for m in member_list:
        member_id = m[MEMBER_ID_KEY]
        member_key = str(member_id)

        daily_member = data[DATA_DAILY_KEY][DAILY_MEMBER_KEY]

        if member_key in daily_member:
            res_list = daily_member[member_key][DAILY_MEMBER_RESERVATION_KEY]

            for i in range(0, len(res_list)):
                for j in range(0, len(res_list[i])):
                    res = res_list[i][j]

                    if res[RESERVATION_STATUS_KEY] == RESERVE_STATUS_RESERVED:
                        new_res = dict(res)
                        new_res[RESERVATION_ID_KEY] = member_id
                        new_res[RESERVATION_SEQ_KEY] = i
                        new_res[RESERVATION_BRANCH_KEY] = j

                        lap_no = new_res[RESERVATION_LAP_NO_KEY]
                        lap_key = str(lap_no)

                        if not lap_key in dic:
                            dic[lap_key] = []
                            for k in range(0,BOSS_MAX):
                                dic[lap_key].append([])

                        dic[lap_key][new_res[RESERVATION_BOSS_ID_KEY]].append(new_res)

    # 各辞書のエントリを時刻順に並び替える
    for key in dic:
        for k in range(0,BOSS_MAX):
            dic[lap_key][new_res[RESERVATION_BOSS_ID_KEY]].sort(key = datetime_compare)

    return dic

# 現在の予約の合計数を算出
def get_hp_sum(dic, lap_no, boss_id):
    lap_key = str(lap_no)

    if lap_key in dic:
        s=0

        for r in dic[lap_key][boss_id]:
            s += r[RESERVATION_DAMAGE_KEY]

        return s
    else:
        return 0


# 指定のボスの現在の周に予約をしているメンバにお知らせする
async def notice_reserving_member(data, guild, boss_id):
    dic = generate_reservation_dict(data)

    lap_no = data[DATA_BOSS_KEY][boss_id][BOSS_LAP_NO_KEY]

    lap_key = str(lap_no)

    if lap_key in dic:
        res_list = dic[lap_key][boss_id]

        id_set = set()

        for res in res_list:
            id_set.add(res[RESERVATION_ID_KEY])
        
        if len(id_set) > 0:
            msg = ''

            channel = guild.get_channel(data[DATA_SERVER_KEY][SERVER_COMMAND_CHANNEL_KEY])

            for id in id_set:
                u = await guild.fetch_member(id)

                msg += f'{u.mention}'

            msg += f'{lap_no}周目 {data[DATA_BOSS_KEY][boss_id][BOSS_NAME_KEY]}'

            msg += messages.msg_notice_boss_change

            await channel.send(msg)



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

# ロックファイルを生成 失敗した場合はエラー
def create_lock():
    fp = open(DATA_LOCK_PATH, 'x', encoding="utf-8")
    fp.close()

# ロックファイルを削除
def delete_lock():
    os.remove(DATA_LOCK_PATH)

# ヘルプを読み込む
def load_help():
    fp = open(DATA_HELP_PATH, 'r', encoding="utf-8")

    help_str = fp.read()

    fp.close()

    return help_str
