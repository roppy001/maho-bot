# maho-bot
プリコネR クランバトル用bot

# コマンド概要
~~~
■予約コマンド
.re ボス番号[@周 or +] 予定ダメージ(万単位)[m[何凸目か]] [コメント]
+が書かれた場合は次の周の予約
周が省略された場合は現在の周、

＜利用例＞
.re 5 3700 ワンパン予定 ⇒ 現在の周の5ボスの予約
.re 3+ 700m ⇒ 次の周の持ち越し予約
.re 3@23 700m1 ⇒ 23周の3ボスの1凸目の持ち越し予約


■凸完了コマンド
.fin ボス番号 実績ダメージ(万単位)[m[何凸目か]]

＜利用例＞
.fin 5 2500 ⇒ 5ボスに本凸 2500万ダメージ
.fin 3 700m ⇒ 3ボスに持ち越し 700万ダメージ
.fin 2 700m1 ⇒ 2ボスに1凸目持ち越し 700万ダメージ


■討伐コマンド
.la ボス番号 [持ち越し秒数 or m[何凸目か]]

＜利用例＞
.la 5 90 ⇒ 5ボスに本凸 90秒残し
.la 5 m ⇒ 5ボスに持ち越し
.la 5 m3 ⇒ 5ボスに3凸目持ち越し


■取り消しコマンド
.cl ⇒ 自分の予約をすべて削除

■ステータス変更コマンド
.ms [ステータス]

＜利用例＞
.ms ⇒ 現在の自分のステータスを表示する
.ms 000 ⇒ すべて未凸状態にしたあと、予約をすべて削除する
.ms 120 ⇒ 1凸目を持越、2凸目を凸済、3凸目を未凸状態にした後、予約をすべて削除する

~~~

## 管理用コマンド
~~~
■クラバト参加コマンド
.add [メンション(複数指定可)]

＜利用例＞
.add ⇒ 自分が参加
.add @あああ @いいい ⇒ あああといいいが参加

■クラバト脱退コマンド
.remove [メンション(複数指定可)]

＜利用例＞
.remove ⇒ 自分が脱退
.remove @あああ @いいい ⇒ あああといいいが脱退

■ボス状態変更コマンド
.mb ボス番号 周 [HP]

.mb 1 1 ⇒ 1ボスの周を1に変更して、HPをMAXにする
.mb 1 3 300⇒ 1ボスの周を13に変更して、残りHPを300万にする

■bot鯖脱退コマンド
.kickbot ⇒ botがdiscord鯖から抜ける

~~~



# 導入方法
## 前提
各クランにてbot動作用のPC／サーバがあること (windows/linux どちらも可)

## 導入手順

1. python 3.8 以降の最新版をインストール

2. discord.pyを導入
~~~
以下のサイトなどを参考に導入する
https://discordpy.readthedocs.io/ja/latest/intro.html

linux:
python3 -m pip install -U discord.py
windows:
py -3 -m pip install -U discord
~~~

3. BOTアカウントを作成
~~~
"discord 自作 bot 導入" で検索するとわかりやすい手順が沢山あるのでそれらを参考にするとよい

discord Developer用サイトは以下
https://discord.com/developers/applications

Applicationを作成後、settings > botの画面でbuild a botを選び、TOKENの内容をコピー控えておく
settings > OAuth2 の OAuth2 URL Generatorを用いてURLを生成しておく
SCOPESには"bot"、BOT PERMISSIONSには"Administrator"を選択し、URLを作成。この内容も控えておく

~~~

4. discordサーバへの招待
~~~
3.で生成したURLにアクセスし、botを導入したいdiscord鯖に招待する
~~~

5. 環境変数にトークンを設定
~~~
環境変数のトークンを設定する。トークンは他者に盗まれないよう注意する。

■windowsの場合
 Window システムツール > コントロールパネル を開く
 システムとセキュリティ > システム を開く
 システムの詳細設定 を開く
 下部の環境変数 を開く
新規に BOT_TOKEN を追加し、値として3.で控えておいたTOKENの内容を設定

■linuxの場合
export BOT_TOKEN=(3.で控えておいたTOKENの内容を設定)を実行
.bashrc等に設定しておく
~~~

6. 実行

botを起動する。
~~~
linux:
./run.sh

windows:
run.bat
~~~
bot起動後、初回にどこかでチャットを打つとコマンド入力用のチャンネルが自動生成される。
以後は、該当のチャンネルでコマンドが打てるようになる

以後、BOTの再起動は6.の手順のみ実施でOK。

動作環境
python 3.8.10
windows 10／amazon linux 2018.3

# コマンド詳細

