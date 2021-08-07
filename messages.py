# 単語
word_atk_branch = ['本凸','持越']
word_atk_index = '凸目'

# お知らせ文言
msg_new_daily = '日付変わり、予約情報初期化されたで'
msg_reserve_success = 'として登録されたで'

# エラー文言
error_args = '正しい引数を入力しとぉくれやす'
error_boss_no = 'ボス番号は1~5を入力しとぉくれやす'
error_lap_no = '周の指定は1~180を入力しとぉくれやす'
error_attack_no = '「何凸目か」は1~3を入力しとぉくれやす'
error_damage = 'ダメージは数値0～99999を入力しとぉくれやす'
error_carry_over = '持ち越し秒数は21~90の範囲で入力しとぉくれやす'
error_cmd_none = '正しいコマンドを入力しとぉくれやす'
error_multi_mention = '複数のメンション付けられてます'
error_init_member = '初回起動もしくは設定読込の失敗のため、クラメン情報が初期化されました'
error_not_member = 'クラメンとして登録されてないメンバです'

error_boss_no_with_lap_no = 'ボス番号は ボス番号(1～5) もしくは ボス番号+ もしくは ボス番号@周(1～180) で指定しとぉくれやす'
error_damage_with_attack_no = 'ダメージは ダメージ もしくは ダメージm もしくは ダメージm1～3 で指定しとぉくれやす'
error_carry_over_with_attack_no = '持ち越しは 持ち越し秒数 もしくは m もしくは m1～3 で指定しとぉくれやす'
error_cancel_attack_no = '対象は 1～3 もしくは m1～3 で指定しとぉくれやす'

error_reserve_full = 'これ以上予約できしまへん'
error_reserve_done = '該当の凸はすでに終わってます'
error_reserve_impossible = '該当の持越し凸の予約はできしまへん'

# 用例
cmd_re_arg = '.re ボス番号[@周 or +] 予定ダメージ(万単位)[m[何凸目か]] [コメント]\n(例: .re 3+ 700m 討伐予定)'
cmd_fin_arg = '.fin ボス番号 実績ダメージ(万単位)[m[何凸目か]]\n(例: .fin 2 700m1)'
cmd_la_arg = '.la ボス番号 持ち越し秒数 or m[何凸目か]\n(例: .la 5 m)'
cmd_cancel_arg = '.cl ボス番号[@周 or +] [何凸目か or m[何凸目か]]号\n(例: .cl 5 3)'
cmd_add_arg = '.add (追加したいメンバをメンション) \n(例: .add @マホ )'
cmd_add_arg = '.remove (追加したいメンバをメンション) \n(例: .remove @マホ )'

