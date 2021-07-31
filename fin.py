import messages
import common

def fin(data, command_args, mention_ids):
    try : 
        if len(command_args) != 3 :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        boss_id = common.convert_boss_no(command_args[1])

        da = common.convert_damage_with_attack_no(command_args[2])

        damage = da[0]

        attack_index = da[1]

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_fin_arg)

    return
