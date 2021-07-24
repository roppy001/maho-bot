# 組み込み
import os
import json
import re
from datetime import datetime

# 追加インストール
import discord

# mahobot関連
import messages
import common
import reserve
import fin
import la
import cancel

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

COMMAND_LIST = [(['.reserve', '.re', '.予約'], reserve.reserve)]


## 管理用コマンド

# ボス周変更コマンド
modifyboss_cmd_list = ['.modifyboss']
cancelboss_cmd_list = ['.cancelboss']

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

    # .で始まらない場合はコマンドではないので無視する
    if not message.content.startswith('.') :
        return

    # コマンド入力チャンネルではない場合は無視する
    if message.channel.id != server_setting.get(COMMAND_CHANNEL_KEY) :
        return

    # メンションの全IDを取得
    mention_re = re.compile('<@!\d+>')
    mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]

    mention_match = mention_re.search(message.content)
    if mention_match:
        command_str = message.content[:mention_match.start(0)]
    else :
        command_str = message.content

    print(command_str)

    # メンションを文字列から削除したのち、空白でコマンドを分割
    command_args = re.split('\s+', command_str.replace('　',' ').strip() )

    # コマンド部分は英字大文字を小文字に置き換える
    command_args[0] = str.lower(command_args[0])

    # IDが0個の場合はメッセージ送信者のIDを追加する
    if len(mention_ids)==0 :
        mention_ids.append(message.author.id)

    try:
        for c in COMMAND_LIST :
            if command_args[0] in c[0] :
                c[1](command_args, mention_ids)
                await message.add_reaction(ok_hand)
                return
        
    except common.CommandError as ce :
        await common.reply_author(message, ce.args[0])
        return

    await common.reply_author(message, messages.error_cmd_none)
    return

    # 予約コマンド
    if command_args[0] in reserve_cmd_list:
        check_result = check_reserve_cmd(command_args)
        if check_result == 0:
            # コマンドチェックOKならリアクションを付ける
            await message.add_reaction(ok_hand)
            # TODO:予約コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{command_args}　ターゲット:{target_id}'
            await message.channel.send(reply)
            # ここまでデバッグ用
            return
        elif check_result == 1:
            # コマンドチェックNGなら使い方を表示する
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
    elif command_args[0] in fin_cmd_list:
        check_result = check_cmd_fin(command_args)
        if check_result == 0:
            await message.add_reaction(ok_hand)
            # TODO:凸完了コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{command_args}　ターゲット:{target_id}'
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
    elif command_args[0] in la_cmd_list:
        check_result = check_cmd_la(command_args)
        if check_result == 0:
            await message.add_reaction(ok_hand)
            # TODO:討伐登録コマンドの処理を入れる
            # デバッグ用コード
            reply = f'{message.author.mention} 引数リスト：{command_args}　ターゲット:{target_id}'
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
    elif command_args[0] in cancel_cmd_list:
        return
    elif command_args[0] in mod_cmd_list:
        return
    elif command_args[0] in modifyboss_cmd_list:
        # 管理者用コマンドは権限のチェックを入れる
        return
    elif command_args[0] in cancelboss_cmd_list:
        # 管理者用コマンドは権限のチェックを入れる
        return
    else:
        #コマンドリストにないのでエラーを表示する
        reply = f'{message.author.mention} {error_cmd_none}'
        await message.channel.send(reply)
        return


# .reserve 周 ボス番号 何凸目か コメント
# result : 0 : チェックOK
def check_reserve_cmd(command_args):
    # 引数の数をチェック
    if len(command_args) < 4 or 5 < len(command_args):
        return 1
    # 周のチェック
    if not common.check_laps(command_args[1]):
        return 2
    # ボス番号のチェック
    if not common.check_boss_no(command_args[2]):
        return 3
    # 何凸目かのチェック
    if not common.check_assault(command_args[3]):
        return 4
    return 0

def check_cmd_fin(command_args):
    if len(command_args) < 4:
        return 1
    if not common.check_boss_no(command_args[1]):
        return 2
    if not common.check_assault(command_args[2]):
        return 3
    if not common.check_damage(command_args[3]):
        return 4
    return 0

def check_cmd_la(command_args):
    if len(command_args) < 4:
        return 1
    if not common.check_boss_no(command_args[1]):
        return 2
    if not common.check_assault(command_args[2]):
        return 3
    if not common.check_over(command_args[3]):
        return 4
    return 0

def check_cmd_cancel(command_args):
    result = 1
    if len(command_args) < 4:
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