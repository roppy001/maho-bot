import messages
import common

def la(command_args, mention_ids):
    try : 
        if len(command_args) != 4 :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        boss_id = common.convert_boss_no(command_args[1])

        attack_index = common.convert_attack_no(command_args[2])

        carry_over = common.convert_carry_over(command_args[3])

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_la_arg)

    return
