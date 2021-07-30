import messages
import common

def cancel(command_args, mention_ids):
    try : 
        if len(command_args) != 3 :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        lb = common.convert_boss_no_with_lap_no(command_args[1])

        boss_id = lb[0]

        lap_no = lb[1]

        ca = common.convert_cancel_attack_no(command_args[2])

        attack_index = ca[0]

        cancel_flag = ca[1]

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_cancel_arg)

    return
