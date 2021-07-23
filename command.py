
# インストールした discord.py を読み込む
import os
import json
import discord
from datetime import datetime
import mojimoji
import common

BOT_TOKEN=os.getenv('BOT_TOKEN')

GUILD_ID_KEY = 'guild_id'
CATEGORY_CHANNEL_KEY = 'category_channel'
COMMAND_CHANNEL_KEY = 'command_channel'
RESERVATION_CHANNEL_KEY = 'reservation_channel'
REST_DETAIL_CHANNEL_KEY = 'rest_detail_channel'

SERVER_TEXT_PATH = 'data/server.txt'

ok_hand = "👌"

## 一般コマンド

# 予約コマンド
reserve_cmd_list = ['.reserve', '.re', '.予約']

# 凸完了コマンド
fin_cmd_list = ['.finish', '.fin', '.完了']

# 討伐登録コマンド
la_cmd_list = ['.lastattack', '.la', '.討伐']

# キャンセルコマンド
cancel_cmd_list = ['.cancel', '.取消']

# ステータス変更コマンド
mod_cmd_list = ['.modifystatus', '.ms', '.状態変更']


## 管理用コマンド

# ボス周変更コマンド
modifyboss_cmd_list = ['.modifyboss']
cancelboss_cmd_list = ['.cancelboss']

# エラー文言
error_re_arg = '正しい引数を入力してください。\n.reserve 周 ボス番号 何凸目か コメント\n(例: .reserve 12 3 1 物理1200)'
error_fin_arg = '正しい引数を入力してください。\n.fin ボス番号 何凸目か 実績ダメージ(万単位)\n(例: .fin 5 1 1800)'
error_la_arg = '正しい引数を入力してください。\n.la ボス番号 何凸目か 持ち越し秒数\n(例: .la 3 2 29)'
error_boss_no = 'ボス番号は1~5を入力してください'
error_laps = '周の指定が正しくありません'
error_assault = '「何凸目か」は1~3を入力してください'
error_damage = 'ダメージは数値を入力してください'
error_over = '持ち越し秒数は21~90の範囲で入力してください'
error_cmd_none = '正しいコマンドを入力してください'
error_multi_mention = '複数のメンションが付けられています。'

client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    return

# 発言時に実行されるイベントハンドラを定義
@client.event
async def on_message(message):
    # await message.guild.leave()
    # return

    await recreate_channels_if_not_exist(message.guild)

    server_setting = load_server_settings()

    # .で始まる場合はコマンドなので処理を行う。
    if message.content.startswith('.'):
        # コマンドを認識できる形に変換 & 分割して格納する
        argument_list = convert_cmd(message.content)
    else:
    # コマンド以外の場合は処理しない
        return

    # 引数無しの場合は処理しない
    #if len(argument_list) == 1:
    #    return

    # 代行入力のチェック
    instead = check_instead_cmd(argument_list)
    print(instead)

    # 0 : 代行入力 1 : 複数メンションエラー 2:代行無し
    if instead == 0:
        # TODO:管理者用コマンドは権限のチェックを入れる
        target_id = argument_list[-1].replace('<@!', '').replace('>', '')
        print(target_id)
        # 代行入力するメンバーのIDを取得したらargument_listからメンション部分を削除する
        argument_list.pop(-1)
    elif instead == 1:
        reply = f'{message.author.mention} {error_multi_mention}'
        await message.channel.send(reply)
        return
    else :
        # 代行入力無しなら特に何もしない
        target_id = message.author.id

    print(argument_list)

    ## コマンドの振り分け

    # 予約コマンド
    if argument_list[0] in reserve_cmd_list:
        check_result = check_reserve_cmd(argument_list)
        if check_result == 0:
            # コマンドチェックOKならリアクションを付ける
            await message.add_reaction(ok_hand)
            # TODO:予約コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{argument_list}　ターゲット:{target_id}'
            await message.channel.send(reply)
            # ここまでデバッグ用
            return
        elif check_result == 1:
            # コマンドチェックNGなら使い方を表示する
            reply()
            reply = f'{message.author.mention} {error_re_arg}'
            await message.channel.send(reply)
            return
        elif check_result == 2:
            reply = f'{message.author.mention} {error_laps}'
            await message.channel.send(reply)
            return
        elif check_result == 3:
            reply = f'{message.author.mention} {error_boss_no}'
            await message.channel.send(reply)
            return
        elif check_result == 4:
            reply = f'{message.author.mention} {error_assault}'
            await message.channel.send(reply)
            return
    # 凸完了コマンド
    elif argument_list[0] in fin_cmd_list:
        check_result = check_cmd_fin(argument_list)
        if check_result == 0:
            await message.add_reaction(ok_hand)
            # TODO:凸完了コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{argument_list}　ターゲット:{target_id}'
            await message.channel.send(reply)
            # ここまでデバッグ用
            return
        elif check_result == 1:
            reply = f'{message.author.mention} {error_fin_arg}'
            await message.channel.send(reply)
            return
        elif check_result == 2:
            reply = f'{message.author.mention} {error_boss_no}'
            await message.channel.send(reply)
            return
        elif check_result == 3:
            reply = f'{message.author.mention} {error_assault}'
            await message.channel.send(reply)
            return
        elif check_result == 4:
            reply = f'{message.author.mention} {error_damage}'
            await message.channel.send(reply)
            return
        return
    # 討伐登録コマンド
    elif argument_list[0] in la_cmd_list:
        check_result = check_cmd_la(argument_list)
        if check_result == 0:
            await message.add_reaction(ok_hand)
            # TODO:討伐登録コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{argument_list}　ターゲット:{target_id}'
            await message.channel.send(reply)
            # ここまでデバッグ用
            return
        elif check_result == 1:
            reply = f'{message.author.mention} {error_la_arg}'
            await message.channel.send(reply)
            return
        elif check_result == 2:
            reply = f'{message.author.mention} {error_boss_no}'
            await message.channel.send(reply)
            return
        elif check_result == 3:
            reply = f'{message.author.mention} {error_assault}'
            await message.channel.send(reply)
            return
        elif check_result == 4:
            reply = f'{message.author.mention} {error_over}'
            await message.channel.send(reply)
            return
        return
    elif argument_list[0] in cancel_cmd_list:
        return
    elif argument_list[0] in mod_cmd_list:
        return
    elif argument_list[0] in modifyboss_cmd_list:
        # 管理者用コマンドは権限のチェックを入れる
        return
    elif argument_list[0] in cancelboss_cmd_list:
        # 管理者用コマンドは権限のチェックを入れる
        return
    else:
        #コマンドリストにないのでエラーを表示する
        reply = f'{message.author.mention} {error_cmd_none}'
        await message.channel.send(reply)
        return

