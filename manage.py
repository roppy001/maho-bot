import discord

import messages
import common


async def add(message, data, command_args, mention_ids):
    try: 
        if len(command_args) != 1:
            raise common.CommandError(messages.error_args)

        members = data[common.DATA_MEMBER_KEY]

        for m in mention_ids:
            flg = True

            # 名前を取得してキャッシュする
            try:
                u = await message.guild.fetch_member(m)
                if u:
                    name = u.display_name
                else:
                    flg = False
            except discord.NotFound:
                flg = False

            for s in members:
                if m == s[common.MEMBER_ID_KEY]:
                    flg = False
        
            if flg:
                e = dict()
                e[common.MEMBER_ID_KEY] = m
                e[common.MEMBER_NAME_KEY] = name
                members.append(e)

        if len(members) > common.MEMBER_MAX:
            raise common.CommandError(messages.error_add_impossible)
        
        common.save_members(members)
        data[common.DATA_MEMBER_KEY] = members

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_add_arg)

    return (True,'')

async def remove(message, data, command_args, mention_ids):
    try: 
        if len(command_args) != 1:
            raise common.CommandError(messages.error_args)

        new_members = []

        for s in data[common.DATA_MEMBER_KEY]:
            flg = True
            for m in mention_ids:
                if m == s[common.MEMBER_ID_KEY]:
                    flg = False

            # 脱退済みメンバかどうかをチェック 脱退済みの場合自動削除する
            try:
                u = await message.guild.fetch_member(s[common.MEMBER_ID_KEY])
                if u:
                    s[common.MEMBER_NAME_KEY] = u.display_name
            except discord.NotFound:
                flg = False

            if flg:
                new_members.append(s)
        
        common.save_members(new_members)
        data[common.DATA_MEMBER_KEY] = new_members

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_remove_arg)

    return (True,'')

async def mb(message, data, command_args, mention_ids):
    try : 
        if not len(command_args) in [3, 4] :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        boss_id = common.convert_boss_no(command_args[1])

        da = common.convert_lap_no_with_status(command_args[2])

        lap_no = da[0]
        boss_status = da[1]

        if lap_no == 0:
            raise common.CommandError(messages.error_lap_no)

        phase = common.get_phase(data, lap_no)
        data[common.DATA_BOSS_KEY][boss_id][common.BOSS_MAX_HP_KEY] = data[common.DATA_CONFIG_KEY][common.CONFIG_BOSS_KEY][boss_id][common.BOSS_MAX_HP_KEY][phase]
        if len(command_args) == 3:
            hp = data[common.DATA_BOSS_KEY][boss_id][common.BOSS_MAX_HP_KEY]
        else:
            hp = common.convert_damage(command_args[3])

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        # ボスの状態を変更
        data[common.DATA_BOSS_KEY][boss_id][common.BOSS_LAP_NO_KEY] = lap_no
        data[common.DATA_BOSS_KEY][boss_id][common.BOSS_STATUS_KEY] = boss_status
        data[common.DATA_BOSS_KEY][boss_id][common.BOSS_HP_KEY] = hp

        # 指定の周までの予約を周未指定予約に変更
        daily = data[common.DATA_DAILY_KEY]

        for key in daily[common.DAILY_MEMBER_KEY]:
            res_list = daily[common.DAILY_MEMBER_KEY][key][common.DAILY_MEMBER_RESERVATION_KEY]
            for i in range(0, len(res_list)):
                for j in range(0, len(res_list[i])):
                    r = res_list[i][j]
                    l = r[common.RESERVATION_LAP_NO_KEY]
                    bi = r[common.RESERVATION_BOSS_ID_KEY]
                    if boss_id == bi and ((l > 0 and l < lap_no) or (l == lap_no and boss_status == common.BOSS_STATUS_DEFEATED)):
                        daily[common.DAILY_MEMBER_KEY][key][common.DAILY_MEMBER_RESERVATION_KEY][i][j][common.RESERVATION_LAP_NO_KEY] = 0
        
        common.save_boss(data[common.DATA_BOSS_KEY])

        data[common.DATA_DAILY_KEY] = daily

        common.save_daily(daily)
    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_mb_arg)

    return (True, '')


async def kickbot(message, data, command_args, mention_ids):
    if len(command_args) != 1:
        raise common.CommandError(messages.error_args)
        
    await message.guild.leave()
    return (True,'')

