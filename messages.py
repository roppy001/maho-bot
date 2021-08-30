# 単語
word_atk_branch = ['本凸','持越']
word_atk_index = '凸目'
word_atk_status = ['未凸','持越','凸済']
word_atk_status_mark = ['\N{LARGE BLUE CIRCLE}','\N{LARGE GREEN CIRCLE}','\N{LARGE ORANGE CIRCLE}']
word_name_unknown = '(不明)'

# お知らせ文言
msg_new_daily = '日付変わり、予約情報初期化されたで'
msg_reserve_success = 'として予約登録されたで'
msg_fin_success = 'として完了登録されたで'
msg_la_success = 'として討伐登録されたで'
msg_ms_success = 'に変更したで'
msg_shutdown_success = 'ほな、さいなら'
msg_notice_boss_change = 'が登場したで'

# エラー文言
error_lock = '他のコマンド処理を実行中どす　メッセージ続く場合はロックファイルを削除しとぉくれやす'

error_args = '正しい引数を入力しとぉくれやす'
error_boss_no = 'ボス番号は1~5を入力しとぉくれやす'
error_lap_no = '周の指定は1~180を入力しとぉくれやす'
error_attack_no = '「何凸目か」は1~3を入力しとぉくれやす'
error_damage = 'ダメージは数値0～99999を入力しとぉくれやす'
error_carry_over = '持ち越し秒数は21~90の範囲で入力しとぉくれやす'
error_comment = 'コマンドの打ち間違いの可能性があるんや'
error_role = 'ロールを指定しとぉくれやす'
error_role_invalid = '指定のロール見つからしまへん'
error_cmd_none = '正しいコマンドを入力しとぉくれやす'
error_multi_mention = '複数のメンション付けられてます'
error_init_member = '初回起動もしくは設定読込の失敗のため、クラメン情報が初期化されました'
error_not_member = 'クラメンとして登録されてないメンバです'
error_status = 'ステータスは000～222の中から選んでください 0:未凸 1:持越 2:凸済'
error_mention_limited = '代行入力は管理コマンド入力チャンネルからのみ入力可能どす'
error_command_limited = '管理コマンド入力チャンネルから実行しとぉくれやす'

error_boss_no_with_lap_no = 'ボス番号は ボス番号(1～5) もしくは ボス番号+ もしくは ボス番号@周(1～180) で指定しとぉくれやす'
error_damage_with_attack_no = 'ダメージは ダメージ もしくは ダメージm もしくは ダメージm1～3 で指定しとぉくれやす'
error_carry_over_with_attack_no = '持ち越しは 持ち越し秒数 もしくは m もしくは m1～3 で指定しとぉくれやす'
error_cancel_attack_no = '対象は 1～3 もしくは m1～3 で指定しとぉくれやす'
error_lap_no_with_status = '周番号は 周番号(1～180) もしくは 周番号+ で指定しとぉくれやす'

error_reserve_limit_lap_no = '予約可能な範囲を超えてます'
error_reserve_full = 'これ以上予約できしまへん'
error_reserve_done = '該当の凸はすでに終わってます'
error_reserve_impossible = '該当の持越し凸の予約はできしまへん'
error_reserve_defeated = '既に討伐されてます'

error_fin_defeated = '既に討伐されてます'
error_fin_full = 'これ以上凸できしまへん'
error_fin_damage_over = '実績ダメージが残りHP以上となってます　討伐登録をする場合は討伐コマンドで登録しとぉくれやす'
error_fin_impossible = '該当の持越し凸の登録はできしまへん'

error_la_defeated = '既に討伐されてます'
error_la_full = 'これ以上凸できしまへん'
error_la_impossible = '該当の持越し凸の登録はできしまへん'

error_add_impossible = 'これ以上クラメンの追加はできしまへん'

# 用例
cmd_re_arg = '.re ボス番号[@周 or +] 予定ダメージ(万単位)[m[何凸目か]] [コメント]\n(例: .re 3+ 700m 討伐予定)'
cmd_fin_arg = '.fin ボス番号 実績ダメージ(万単位)[m[何凸目か]]\n(例: .fin 2 700m1)'
cmd_la_arg = '.la ボス番号 持ち越し秒数 or m[何凸目か]\n(例: .la 5 m)'
cmd_cancel_arg = '.cl \n(例: .cl)'
cmd_add_arg = '.add (追加したいメンバをメンション) \n(例: .add @マホ )'
cmd_remove_arg = '.remove (追加したいメンバをメンション) \n(例: .remove @マホ )'
cmd_ms_arg = '.ms 000～222 \n(例: .ms 000 )'
cmd_mb_arg = '.mb ボス番号 周[+] [HP] \n(例: .mb 3 10+ )'
cmd_im_arg = '.im ロール \n(例: .im @クランメンバー )'