# 返信する非同期関数を定義
async def reply(message, words):
    reply = f'{message.author.mention}{words}'
    await message.channel.send(reply)

def convert_cmd(message):
    # 全角スペースを半角スペースに変換して半角スペース区切りで配列に入れる
    argument_list = message.replace("　"," ").replace("   "," ").replace("  "," ").split(" ")
    # 文末にスペースが入ってる場合には取り除く
    if len(argument_list[-1]) == 0:
        argument_list.pop(-1)
    # 大文字から小文字に変換
    argument_list = list(map(str.lower, argument_list))
    # 全角から半角に変換
    argument_list = list(map(mojimoji.zen_to_han, argument_list))

    return argument_list

def common_check_cmd(argument_list):
    return

# 代行入力のチェック
def check_instead_cmd(argument_list):
    if argument_list[-1].startswith('<@!'):
        if len(argument_list[-1].split("<@!"))>2:
            return 1
        if argument_list[-2].startswith('<@!'):
            return 1
        else:
            return 0
    else:
        return 2

# .reserve 周 ボス番号 何凸目か コメント
# result : 0 : チェックOK
def check_reserve_cmd(argument_list):
    # 引数の数をチェック
    if len(argument_list) < 4 or 5 < len(argument_list):
        return 1
    # 周のチェック
    if not common.check_laps(argument_list[1]):
        return 2
    # ボス番号のチェック
    if not common.check_boss_no(argument_list[2]):
        return 3
    # 何凸目かのチェック
    if not common.check_assault(argument_list[3]):
        return 4
    return 0

def check_cmd_fin(argument_list):
    if len(argument_list) < 4:
        return 1
    if not common.check_boss_no(argument_list[1]):
        return 2
    if not common.check_assault(argument_list[2]):
        return 3
    if not common.check_damage(argument_list[3]):
        return 4
    return 0

def check_cmd_la(argument_list):
    if len(argument_list) < 4:
        return 1
    if not common.check_boss_no(argument_list[1]):
        return 2
    if not common.check_assault(argument_list[2]):
        return 3
    if not common.check_over(argument_list[3]):
        return 4
    return 0

def check_cmd_cancel(argument_list):
    result = 1
    if len(argument_list) < 4:
        result = 0
        return result
    return




@client.event
async def on_guild_join(guild):
    await create_bot_channels(guild) 
    return

async def create_bot_channels(guild):
    category_channel    : discord.CategoryChannel = await guild.create_category_channel('マホBOT')
    command_channel     : discord.TextChannel     = await guild.create_text_channel('コマンド入力',category = category_channel )
    reservation_channel : discord.TextChannel     = await guild.create_text_channel('予約状況表示',category = category_channel )
    rest_detail_channel : discord.TextChannel     = await guild.create_text_channel('残凸状況表示',category = category_channel )

    server_setting = {
        GUILD_ID_KEY : guild.id,
        CATEGORY_CHANNEL_KEY : category_channel.id,
        COMMAND_CHANNEL_KEY : command_channel.id,
        RESERVATION_CHANNEL_KEY : reservation_channel.id,
        REST_DETAIL_CHANNEL_KEY : rest_detail_channel.id
    }

    fp = open(SERVER_TEXT_PATH, 'w')

    json.dump(server_setting, fp, indent=4)

    fp.close()

    return

async def recreate_channels_if_not_exist(guild):
    if(not os.path.exists(SERVER_TEXT_PATH)) :
        await create_bot_channels(guild)

    return


def load_server_settings():
    fp = open(SERVER_TEXT_PATH, 'r')

    server_setting =json.load(fp)

    fp.close()

    return server_setting


# 60秒に一回ループ
#@tasks.loop(seconds=60)
#async def loop():

#ループ処理実行
#loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(BOT_TOKEN)