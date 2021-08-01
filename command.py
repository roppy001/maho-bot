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
import member

BOT_TOKEN=os.getenv('BOT_TOKEN')

ok_hand = "👌"
data = dict()

## コマンド
COMMAND_LIST = [
    (['.reserve', '.re', '.予約'], reserve.reserve),
    (['.finish', '.fin', '.完了'], fin.fin),
    (['.lastattack', '.la', '.討伐'], la.la),
    (['.cancel', '.cl', '.取消'], cancel.cancel),
    (['.add', '.追加'], member.add),
    (['.remove', '.削除'], member.remove)
    ]

# ボス周変更コマンド
# modifyboss_cmd_list = ['.modifyboss']
# cancelboss_cmd_list = ['.cancelboss']

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

    data[common.DATA_CONFIG_KEY] = common.load_config()
    
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    # .で始まらない場合はコマンドではないので無視する
    if not message.content.startswith('.') :
        return

    # コマンド入力チャンネルではない場合は無視する
    if message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_COMMAND_CHANNEL_KEY] :
        return

    # メンバ情報を取得
    try:
        data[common.DATA_MEMBER_KEY] = common.load_members()
    except FileNotFoundError:
        await common.reply_author(message, messages.error_init_member)
        data[common.DATA_MEMBER_KEY] = []
        common.save_members(data[common.DATA_MEMBER_KEY])

    # ボス情報を取得
    try:
        data[common.DATA_BOSS_KEY] = common.load_boss()
    except FileNotFoundError:
        common.init_boss(data)

    # メンションの全IDを取得
    mention_re = re.compile('<@!\d+>')
    mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]

    mention_match = mention_re.search(message.content)
    if mention_match:
        command_str = message.content[:mention_match.start(0)]
    else :
        command_str = message.content

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
                c[1](data, command_args, mention_ids)
                await message.add_reaction(ok_hand)
                return
        
    except common.CommandError as ce :
        await common.reply_author(message, ce.args[0])
        return

    await common.reply_author(message, messages.error_cmd_none)
    return

@client.event
async def on_guild_join(guild):
    await create_bot_channels(guild) 
    return

async def create_bot_channels(guild):
    category_channel    = await guild.create_category_channel('マホBOT')
    command_channel     = await guild.create_text_channel('コマンド入力',category = category_channel )
    reservation_channel = await guild.create_text_channel('予約状況表示',category = category_channel )
    rest_detail_channel = await guild.create_text_channel('残凸状況表示',category = category_channel )

    server_setting = {
        common.SERVER_GUILD_ID_KEY : guild.id,
        common.SERVER_CATEGORY_CHANNEL_KEY : category_channel.id,
        common.SERVER_COMMAND_CHANNEL_KEY : command_channel.id,
        common.SERVER_RESERVATION_CHANNEL_KEY : reservation_channel.id,
        common.SERVER_REST_DETAIL_CHANNEL_KEY : rest_detail_channel.id
    }

    data[common.DATA_SERVER_KEY] = server_setting

    common.save_server_settings(data[common.DATA_SERVER_KEY])

    return

async def recreate_channels_if_not_exist(guild):
    if(not os.path.exists(common.DATA_SERVER_PATH)) :
        await create_bot_channels(guild)

    return


# 60秒に一回ループ
#@tasks.loop(seconds=60)
#async def loop():

#ループ処理実行
#loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(BOT_TOKEN)