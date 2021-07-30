import messages
import common

def reserve(command_args, mention_ids):
    try : 
        if not (len(command_args) in [3,4]) :
            raise common.CommandError(messages.error_args)

        # 引数のチェックと変換
        target_id = common.get_target_id(mention_ids)

        lb = common.convert_boss_no_with_lap_no(command_args[1])

        boss_id = lb[0]

        lap_no = lb[1]

        da = common.convert_damage_with_attack_no(command_args[2])

        damage = da[0]

        attack_index = da[1]

        comment = ''

        if len(command_args) == 4:
            comment = command_args[3]



    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_re_arg)

    return




