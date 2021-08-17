import discord

import common
import messages

async def display_reservation(data, message):
    summary = get_summary(data)

    edit_str = f'**■ 凸状況 {summary[0]}/{summary[1]} 持越合計{summary[2]}**\n\n'

    min_lap = common.get_min_lap_no(data)

    dic = common.generate_reservation_dict(data)

    boss = data[common.DATA_BOSS_KEY]

    for l in range(min_lap, min_lap + max(data[common.DATA_CONFIG_KEY][common.CONFIG_RESERVATION_LIMIT_KEY], 1) + 1):
        if not str(l) in dic and l >= min_lap + 2:
            continue

        phase = common.get_phase(data, l)

        edit_str += f'**■{l}周目 {phase+1}段階目**\n'
        for boss_id in range(0, common.BOSS_MAX):
            b = boss[boss_id]
            if l < b[common.BOSS_LAP_NO_KEY] or (l == b[common.BOSS_LAP_NO_KEY] and b[common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED):
                edit_str += f'~~● {b[common.BOSS_NAME_KEY]} 討伐済~~\n'
            elif l == b[common.BOSS_LAP_NO_KEY]:
                if b[common.BOSS_HP_KEY] > common.get_hp_sum(dic, l, boss_id):
                    h = '\N{LARGE GREEN CIRCLE}'
                else:
                    h = '\N{LARGE ORANGE CIRCLE}'

                edit_str += f'{h} {b[common.BOSS_NAME_KEY]} {b[common.BOSS_HP_KEY]}万/{b[common.BOSS_MAX_HP_KEY]}万\n'
                edit_str += await get_reservation_str(data, message, dic, l, boss_id)
            else:
                edit_str += f'\N{LARGE BLUE CIRCLE} {b[common.BOSS_NAME_KEY]} 未登場\n'
                edit_str += await get_reservation_str(data, message, dic, l, boss_id)

        edit_str += f'\n'

    # 周未指定予約の表示
    if '0' in dic:
        edit_str += '**■周未指定予約**\n'
        for boss_id in range(0, common.BOSS_MAX):
            b = boss[boss_id]
            edit_str += f'● {b[common.BOSS_NAME_KEY]} \n'
            edit_str += await get_reservation_str(data, message, dic, 0, boss_id)
        edit_str += '\n'

    await message.edit(content = edit_str)

    return

async def get_reservation_str(data, message, dic, lap_no, boss_id):
    lap_key = str(lap_no)

    if not lap_key in dic:
        return ''
    
    s = ''

    res_list = dic[lap_key][boss_id]

    for res in res_list:
        s += f'　{res[common.RESERVATION_DAMAGE_KEY]}万 { res[common.RESERVATION_NAME_KEY] } {res[common.RESERVATION_COMMENT_KEY]} {res[common.RESERVATION_SEQ_KEY]+1}{messages.word_atk_index}{messages.word_atk_branch[res[common.RESERVATION_BRANCH_KEY]]}\n'

    return s

def get_summary(data):
    # 登録メンバのみを抽出
    member_list = data[common.DATA_MEMBER_KEY]

    atk_sum_max = len(member_list) * common.ATTACK_MAX
    atk_sum = 0
    carry_sum = 0

    for m in member_list:
        member_id = m[common.MEMBER_ID_KEY]
        member_key = str(member_id)

        daily_member = data[common.DATA_DAILY_KEY][common.DAILY_MEMBER_KEY]

        if member_key in daily_member:
            atk = daily_member[member_key][common.DAILY_MEMBER_ATTACK_KEY]

            for i in range(0, len(atk)):
                s = atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY]
                if s == common.DAILY_ATTACK_STATUS_DONE:
                    atk_sum += 1
                elif s == common.DAILY_ATTACK_STATUS_CARRY_OVER:
                    carry_sum += 1

    return (atk_sum, atk_sum_max, carry_sum)

async def display_rest_detail(data, message):
    summary = get_summary(data)

    msg = f'**■ 凸状況 {summary[0]}/{summary[1]} 持越合計{summary[2]}**\n\n'

    # 登録メンバのみを抽出
    member_list = data[common.DATA_MEMBER_KEY]

    for m in member_list:
        member_id = m[common.MEMBER_ID_KEY]
        member_key = str(member_id)

        daily_member = data[common.DATA_DAILY_KEY][common.DAILY_MEMBER_KEY]

        if member_key in daily_member:
            atk = daily_member[member_key][common.DAILY_MEMBER_ATTACK_KEY]
        else:
            atk = []
            for i in range(0, common.ATTACK_MAX):
                f = {}
                f[common.DAILY_MEMBER_ATTACK_STATUS_KEY] = common.DAILY_ATTACK_STATUS_NONE
                f[common.DAILY_MEMBER_ATTACK_CARRY_OVER_KEY] = 0
                atk.append(f)

        for i in range(0, len(atk)):
            msg += f'{messages.word_atk_status_mark[atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY]]} '

        msg += m[common.MEMBER_NAME_KEY] + '  '

        # 持越しを表示
        for i in range(0, len(atk)):
            if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_CARRY_OVER:
                c = atk[i][common.DAILY_MEMBER_ATTACK_CARRY_OVER_KEY]
                if c == 0:
                    msg += f'持越 '
                else: 
                    msg += f'{c}秒持越 '

        msg += '\n'

    await message.edit(content = msg)

    return