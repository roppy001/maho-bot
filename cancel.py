import messages
import common

async def cancel(message, data, command_args, mention_ids):
    try : 
        # if len(command_args) != 3 :
        #     raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        # lb = common.convert_boss_no_with_lap_no(command_args[1])

        # boss_id = lb[0]

        # lap_no = lb[1]

        # ca = common.convert_cancel_attack_no(command_args[2])

        # attack_index = ca[0]

        # cancel_flag = ca[1]

        if len(command_args) != 1 :
            raise common.CommandError(messages.error_args)
        
        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            daily[common.DAILY_MEMBER_KEY][target_key] = common.create_daily_member()

        # 予約をすべて削除
        daily[common.DAILY_MEMBER_KEY][target_key][common.DAILY_MEMBER_RESERVATION_KEY] = []

        data[common.DATA_DAILY_KEY] = daily

        common.save_daily(daily)

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_cancel_arg)

    return (True,'')
