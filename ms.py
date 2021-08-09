import messages
import common

async def ms(message, data, command_args, mention_ids):
    msg = ''

    try : 
        if not len(command_args) in [1,2]:
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            daily[common.DAILY_MEMBER_KEY][target_key] = common.create_daily_member()

        member = daily[common.DAILY_MEMBER_KEY][target_key]

        atk = member[common.DAILY_MEMBER_ATTACK_KEY]

        # 現在のステータスを返却
        if len(command_args) == 1 :
            msg += get_status_str(atk)

            return (True, msg)

        status = common.convert_status(command_args[1])

        # ステータス変更
        for i in range(0, len(status)):
            atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] = status[i]

        member[common.DAILY_MEMBER_ATTACK_KEY] = atk 
        
        # 予約をすべて削除
        member[common.DAILY_MEMBER_RESERVATION_KEY] = []

        daily[common.DAILY_MEMBER_KEY][target_key] = member

        # 予約をすべて削除
        daily[common.DAILY_MEMBER_KEY][target_key][common.DAILY_MEMBER_RESERVATION_KEY] = []

        data[common.DATA_DAILY_KEY] = daily

        common.save_daily(daily)

        msg += f'{get_status_str(atk)}{messages.msg_ms_success}'

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_ms_arg)

    return (True, msg)

def get_status_str(atk):
    result = ''

    for i in range(0, len(atk)):
        result += f'{i+1}{messages.word_atk_index}{messages.word_atk_status[atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY]]} '
    
    return result
