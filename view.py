import discord

import common

async def display_reservation(data, message):
    edit_str = ''

    boss = data[common.DATA_BOSS_KEY]

    min_lap = 9999

    for b in boss:
        min_lap = min(min_lap, b[common.BOSS_LAP_NO_KEY])

    for l in range(min_lap, min_lap + 2):
        edit_str += f'■{l}周目\n'
        for b in boss:
            if l < b[common.BOSS_LAP_NO_KEY] or (l == b[common.BOSS_LAP_NO_KEY] and b[common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED):
                edit_str += f'{b[common.BOSS_NAME_KEY]} 討伐済\n'    
            elif l == b[common.BOSS_LAP_NO_KEY]:
                edit_str += f'{b[common.BOSS_NAME_KEY]} {b[common.BOSS_HP_KEY]}/{b[common.BOSS_MAX_HP_KEY]}\n'
            else:
                edit_str += f'{b[common.BOSS_NAME_KEY]} 未登場\n'

        edit_str += f'\n'

    await message.edit(content = edit_str)

    return

async def display_rest_detail(data, message):
    await message.edit(content = 'ざんとつ　編集')

    return