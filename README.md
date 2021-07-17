# maho-bot
プリコネR クランバトル用bot

# このBOTでできるようになること
## 実現優先度高め
 * クランメンバの凸状況が把握できるようになる
 * クランメンバがどの周のどのボスに凸をしたいかが把握できるようになる
 * 現在の各予約でのダメージが把握でき、ボスの討伐に人数が足りてるかどうかが把握できるようになる
 * 7月以降のクラバトの仕様に対応する
   * 全ボスの残りダメージが管理できること
   * メンバのステータスは1凸目(未／持越／済)、2凸目(未／持越／済)、3凸目(未／持越／済)の組み合わせで表現する
   * 各予約が、どの凸のどの本凸／持越なのかを管理できる
   * これまでは「どの周の何ボス目か」が進行状況を表していたが、今後は「どの周か」のみになる
 * 全ボス撃破したときに、次の周の予約をしている人に対してメンションでお知らせしてくれる
 * クランメンバ合計の凸状況が把握できるようになる
 * 誤ったコマンドを打った時に、別のメンバで修正ができる
## 実現優先度低め
 * クランメンバ合計の凸状況と5時までの時間を計測し、今のペースが速いのか遅いのかが把握できるようになる
 * 凸宣言後40分経過するとメンションで知らせてくれる
## 実現予定なし
 * 凸中かどうかのステータス管理
   * 凸コマンドは不要
 * 同時凸／ダメコン時のダメージ状況管理
   * チャットで直接やり取りすればOKなので不要

# コマンド

## 全コマンド共通
 * []で囲まれたものは省略可能
 * 末尾にメンションを付けると代行入力が可能。複数のメンションが付けられた場合は入力エラーとなる。
 * コマンドの間は1個以上の全角スペースもしくは半角スペースで空ける
 * 数字に数字以外のもの、入力できる範囲外の数字を入力した場合は入力エラーとなる
 * 全角数字は許容する
 * 5時をまたいだ際、前日の予約・実績情報は全て削除される

## クラメン用標準コマンド

### 予約コマンド
#### コマンドの使い方
~~~
.reserve 周 ボス番号 何凸目か 予定ダメージ(万単位) [コメント]
.予約 周 ボス番号 何凸目か 予定ダメージ(万単位) [コメント]
~~~

#### コマンド入力例
~~~
.reserve 23 3 1 2000
.予約 32 1 2 3200 ニャルワンパン予定
.reserve 0 5 3 2000 20時以降凸予定
~~~

#### コマンド打った時の動き
 * コマンドで指定された周、ボスに予約を入れる。予約リストに表示がされるようになる
 * 指定された凸の予約が入る。
   * 1凸目を予約してないのに2凸目3凸目の予約をした場合、2凸目を予約してないのに3凸目の予約をした場合は入力エラーになる
   * 1凸目を予約済みで、予約済みのボスに1凸目の予約をした場合、既存の情報の上書きになる
   * 1凸目を予約済みで、1凸目の持ち越しを予約済みでなくて、予約済みのボス以外に1凸目の予約をした場合、1凸目の持ち越しの予約となる
   * 1凸目を予約済みで、1凸目の持ち越しを予約済みで、予約済みのボス以外に1凸目の予約をした場合、入力エラーとなる
   * ユーザステータスが1凸目完了で、1凸目の持ち越しを持っていなくて、1凸目の予約をした場合は、入力エラーとなる
   * ユーザステータスが1凸目持越で、1凸目の持ち越しを持っていて、1凸目の持ち越しを予約済みでなくて、1凸目の予約をした場合は、1凸目の持ち越しの予約となる
   * 上記は2凸目以降も同等となる
 * 周が0の場合は、周未指定の予約として予約リストに表示がされる
 * コマンドに指定されたダメージをもとに、敵の残り予定HPが計算され、予約リストに表示される
 * コマンド実行時に、予約登録時刻が記録される。予約リストは、予約登録時刻順に表示がされる。上書きの場合は予約登録時刻は更新されない。
 * すでに討伐済みの周の予約がされた場合は、エラーとなる

### 凸完了コマンド

#### コマンドの使い方
~~~
.fin ボス番号 何凸目か 実績ダメージ(万単位)
.完了 ボス番号 何凸目か 実績ダメージ(万単位)
~~~

#### コマンド入力例
~~~
.fin 3 1 2000
.完了 1 2 3200
~~~

#### コマンド打った時の動き
 * コマンドで指定された周、ボスの実績ダメージを入れる。予約リストに実績として表示がされるようになる。
 * 指定された凸の実績登録が行われる。実績登録がされるとともに、予約が以下のルールに従って削除される。
   * 1凸目の実績がないのに2凸目3凸目の実績登録をした場合、2凸目の実績登録がないのに実績登録をした場合、エラーとなる
   * 1凸目の実績登録をした際に、同じボスに複数の予約登録があった場合、最も凸数目の小さい予約が削除される
   * 1凸目の実績登録をした際に、1凸目の予約、1凸目の持ち越し予約が別のボスに入っていた場合、1凸目の予約、1凸目の持ち越し予約が削除される
   * ユーザステータスが1凸目持越の時に1凸目の実績登録をした場合、持ち越しの実績登録扱いとなる。
   * ユーザステータスが1凸目完了の時に1凸目の実績登録をした場合、入力エラーとなる。
   * 上記は2凸目以降も同等となる
 * コマンドに指定されたダメージをもとに、敵の残り実績HPが計算され、予約リストに表示される
 * コマンド実行時に、予約がされてなかった場合は登録時刻が記録される。予約リスト内の実績リストには、登録時刻順で表示がされる。上書きの場合は登録時刻は更新されない。
 * すでに討伐済みの周の実績登録がされた場合は、エラーとなる

### キャンセルコマンド

#### コマンドの使い方
~~~
.cancel 周 ボス番号 何凸目か
.取消  周 ボス番号 何凸目か
~~~

### ステータス変更コマンド

#### コマンドの使い方
~~~
.modifyStatus ステータス
.状態変更  ステータス
ステータス：000 などの3桁の数字で表される 0:未凸 1:持ち越し 2:凸完了 を表す
~~~

## 管理用コマンド

### ボス周変更コマンド
#### コマンドの使い方
~~~
.modifyBoss 周 ボス番号
~~~

#### コマンド打った時の動き
 * 指定のボスが指定の周に変更される。

### ボス予約実績取り消しコマンド
#### コマンドの使い方
~~~
.cancelBoss 周 ボス番号
~~~

#### コマンド打った時の動き
 * 指定のボスが指定の周の予約、実績がすべて削除される

#### コマンドの使い方

### 全予約実績取り消しコマンド
#### コマンドの使い方
~~~
.cancelAll 周
~~~

#### コマンド打った時の動き
 * 指定の周および指定の周以降の予約・実績がすべて削除される
 * 周が0の場合、全ての予約・実績がすべて削除される

