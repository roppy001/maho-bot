

class CommandError(Exception):
    pass

async def reply_author(message, str):
    reply = f'{message.author.mention} {str}'
    await message.channel.send(reply)
    return

def check_boss_no(boss_no):
    boss_no_list = ['1','2','3','4','5']
    if boss_no.isdigit():
        if boss_no in boss_no_list:
            return True
        else:
            return False
    else:
        return False

def check_laps(lap_no):
    if lap_no.isdigit():
        return True
    else:
        return False

def check_assault(assault):
    assault_list = ['1','2','3']
    if assault.isdigit():
        if assault in assault_list:
            return True
        else:
            return False
    else:
        return False

def check_damage(damage):
    if damage.isdigit():
        return True
    else:
        return False

def check_over(over):
    if over.isdigit():
        if 21 <= int(over) <= 90:
            return True
        else:
            return False
    else:
        return False
