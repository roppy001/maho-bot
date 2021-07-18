# 設計

## ファイル構造 

~~~
config.txt : 各種設定、ボスの設定など  
lock.loc : ロックファイル(実行時に一時的に生成)  
data/  
  boss.txt : ボスの周、HP、名前などを保存  
  member.txt : クラメン情報  
  reservation.txt : 予約、実績情報  
~~~

## boss.txt

~~~
JSON形式
[
{
 "name" : "ゴブリングレート"
 "lap_no" : 5
 "max_hp" : 8500
 "hp" : 4500
 "status" : 0
 "message_id" : ""
},

省略
]
~~~
 * 1ボス～5ボスは配列で表現される 1ボスは配列0に設定される
 * name : ボスの名前 
 * lap_no : 段階 5が指定されていたら5段階目 
 * max_hp : 最大HP 万単位で指定 
 * hp : HP 万単位で指定
 * status : 0:生存 1:討伐
 * message_id : UI用に仕様 ボスの状態を表示するメッセージのIDを格納

## member.txt

~~~
""
   {
 "id" : "" 
 "lap_no" : 5
 "max_hp" : 8500
 "hp" : 4500
 "status" : 0
 "message_id" : ""
},

省略
]
~~~
 * 1ボス～5ボスは配列で表現される 1ボスは配列0に設定される
 * name : ボスの名前 
 * lap_no : 段階 5が指定されていたら5段階目 
 * max_hp : 最大HP 万単位で指定 
 * hp : HP 万単位で指定
 * status : 0:生存 1:討伐
 * message_id : UI用に仕様 ボスの状態を表示するメッセージのIDを格納

