# 組み込み
import os
import json
import re
import datetime

# 追加インストール
import discord

# mahobot関連
import messages
import common
import reserve
import fin
import la
import cancel
import ms
import manage
import view

client = discord.Client()

BOT_TOKEN=os.getenv('BOT_TOKEN')

OK_HAND = '\N{OK HAND SIGN}'

async def shutdown(message , data, command_args, mention_ids):
    await message.add_reaction(OK_HAND)
    await client.logout()
    return (True,'')

## コマンド
COMMAND_LIST = [
    (['.reserve', '.re', '.予約'], reserve.reserve, True),
    (['.finish', '.fin', '.完了'], fin.fin, True),
    (['.lastattack', '.la', '.討伐'], la.la, True),
    (['.cancel', '.cl', '.取消'], cancel.cancel, True),
    (['.modifystatus', '.ms', '.ステータス変更'], ms.ms, True),
    (['.add', '.追加'], manage.add, False),
    (['.remove', '.削除'], manage.remove, False),
    (['.modifyboss', '.mb', '.ボス変更'], manage.mb, False),
    (['.shutdown'], shutdown, False),
    (['.kickbot'], manage.kickbot, False)
    ]

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    return

# 発言時に実行されるイベントハンドラを定義
@client.event
async def on_message(message):    
    # .で始まらない場合はコマンドではないので無視する
    if not message.content.startswith('.') :
        return

    try:
        common.create_lock()
    except:
        await common.reply_author(message, messages.error_lock)
        return
    
    try:
        await command_main(message)
    finally:
        common.delete_lock()
    
    return


async def command_main(message):
    data = dict()

    await recreate_channels_if_not_exist(data, message.guild)

    data[common.DATA_CONFIG_KEY] = common.load_config()
    
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    # コマンド入力チャンネルではない場合は無視する
    if not message.channel.id in [data[common.DATA_SERVER_KEY][common.SERVER_COMMAND_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]]:
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

    # 日次予約情報を取得
    try:
        data[common.DATA_DAILY_KEY] = common.load_daily()

        # 5時をまたいだ場合は初期化する
        if datetime.date.fromisoformat(data[common.DATA_DAILY_KEY][common.DAILY_DATE_KEY]) < common.get_date(datetime.datetime.now()):
            common.init_daily(data)
            await common.reply_author(message, messages.msg_new_daily)

    except FileNotFoundError:
        common.init_daily(data)


    # メンションの全IDを取得
    mention_re = re.compile('<@!\d+>')
    mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]

    if len(mention_ids) > 0 and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]) and data[common.DATA_CONFIG_KEY][common.CONFIG_DEPUTY_LIMITED_KEY]:
        await common.reply_author(message, messages.error_mention_limited)
        return 


    mention_match = mention_re.search(message.content)
    if mention_match:
        command_str = message.content[:mention_match.start(0)]
    else :
        command_str = message.content

    # メンションを文字列から削除したのち、空白でコマンドを分割
    command_args = re.split('\s+', command_str.replace('　',' ').strip(), 3)

    # コマンド部分は英字大文字を小文字に置き換える
    command_args[0] = str.lower(command_args[0])

    # IDが0個の場合はメッセージ送信者のIDを追加する
    if len(mention_ids)==0 :
        mention_ids.append(message.author.id)

    ref = (False,'')

    try:
        flg = True
        for c in COMMAND_LIST :
            if command_args[0] in c[0] :
                if (not c[2]) and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]):
                    raise common.CommandError(messages.error_command_limited)

                ref = await c[1](message, data, command_args, mention_ids)
                await message.add_reaction(OK_HAND)
                flg = False
                break
        
        if flg:
            await common.reply_author(message, messages.error_cmd_none)
            return
        
    except common.CommandError as ce :
        await common.reply_author(message, ce.args[0])
        return
    
    reservation_message = await fetch_reservation_message(data, message.guild)

    rest_detail_message = await fetch_rest_detail_message(data, message.guild)

    await set_help_message(data, message.guild)

    if ref[0]:
        await view.display_reservation(data, reservation_message)
        await view.display_rest_detail(data, rest_detail_message)

    if ref[1] != '':
        await common.reply_author(message, ref[1])

    return

@client.event
async def on_guild_join(guild):
    data = dict()
    await create_bot_channels(data, guild) 
    return

# bot用のチャンネルを生成
async def create_bot_channels(data, guild):
    category_channel      = await guild.create_category_channel('マホBOT')
    command_channel       = await guild.create_text_channel('コマンド入力',category = category_channel )
    admin_command_channel = await guild.create_text_channel('管理コマンド入力',category = category_channel )
    reservation_channel   = await guild.create_text_channel('予約状況表示',category = category_channel )
    rest_detail_channel   = await guild.create_text_channel('残凸状況表示',category = category_channel )
    help_channel          = await guild.create_text_channel('コマンドヘルプ',category = category_channel )

    server_setting = {
        common.SERVER_GUILD_ID_KEY : guild.id,
        common.SERVER_CATEGORY_CHANNEL_KEY : category_channel.id,
        common.SERVER_COMMAND_CHANNEL_KEY : command_channel.id,
        common.SERVER_ADMIN_COMMAND_CHANNEL_KEY : admin_command_channel.id,
        common.SERVER_RESERVATION_CHANNEL_KEY : reservation_channel.id,
        common.SERVER_REST_DETAIL_CHANNEL_KEY : rest_detail_channel.id,
        common.SERVER_HELP_CHANNEL_KEY : help_channel.id
    }

    data[common.DATA_SERVER_KEY] = server_setting

    common.save_server_settings(data[common.DATA_SERVER_KEY])

    return

# 設定ファイルが無い場合は、チャンネルを新たに生成
async def recreate_channels_if_not_exist(data, guild):
    if(not os.path.exists(common.DATA_SERVER_PATH)) :
        await create_bot_channels(data, guild)

    return

# 予約表示用メッセージを取得
async def fetch_reservation_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_RESERVATION_CHANNEL_KEY])

    if (not common.SERVER_RESERVATION_MESSAGE_KEY in server):
        message = await channel.send('よやく')
        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_RESERVATION_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('よやく')
        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# 残凸表示用メッセージを取得
async def fetch_rest_detail_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_REST_DETAIL_CHANNEL_KEY])

    if (not common.SERVER_REST_DETAIL_MESSAGE_KEY in server):
        message = await channel.send('ざんとつ')
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_REST_DETAIL_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('ざんとつ')
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# ヘルプメッセージを取得
async def set_help_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_HELP_CHANNEL_KEY])

    if (not common.SERVER_HELP_MESSAGE_KEY in server):
        message = await channel.send(common.load_help())
        message_id = message.id
        server[common.SERVER_HELP_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_HELP_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send(common.load_help())
        message_id = message.id
        server[common.SERVER_HELP_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# Botの起動とDiscordサーバーへの接続
client.run(BOT_TOKEN)