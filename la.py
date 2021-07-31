import messages
import common

def la(data, command_args, mention_ids):
    try: 
        if len(command_args) != 3:
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        boss_id = common.convert_boss_no(command_args[1])

        da = common.convert_carry_over_with_attack_no(command_args[2])

        carry_over = da[0]

        attack_index = da[1]

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_la_arg)

    return
