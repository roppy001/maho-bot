import datetime

import messages
import common

def reserve(data, command_args, mention_ids):
    msg = ''

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

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        # ボスの現在の周を取得し、lap_noを置き換える
        current_lap_no = data[common.DATA_BOSS_KEY][boss_id][common.BOSS_LAP_NO_KEY]
        # 討伐済みの場合は次の周の予約とする
        if data[common.DATA_BOSS_KEY][boss_id][common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED:
            current_lap_no += 1

        if lap_no == common.LAP_CURRENT:
            lap_no = current_lap_no
        elif lap_no == common.LAP_NEXT:
            lap_no = current_lap_no + 1

        # 現在の周 + 1 + reservation_limitより大きい場合はエラー
        min_lap = common.get_min_lap_no(data)

        if lap_no > min_lap + 1 + data[common.DATA_CONFIG_KEY][common.CONFIG_RESERVATION_LIMIT_KEY]:
            raise common.CommandError(messages.error_reserve_limit_lap_no)

        now_str = datetime.datetime.now().isoformat()

        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            daily[common.DAILY_MEMBER_KEY][target_key] = common.create_daily_member()
        
        member = daily[common.DAILY_MEMBER_KEY][target_key]

        res = member[common.DAILY_MEMBER_RESERVATION_KEY]
        atk = member[common.DAILY_MEMBER_ATTACK_KEY]
        
        for i in range(0, common.ATTACK_MAX + 1):
            # 凸登録できなかった場合はエラー生成
            if i == common.ATTACK_MAX:
                if attack_index == common.ATTACK_MAIN:
                    raise common.CommandError(messages.error_reserve_full)
                else:
                    raise common.CommandError(messages.error_reserve_impossible)

            # ステータスが凸済の場合はスキップ
            if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_DONE:
                if i == attack_index:
                    raise common.CommandError(messages.error_reserve_done)
                continue

            # 本凸予約の場合
            if attack_index == common.ATTACK_MAIN:
                # ステータスが持ち越しの場合はスキップ
                if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_CARRY_OVER:
                    continue
                
                # 本凸予約済みの場合はスキップ
                if i < len(res) and len(res[i]) > 0 and res[i][0][common.RESERVATION_STATUS_KEY] != common.DAILY_RESERVE_STATUS_NONE:
                    continue

                # 本凸予約を追加

                # 該当凸の予約ができるよう空配列を追加
                while i >= len(res):
                    res.append([])

                if len(res[i]) == 0:
                    res[i].append({})
                
                new_reserve = {}

                new_reserve[common.RESERVATION_STATUS_KEY] = common.DAILY_RESERVE_STATUS_RESERVED
                new_reserve[common.RESERVATION_LAP_NO_KEY] = lap_no
                new_reserve[common.RESERVATION_BOSS_ID_KEY] = boss_id
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_COMMENT_KEY] = comment
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[i][0] = new_reserve

                msg_atk_index = i
                msg_atk_branch = 0

                break

            # 持越予約の場合
            else:
                # ステータスが未凸で本凸未予約の場合はスキップ
                if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_NONE and (i >= len(res) or len(res[i]) == 0 or res[i][0][common.RESERVATION_STATUS_KEY] == common.DAILY_RESERVE_STATUS_NONE):
                    if i == attack_index:
                        raise common.CommandError(messages.error_reserve_impossible)
                    continue

                # 持越予約済みの場合はスキップ
                if i < len(res) and len(res[i]) > 1 and res[i][1][common.RESERVATION_STATUS_KEY] != common.DAILY_RESERVE_STATUS_NONE:
                    if i == attack_index:
                        raise common.CommandError(messages.error_reserve_impossible)
                    continue

                # 持越しの凸が合わない場合はスキップ
                if attack_index != common.ATTACK_CARRY_OVER and attack_index != i:
                    continue

                # 持越し予約を登録

                # 該当凸の予約ができるよう空配列を追加
                while i >= len(res):
                    res.append([])

                while len(res[i]) <= 1:
                    new_reserve = {}
                    new_reserve[common.RESERVATION_STATUS_KEY] = common.DAILY_RESERVE_STATUS_NONE
                    res[i].append(new_reserve)
                
                new_reserve = {}

                new_reserve[common.RESERVATION_STATUS_KEY] = common.DAILY_RESERVE_STATUS_RESERVED
                new_reserve[common.RESERVATION_LAP_NO_KEY] = lap_no
                new_reserve[common.RESERVATION_BOSS_ID_KEY] = boss_id
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_COMMENT_KEY] = comment
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[i][1] = new_reserve

                msg_atk_index = i
                msg_atk_branch = 1

                break

        member[common.DAILY_MEMBER_RESERVATION_KEY] = res 

        daily[common.DAILY_MEMBER_KEY][target_key] = member

        data[common.DATA_DAILY_KEY] = daily

        common.save_daily(daily)

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_reserve_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_re_arg)

    return (True,msg)




