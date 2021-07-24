import messages
import common

def reserve(command_args, mention_ids):
    try : 
        if not (len(command_args) in [5,6]) :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        lap_no = common.convert_lap_no(command_args[1])

        boss_id = common.convert_boss_no(command_args[2])

        attack_index = common.convert_attack_no(command_args[3])

        damage = common.convert_damage(command_args[4])


    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_re_arg)

    return

