import datetime

import messages
import common

async def fin(message, data, command_args, mention_ids):
    msg = ''

    try : 
        if len(command_args) != 3 :
            raise common.CommandError(messages.error_args)

        target_id = common.get_target_id(mention_ids)

        boss_id = common.convert_boss_no(command_args[1])

        da = common.convert_damage_with_attack_no(command_args[2])

        damage = da[0]

        attack_index = da[1]

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        boss = data[common.DATA_BOSS_KEY]

        # 討伐済みの場合はエラーとする
        if data[common.DATA_BOSS_KEY][boss_id][common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED:
            raise common.CommandError(messages.error_fin_defeated)

        # ダメージが残りHP以上の場合はエラーとする
        if damage >= data[common.DATA_BOSS_KEY][boss_id][common.BOSS_HP_KEY]:
            raise common.CommandError(messages.error_fin_damage_over)

        # 既存の予約情報を取得
        now_str = datetime.datetime.now().isoformat()

        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            daily[common.DAILY_MEMBER_KEY][target_key] = common.create_daily_member()
        
        member = daily[common.DAILY_MEMBER_KEY][target_key]

        res = member[common.DAILY_MEMBER_RESERVATION_KEY]
        atk = member[common.DAILY_MEMBER_ATTACK_KEY]
        
        current_lap_no = data[common.DATA_BOSS_KEY][boss_id][common.BOSS_LAP_NO_KEY]
        current_lap_key = str(current_lap_no)

        dic = common.generate_reservation_dict(data)

        # コマンドから本凸か持越しかを判定
        if attack_index == common.ATTACK_MAIN:
            # 消費対象の凸を判定 消費対象の凸がない場合はエラー
            for i in range(0, common.ATTACK_MAX + 1):
                if i == common.ATTACK_MAX:
                    raise common.CommandError(messages.error_fin_full)

                if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_NONE:
                    target_attack_index = i
                    break

            # 本凸予約があるかどうかをチェック
            flg = True

            if current_lap_key in dic:
                rs = dic[current_lap_key][boss_id]

                for i in range(0, len(rs)):
                    # 予約があった場合は予約情報を保存
                    if rs[i][common.RESERVATION_ID_KEY] == target_id and rs[i][common.RESERVATION_BRANCH_KEY] == 0:
                        target_res = rs[i]
                        flg = False
                        break
            
            # 本凸予約が無い場合は新しく登録
            if flg:
                # 該当凸の登録ができるよう空配列を追加
                while target_attack_index >= len(res):
                    res.append([])
                
                new_reserve = {}

                new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_DONE
                new_reserve[common.RESERVATION_LAP_NO_KEY] = current_lap_no
                new_reserve[common.RESERVATION_BOSS_ID_KEY] = boss_id
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_COMMENT_KEY] = ''
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index] = [new_reserve]
            # 本凸予約がある場合
            else:
                # 本凸予約取得後、本凸予約の凸と消費対象の凸が異なる場合は交換
                org_attack_index = target_res[common.RESERVATION_SEQ_KEY]
                if org_attack_index != target_attack_index:
                    tmp = res[org_attack_index]
                    res[org_attack_index] = res[target_attack_index]
                    res[target_attack_index] = tmp
                
                new_reserve = res[target_attack_index][0]

                new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_DONE
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                # 持越予約は削除する
                res[target_attack_index] = [new_reserve]
            
            # ステータスを変更
            atk[target_attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY] = common.DAILY_ATTACK_STATUS_DONE

            msg_atk_index = target_attack_index
            msg_atk_branch = 0

        else:
            # 凸を指定しない持越しの場合
            if attack_index == common.ATTACK_CARRY_OVER:
                # 消費対象の凸を判定 消費対象の凸がない場合はエラー
                for i in range(0, common.ATTACK_MAX + 1):
                    if i == common.ATTACK_MAX:
                        raise common.CommandError(messages.error_fin_impossible)

                    if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_CARRY_OVER:
                        target_attack_index = i
                        break
            
            # 凸指定持ち越しの場合 該当のステータスが持越しでない場合はエラー
            else:
                if atk[attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY] != common.DAILY_ATTACK_STATUS_CARRY_OVER:
                    raise common.CommandError(messages.error_fin_impossible)
                
                target_attack_index = attack_index
            
            # 持越予約があるかどうかをチェック
            flg = True

            if current_lap_key in dic:
                rs = dic[current_lap_key][boss_id]

                for i in range(0, len(rs)):
                    # 予約があった場合は予約情報を保存
                    if rs[i][common.RESERVATION_ID_KEY] == target_id and rs[i][common.RESERVATION_BRANCH_KEY] == 1:
                        target_res = rs[i]
                        flg = False
                        break

            # 持越予約が無い場合は新しく登録
            if flg:
                # 該当凸の登録ができるよう空配列を追加
                while target_attack_index >= len(res):
                    res.append([])
                
                while len(res[target_attack_index]) <= 1:
                    new_reserve = {}
                    new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_NONE
                    res[target_attack_index].append(new_reserve)
                
                new_reserve = {}

                new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_DONE
                new_reserve[common.RESERVATION_LAP_NO_KEY] = current_lap_no
                new_reserve[common.RESERVATION_BOSS_ID_KEY] = boss_id
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_COMMENT_KEY] = ''
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index][1] = new_reserve
            # 持越予約がある場合
            else:
                new_reserve = res[target_attack_index][1]

                new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_DONE
                new_reserve[common.RESERVATION_DAMAGE_KEY] = damage
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index][1] = new_reserve
            
            # ステータスを変更
            atk[target_attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY] = common.DAILY_ATTACK_STATUS_DONE

            msg_atk_index = target_attack_index
            msg_atk_branch = 1
        
        # ボスのHPを消費
        boss[boss_id][common.BOSS_HP_KEY] -= damage

        data[common.DATA_BOSS_KEY] = boss

        common.save_boss(boss)

        member[common.DAILY_MEMBER_RESERVATION_KEY] = res 
        member[common.DAILY_MEMBER_ATTACK_KEY] = atk 

        daily[common.DAILY_MEMBER_KEY][target_key] = member

        data[common.DATA_DAILY_KEY] = daily

        common.save_daily(daily)

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_fin_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_fin_arg)

    return (True, msg)