## 全コマンド共通
 * []で囲まれたものは省略可能
 * 末尾にメンションを付けると代行入力が可能。複数のメンションが付けられた場合は入力エラーとなる。
 * コマンドの間は1個以上の全角スペースもしくは半角スペースで空ける
 * 数字に数字以外のもの、入力できる範囲外の数字を入力した場合は入力エラーとなる
 * 全角数字は許容する
 * コマンドの英字大文字指定は許容する
 * 5時をまたいだ際、前日の予約・実績情報は全て削除される

## クラメン用標準コマンド

### 予約コマンド
#### コマンドの使い方
~~~
.reserve ボス番号[@周 or +] 予定ダメージ(万単位)[m[何凸目か]] [コメント]

エイリアス
.re 
.予約 
~~~

#### コマンド打った時の動き
 * コマンドで指定された周、ボスに予約を入れる。予約リストに表示がされるようになる
 * 凸の予約が入る。
   * 基本的に追加の予約として登録される。既存の予約の変更はできない。
   * 凸指定なし予約の場合、ユーザーステータス、予約済状況を踏まえ、最も若い凸の予約が入る。予約ができない場合はエラーとなる
   * 本凸予約が持ち越し予約に置き換わることはない。
 * 周が0の場合は、周未指定の予約として予約リストに表示がされる
 * コマンド実行時に、予約登録時刻が記録される。予約リストは、予約登録時刻順に表示がされる。
 * すでに討伐済みの周の予約がされた場合は、エラーとなる

### 凸完了コマンド

#### コマンドの使い方
~~~
.finish ボス番号 実績ダメージ(万単位)[m[何凸目か]]

エイリアス
.fin
.完了
~~~

#### コマンド打った時の動き
 * コマンドで指定された周、ボスの完了登録がされる。
 * このコマンドではボスは討伐状態にならない。HPが0となるようなダメージを登録するとエラーになる
 * 1凸目の本凸がまだの状態で、3凸目の予約がされたボスに凸をすると、別のボスに1凸目として登録された予約が3凸目本凸に置き換わる
 * 指定の凸のユーザステータスを凸完了済に変更する
 * コマンドに指定されたダメージをもとに、敵の残り実績HPが計算され、予約リストに表示される
 * すでに討伐済みの周の完了登録は、エラーとなる

### 討伐登録コマンド

#### コマンドの使い方
~~~
.lastattack ボス番号 [持ち越し秒数 or m[何凸目か]]

エイリアス
.la
.討伐
~~~

#### コマンド打った時の動き
 * コマンドで指定された周、ボスの討伐実績登録がされる。予約リストに実績として表示がされるようになる。
 * 指定のボスの周状態が次の周に変更される
 * 1凸目の本凸がまだの状態で、3凸目の予約がされたボスに凸をすると、別のボスに1凸目として登録された予約が3凸目本凸に置き換わる
 * まだ未凸の予約が残っていた場合、未凸の予約が、設定に沿って次の周かもしくは凸未指定の予約に移動される
 * 指定の凸のユーザステータスが持ち越しの場合、ユーザステータスを凸完了に変更する
 * 指定の凸のユーザステータスが未凸の場合、ユーザステータスを持ち越しに変更する
 * すでに討伐済みの周の討伐登録は、エラーとなる

### キャンセルコマンド

#### コマンドの使い方
~~~
.cancel

エイリアス
.cl
.取消
~~~

#### コマンド打った時の動き
 * 予約がすべて削除される

### ステータス変更コマンド

#### コマンドの使い方
~~~
.modifystatus ステータス
ステータス：000 などの3桁の数字で表される 0:未凸 1:持ち越し 2:凸完了 を表す

エイリアス
.ms
.状態変更
~~~

#### コマンド打った時の動き
 * ユーザステータスが指定のステータスに変更される。
   * 左から1凸目、2凸目、3凸目を表す

## 管理用コマンド

### クラメン追加／削除コマンド
#### コマンドの使い方
~~~
.add (メンション)
.remove (メンション)
~~~

#### コマンド打った時の動き
 * メンションしたメンバを追加・削除する。追加することで予約などの各種コマンドの対象になる。
 * メンションを省略した場合は自分が追加・削除される。

### ボス周変更コマンド
#### コマンドの使い方
~~~
.modifyboss ボス番号[+] 周 [HP]

エイリアス
.mb
~~~

#### コマンド打った時の動き
 * 指定のボスが指定の周の指定のHPに変更される。+を打った場合討伐状態となる。
 * 周を変更した際、討伐済みとなったボスの予約は周指定なし予約に移動される

### bot追放コマンド
#### コマンドの使い方
~~~
.kickbot
~~~

#### コマンド打った時の動き
 * botがdiscord鯖から立ち去る

