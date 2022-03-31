# YouTube Liveのアーカイブからチャットを取得する

## 背景

* Youtube Live Streaming APIはリアルタイムで取るためのもの．（アーカイブからは取れない）
* 2018 Seleniumでとる方法が出回る．http://watagassy.hatenablog.com/entry/2018/10/06/002628
* 2018--2020/6 静的HTMLで取れることがわかる．http://watagassy.hatenablog.com/entry/2018/10/08/132939 https://note.com/or_ele/n/n5fc139ff3f06
* 2020/10 静的HTMLでは取れなくなる．Seleniumに戻る．

そこで，Dockerで動かしたブラウザからデータを取るようにする．

## 準備

すべでWSLのUbuntuで作業する．（好きな作業場所をエクスプローラで開き，アドレスバーで`bash`エンター）

```bash
sudo apt update
sudo apt install -y python3-selenium
pip3 install bs4 lxml pandas matplotlib
```

## 本番

WSLのUbuntuからDockerを起動する．参考：https://github.com/SeleniumHQ/docker-selenium

```bash
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm --name chrome selenium/standalone-chrome

# 終わるときは
docker rm -f chrome
```

チャットの取得（例：動画ID=7kPhOWM_uXQ）

```bash
python3 getchat.py 7kPhOWM_uXQ
#エラーになることがあるがよくわからない．もう一度実行すると取れたりする．
```

画面キャプチャをtest.pngに保存しているから，まずこれを確認する．

JSONをTSVに変換

```bash
python3 totsv.py livechatlog_7kPhOWM_uXQ.json
```

時間vs累積金額のグラフを描く（統計量も表示する）．

```bash
python3 cumplot.py livechatlog_7kPhOWM_uXQ.tsv
```

統計量も表示する

```
count      154.000000
mean       884.305195
std       1585.128589
min        100.000000
25%        250.000000
50%        490.000000
75%       1000.000000
max      12000.000000
Name: 9, dtype: float64
```

動画ID=GvXDQs_00IAの結果

```
count      40.00000
mean      820.25000
std      1056.45631
min       100.00000
25%       250.00000
50%       370.00000
75%      1000.00000
max      5000.00000
Name: 9, dtype: float64
```

## しくみの説明

`python3`でPythonを起動する．

```
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import re
import ast

driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME)

# 動画を開く
video_id = 'GvXDQs_00IA'
driver.get('https://www.youtube.com/watch?v=' + video_id)

# 画面キャプチャを取ってみる．
driver.save_screenshot('test.png')

# 画面キャプチャを取ってみる．
driver.save_screenshot('test2.png')
# 2枚の画像を見て，動画が再生されていること，チャットが表示されていることを確認する．
# 再生が始まらない場合があるようだが，よくわからない．再生していなかったら，もう一度get？
```

あとはhttp://watagassy.hatenablog.com/entry/2018/10/06/002628 の方法で取ればよい．https://note.com/or_ele/n/n5fc139ff3f06 も参考にする．

```python
dict_str = ""
next_url = ""
comment_data = []

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

for iframe in soup.find_all("iframe"):
    if("live_chat_replay" in iframe["src"]):
        next_url= iframe["src"]

next_url = 'https://www.youtube.com' + next_url
next_url # 取れていることを確認する．
```

チャットの取得

```python
driver.get(next_url)

soup = BeautifulSoup(driver.page_source, "lxml")

# Loop through all script tags.
for script in soup.find_all('script'):
    script_text = str(script)
    if 'ytInitialData' in script_text:
        dict_str = ''.join(script_text.split(" = ")[1:])

# Capitalize booleans so JSON is valid Python dict.
dict_str = dict_str.replace("false", "False")
dict_str = dict_str.replace("true", "True")

# Strip extra HTML from JSON.
dict_str = re.sub(r'};.*\n.+<\/script>', '}', dict_str)

# Correct some characters.
dict_str = dict_str.rstrip("  \n;")
dict_str # これで何も出てこないと，うまく行っていない．
```
