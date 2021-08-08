import discord

import common
import messages

async def display_reservation(data, message):
    edit_str = ''

    min_lap = common.get_min_lap_no(data)

    dic = common.generate_reservation_dict(data)

    boss = data[common.DATA_BOSS_KEY]

    for l in range(min_lap, min_lap + 2 + data[common.DATA_CONFIG_KEY][common.CONFIG_RESERVATION_LIMIT_KEY]):
        if not str(l) in dic and l >= min_lap + 2:
            continue

        edit_str += f'■{l}周目\n'
        for boss_id in range(0, common.BOSS_MAX):
            b = boss[boss_id]
            if l < b[common.BOSS_LAP_NO_KEY] or (l == b[common.BOSS_LAP_NO_KEY] and b[common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED):
                edit_str += f'{b[common.BOSS_NAME_KEY]} 討伐済\n'
            elif l == b[common.BOSS_LAP_NO_KEY]:
                edit_str += f'{b[common.BOSS_NAME_KEY]} {b[common.BOSS_HP_KEY]}/{b[common.BOSS_MAX_HP_KEY]}\n'
                edit_str += await get_reservation_str(data, message, dic, l, boss_id)
            else:
                edit_str += f'{b[common.BOSS_NAME_KEY]} 未登場\n'
                edit_str += await get_reservation_str(data, message, dic, l, boss_id)

        edit_str += f'\n'

    # 周未指定予約の表示
    if '0' in dic:
        edit_str += '■周未指定予約\n'
        for boss_id in range(0, common.BOSS_MAX):
            b = boss[boss_id]
            edit_str += await get_reservation_str(data, message, dic, l, boss_id)
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
        u = await message.guild.fetch_member(res[common.RESERVATION_ID_KEY])

        if u:
            name = u.name
        else:
            name = messages.word_name_unknown

        s += f'　{res[common.RESERVATION_DAMAGE_KEY]} {name} {res[common.RESERVATION_COMMENT_KEY]} {res[common.RESERVATION_SEQ_KEY]+1}{messages.word_atk_index}{messages.word_atk_branch[res[common.RESERVATION_BRANCH_KEY]]}\n'

    return s

async def display_rest_detail(data, message):
    await message.edit(content = 'ざんとつ　編集')

    return