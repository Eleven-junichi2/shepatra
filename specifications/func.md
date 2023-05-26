# func

## hash_str_as_hexdigest()

- ハッシュ関数を要素に持つ順序付きリスト(hashfunclayers)を受け取る
- 与えられたハッシュ化したい文字列をforループでhashfunclayersの各ハッシュ関数にかける。
  - このとき、2番目以降のhashfunclayersの要素の番のとき、前回ハッシュ化した文字列を現在の番のハッシュ関数でハッシュ化する
