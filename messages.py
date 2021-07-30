# エラー文言
error_args = '正しい引数を入力しとぉくれやす'
error_boss_no = 'ボス番号は1~5を入力しとぉくれやす'
error_lap_no = '周の指定は1~180を入力しとぉくれやす'
error_attack_no = '「何凸目か」は1~3を入力しとぉくれやす'
error_damage = 'ダメージは数値0～99999を入力しとぉくれやす'
error_carry_over = '持ち越し秒数は21~90の範囲で入力しとぉくれやす'
error_cmd_none = '正しいコマンドを入力しとぉくれやす'
error_multi_mention = '複数のメンション付けられてます'

error_boss_no_with_lap_no = 'ボス番号は ボス番号(1～5) もしくは ボス番号+ もしくは ボス番号@周(1～180) で指定しとぉくれやす'
error_damage_with_attack_no = 'ダメージは ダメージ もしくは ダメージm もしくは ダメージm1～3 で指定しとぉくれやす'
error_carry_over_with_attack_no = '持ち越しは 持ち越し秒数 もしくは m もしくは m1～3 で指定しとぉくれやす'

# 用例
cmd_re_arg = '.re 周 ボス番号 何凸目か 予定ダメージ(万単位) コメント\n(例: .reserve 12 3 1 1200 事故らなければワンパン)'
cmd_fin_arg = '.fin ボス番号 何凸目か 実績ダメージ(万単位)\n(例: .fin 5 1 1800)'
cmd_la_arg = '.la ボス番号 何凸目か 持ち越し秒数\n(例: .la 3 2 29)'
cmd_cancel_arg = '.cl 周 ボス番号 何凸目か\n(例: .cl 12 3 2)'
