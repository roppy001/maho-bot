# 設計

## ファイル構造 

~~~
config.txt : 各種設定、ボスの設定など  
lock.loc : ロックファイル(実行時に一時的に生成)  
data/  
  boss.txt : ボスの周、HP、名前などを保存  
  member.txt : クラメン情報  
  daily.txt : クラメンの凸状況、予約、実績情報
  server.txt
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
[{
   "id" : "123456789012345678",
  },
]

省略
]
~~~

 * id : discordでユーザを特定するID  
 * attack : 3凸分の状態を配列で保持  
 * status : 0:未凸 1:持ち越し 2:凸完了  
 * second : 持ち越し秒数を保持  

## daily.txt
~~~
{
 "day" : "20210724"
 "member" :
 [{
   "id" : "123456789012345678",
   "attack" : [{"status" : 0},
               {"status" : 1, "carry_over" : 65},
               {"status" : 2}]
   "reservation" :
    [[{
       "seq" : 0
       "branch" : 0
       "status" : 0
       "lap_no" : 1
       "boss_id" : 0
       "damage" : 0
       "registered_date" : 0
      },
      {
      }],
      [省略],
      [省略]]
  },
  省略
 ]
~~~

 * day : 5時切り替えの日を記録 5時の切り替えが必要かの判定に用いる

## server.txt
~~~
{
  "command_channel" : ""
  "reservation_channel" : ""
  "detail_status_channel" : ""
}
~~~
