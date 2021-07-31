from os import stat_result
import messages

class CommandError(Exception):
    pass

LAP_CURRENT = -1
LAP_NEXT = -2
ATTACK_MAIN = -1
ATTACK_CARRY_OVER = -2

async def reply_author(message, str):
    reply = f'{message.author.mention} {str}'
    await message.channel.send(reply)
    return


def get_target_id(mention_ids):
    if len(mention_ids) > 1:
        raise CommandError(messages.error_multi_mention)
    
    return mention_ids[0]

# boss_noを数値に変換するとともに、0-originとなるよう1引く
def convert_boss_no(boss_no):
    try:
        r = int(boss_no)
        if r<1 or r>5 :
            raise CommandError(messages.error_boss_no)
        return r-1
    except ValueError:
        raise CommandError(messages.error_boss_no)

# lap_noを数値に変換する
def convert_lap_no(lap_no):
    try:
        r = int(lap_no)
        if r<0 or r>180:
            raise CommandError(messages.error_lap_no)
        return r
    except ValueError:
        raise CommandError(messages.error_lap_no)

# attack_noを数値に変換するとともに、0-originとなるよう1引く
def convert_attack_no(attack_no):
    try:
        r = int(attack_no)
        if r<1 or r>3:
            raise CommandError(messages.error_attack_no)
        return r-1
    except ValueError:
        raise CommandError(messages.error_attack_no)

def convert_damage(damage):
    try:
        r = int(damage)
        if r<0 or r>=100000:
            raise CommandError(messages.error_damage)
        return r
    except ValueError:
        raise CommandError(messages.error_damage)

def convert_carry_over(carry_over):
    try:
        r = int(carry_over)
        if r<21 or r>90:
            raise CommandError(messages.error_carry_over)
        return r
    except ValueError:
        raise CommandError(messages.error_carry_over)

def convert_boss_no_with_lap_no(str):
    try:
        if str.endswith('+'):
            return (convert_boss_no(str[:len(str)-1]), LAP_NEXT)

        strs = str.split('@')
        if len(strs)==1:
            return (convert_boss_no(str), LAP_CURRENT)
        elif len(strs)==2:
            return (convert_boss_no(strs[0]), convert_boss_no(strs[1]))
        else:
            raise CommandError()
    except CommandError:
        raise CommandError(messages.error_boss_no_with_lap_no)

def convert_damage_with_attack_no(str):
    try:
        strs = str.lower().split('m')
        if len(strs)==1:
            return (convert_damage(strs[0]), ATTACK_MAIN)
        elif len(strs)==2:
            if strs[1] == '':
                return (convert_damage(strs[0]), ATTACK_CARRY_OVER)
            return (convert_damage(strs[0]), convert_attack_no(strs[1]))
        else:
            raise CommandError()
    except CommandError:
        raise CommandError(messages.error_damage_with_attack_no)


def convert_carry_over_with_attack_no(str):
    try:
        str = str.lower()

        if str.startswith('m'):
            str = str[1:]
            if str == '':
                return (0, ATTACK_CARRY_OVER)
            return (0, convert_attack_no(str))
        else:
            return (convert_carry_over(str), ATTACK_MAIN)
    except CommandError:
        raise CommandError(messages.error_carry_over_with_attack_no)

def convert_cancel_attack_no(str):
    try:
        str = str.lower()

        if str.startswith('m'):
            str = str[1:]
            return (convert_attack_no(str), ATTACK_MAIN)
        else:
            return (convert_attack_no(str), ATTACK_CARRY_OVER)
    except CommandError:
        raise CommandError(messages.error_cancel_attack_no)

