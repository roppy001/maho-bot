import messages
import common


def add(data, command_args, mention_ids):
    try: 
        if len(command_args) != 1:
            raise common.CommandError(messages.error_args)

        members = data[common.DATA_MEMBER_KEY]

        for m in mention_ids:
            flg = True
            for s in members:
                if m == s[common.MEMBER_ID_KEY]:
                    flg = False
        
            if flg:
                e = dict()
                e[common.MEMBER_ID_KEY] = m
                members.append(e)
        
        common.save_members(members)
        data[common.DATA_MEMBER_KEY] = members

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_add_arg)

    return (True,'')

def remove(data, command_args, mention_ids):
    try: 
        if len(command_args) != 1:
            raise common.CommandError(messages.error_args)

        new_members = []

        for s in data[common.DATA_MEMBER_KEY]:
            flg = True
            for m in mention_ids:
                if m == s[common.MEMBER_ID_KEY]:
                    flg = False

            if flg:
                new_members.append(s)
        
        common.save_members(new_members)
        data[common.DATA_MEMBER_KEY] = new_members

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_add_arg)

    return (True,'')
