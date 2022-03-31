from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import re
import ast
import sys

driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME)

# 動画を開く
video_id = sys.argv[1]
driver.get('https://www.youtube.com/watch?v=' + video_id)

# 画面キャプチャを取ってみる．
driver.save_screenshot('test.png')

dict_str = ""
next_url = ""
comment_data = []

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

for iframe in soup.find_all("iframe"):
    if("live_chat_replay" in iframe["src"]):
        next_url = iframe["src"]

next_url = 'https://www.youtube.com' + next_url

while(1):
    try:
        driver.get(next_url)
        soup = BeautifulSoup(driver.page_source,"lxml")

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

        # TODO: I don't seem to have any issues with emoji in the messages.
        # dict_str = RE_EMOJI.sub(r'', dict_str)

        # Evaluate the cleaned up JSON into a python dict.
        dics = ast.literal_eval(dict_str)

        # TODO: On the last pass this returns KeyError since there are no more
        # continuations or actions. Should probably just break in that case.
        continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
        print('Found another live chat continuation:')
        print(continue_url)
        next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url

        # Extract the data for each live chat comment.
        for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
            comment_data.append(str(samp) + "\n")

    # next_urlが入手できなくなったら終わり
    except requests.ConnectionError:
        print("Connection Error")
        continue
    except requests.HTTPError:
        print("HTTPError")
        break
    except requests.Timeout:
        print("Timeout")
        continue
    except requests.exceptions.RequestException as e:
        print(e)
        break
    except KeyError as e:
        error = str(e)
        if 'liveChatReplayContinuationData' in error:
            print('Hit last live chat segment, finishing job.')
        else:
            print("KeyError")
            print(e)
        break
    except SyntaxError as e:
        print("SyntaxError")
        print(e)
        break
        # continue #TODO
    except KeyboardInterrupt:
        break
    except Exception:
        print("Unexpected error:" + str(sys.exc_info()[0]))

filename = f'livechatlog_{video_id}.json'
with open(filename, mode='w', encoding="utf-8") as f:
    f.writelines(comment_data)