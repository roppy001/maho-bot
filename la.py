import datetime

import messages
import common

async def la(message, data, command_args, mention_ids):
    msg = ''

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

        boss = data[common.DATA_BOSS_KEY]

        # 討伐済みの場合はエラーとする
        if data[common.DATA_BOSS_KEY][boss_id][common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED:
            raise common.CommandError(messages.error_la_defeated)

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

        min_lap_no = common.get_min_lap_no(data)

        dic = common.generate_reservation_dict(data)

        # コマンドから本凸か持越しかを判定
        if attack_index == common.ATTACK_MAIN:
            # 消費対象の凸を判定 消費対象の凸がない場合はエラー
            for i in range(0, common.ATTACK_MAX + 1):
                if i == common.ATTACK_MAX:
                    raise common.CommandError(messages.error_la_full)

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
                new_reserve[common.RESERVATION_DAMAGE_KEY] = boss[boss_id][common.BOSS_HP_KEY]
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
                new_reserve[common.RESERVATION_DAMAGE_KEY] = boss[boss_id][common.BOSS_HP_KEY]
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index][0] = new_reserve
            
            # ステータスを変更
            atk[target_attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY] = common.DAILY_ATTACK_STATUS_CARRY_OVER
            atk[target_attack_index][common.DAILY_MEMBER_ATTACK_CARRY_OVER_KEY] = carry_over

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
                new_reserve[common.RESERVATION_DAMAGE_KEY] = boss[boss_id][common.BOSS_HP_KEY]
                new_reserve[common.RESERVATION_COMMENT_KEY] = ''
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index][1] = new_reserve
            # 持越予約がある場合
            else:
                new_reserve = res[target_attack_index][1]

                new_reserve[common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_DONE
                new_reserve[common.RESERVATION_DAMAGE_KEY] = boss[boss_id][common.BOSS_HP_KEY]
                new_reserve[common.RESERVATION_DATETIME_KEY] = now_str

                res[target_attack_index][1] = new_reserve
            
            # ステータスを変更
            atk[target_attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY] = common.DAILY_ATTACK_STATUS_DONE

            msg_atk_index = target_attack_index
            msg_atk_branch = 1
        
        # ここまでの情報をdataに反映
        member[common.DAILY_MEMBER_RESERVATION_KEY] = res 
        member[common.DAILY_MEMBER_ATTACK_KEY] = atk 

        daily[common.DAILY_MEMBER_KEY][target_key] = member

        data[common.DATA_DAILY_KEY] = daily

        # ボスのHPを0にし、ステータスを討伐状態に
        boss[boss_id][common.BOSS_HP_KEY] = 0
        boss[boss_id][common.BOSS_STATUS_KEY] = common.BOSS_STATUS_DEFEATED

        # 残ってた予約を移動する
        if data[common.DATA_CONFIG_KEY][common.CONFIG_INVALID_RESERVATION_MOVE_NEXT]:
            new_lap_no = current_lap_no + 1
        else:
            new_lap_no = 0

        # 辞書を再生成
        dic = common.generate_reservation_dict(data)

        if current_lap_key in dic:
            rs = dic[current_lap_key][boss_id]

            for r in rs:
                # 予約状態のものがあった場合は、周を移動する
                if r[common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_RESERVED:
                    member_key = str(r[common.RESERVATION_ID_KEY])
                    data[common.DATA_DAILY_KEY][common.DAILY_MEMBER_KEY][member_key][common.DAILY_MEMBER_RESERVATION_KEY][r[common.RESERVATION_SEQ_KEY]][r[common.RESERVATION_BRANCH_KEY]][common.RESERVATION_LAP_NO_KEY] = new_lap_no

        # 全ボスが討伐済もしくは次の周に移っている場合は、次の周に移る
        flg = True
        for b in boss:
            if b[common.BOSS_STATUS_KEY] == common.BOSS_STATUS_ALIVE and b[common.BOSS_LAP_NO_KEY] == min_lap_no:
                flg = False
        
        if flg:
            for i in range(0, len(boss)):
                if boss[i][common.BOSS_LAP_NO_KEY] == min_lap_no:
                    boss[i][common.BOSS_LAP_NO_KEY] += 1
                    boss[i][common.BOSS_STATUS_KEY] = common.BOSS_STATUS_ALIVE 
                    phase = common.get_phase(data, boss[i][common.BOSS_LAP_NO_KEY])
                    boss[i][common.BOSS_NAME_KEY] = data[common.DATA_CONFIG_KEY][common.CONFIG_BOSS_KEY][i][common.BOSS_NAME_KEY]
                    boss[i][common.BOSS_MAX_HP_KEY] = data[common.DATA_CONFIG_KEY][common.CONFIG_BOSS_KEY][i][common.BOSS_MAX_HP_KEY][phase]
                    boss[i][common.BOSS_HP_KEY] = boss[i][common.BOSS_MAX_HP_KEY]

                    data[common.DATA_BOSS_KEY] = boss
                    await common.notice_reserving_member(data, message.guild, i)

        # ステータスが討伐済みで、次の周が討伐可能な場合は次の周に移る
        data[common.DATA_BOSS_KEY] = boss
        max_lap_no = common.get_max_attack_lap_no(data)

        for i in range(0, len(boss)):
            if boss[i][common.BOSS_STATUS_KEY] == common.BOSS_STATUS_DEFEATED and boss[i][common.BOSS_LAP_NO_KEY] < max_lap_no:
                boss[i][common.BOSS_LAP_NO_KEY] += 1
                boss[i][common.BOSS_STATUS_KEY] = common.BOSS_STATUS_ALIVE 
                phase = common.get_phase(data, boss[i][common.BOSS_LAP_NO_KEY])
                boss[i][common.BOSS_NAME_KEY] = data[common.DATA_CONFIG_KEY][common.CONFIG_BOSS_KEY][i][common.BOSS_NAME_KEY]
                boss[i][common.BOSS_MAX_HP_KEY] = data[common.DATA_CONFIG_KEY][common.CONFIG_BOSS_KEY][i][common.BOSS_MAX_HP_KEY][phase]
                boss[i][common.BOSS_HP_KEY] = boss[i][common.BOSS_MAX_HP_KEY]

                data[common.DATA_BOSS_KEY] = boss
                await common.notice_reserving_member(data, message.guild, i)

        data[common.DATA_BOSS_KEY] = boss

        common.save_boss(boss)

        common.save_daily(data[common.DATA_DAILY_KEY])

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_la_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_la_arg)

    return (True, msg)





