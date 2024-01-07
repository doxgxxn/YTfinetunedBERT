import streamlit as st
import pandas as pd
import requests
import re
import json
import time
from bs4 import BeautifulSoup



def get_url(nickname):
    res = requests.get(f"https://www.youtube.com/@{nickname}/videos")
    html_content = res.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.find('body').find_all('script')[14].get_text()

    start_index = text.find('{"responseContext":')
    end_index = text.find('</script>', start_index)
    json_data = text[start_index:end_index]

    # JSON 파싱
    yt_initial_data = json.loads(json_data)

    video_list = yt_initial_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']
    
    video_url = []
    for i in video_list[:10]: # 10개까지만
        try:
            video_url.append({"title": i['richItemRenderer']['content']['videoRenderer']['title']['accessibility']['accessibilityData']['label'],
                              "value": i['richItemRenderer']['content']['videoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'][9:]}
                             )
        except Exception as e:
            print('get_url_error : ', e)
            pass
    
    return pd.DataFrame(video_url)

def search_dict(dic, search_key):
    stack = [dic]
    while stack:
        current_item = stack.pop()
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)

def get_youtube_comments(video_id):
    YT_URL = f"https://www.youtube.com/watch?v={video_id}"
    HEADER = {"user-agent": "Mozilla/5.0"}

    session = requests.Session()
    r = session.get(YT_URL, headers=HEADER)

    tar_str1 = "var ytInitialData = "
    tar_str2 = "ytcfg.set({"

    ytinit = json.loads(r.text[r.text.find(tar_str1) + len(tar_str1) : r.text.find("};", r.text.find(tar_str1)) + 1])
    ytcfg = json.loads(r.text[r.text.find(tar_str2) + len(tar_str2) - 1 : r.text.find(");", r.text.find(tar_str2))])

    section = next(search_dict(ytinit['contents'], 'itemSectionRenderer'), None)
    renderer = next(search_dict(section, 'continuationItemRenderer'), None) if section else None

    if renderer:
        endpoints = [renderer['continuationEndpoint']]
        results = []
        while endpoints:
            endpoint = endpoints.pop()
            url = 'https://www.youtube.com' + endpoint['commandMetadata']['webCommandMetadata']['apiUrl']
            data = {'context': ytcfg['INNERTUBE_CONTEXT'], 'continuation': endpoint['continuationCommand']['token']}

            # print(f">>>>>> {url} <<<<<<")
            response = session.post(url, params={'key': ytcfg['INNERTUBE_API_KEY']}, json=data)
            _json = response.json()

            reload_items = list(search_dict(_json, 'reloadContinuationItemsCommand'))
            append_items = list(search_dict(_json, 'appendContinuationItemsAction'))
            actions = reload_items + append_items
            for action in actions:
                time.sleep(0.1)
                for item in action.get('continuationItems', []):
                    if action['targetId'] == 'comments-section':
                        r = []
                        for e in search_dict(item, "continuationEndpoint"):
                            r.append(e)
                        endpoints[:0] = r
                        
            
            for c in reversed(list(search_dict(_json, 'commentRenderer'))):
                results.append({
                    "id": c.get("authorText").get("simpleText"),
                    "comment": ''.join([x['text'] for x in c['contentText'].get('runs', [])]),
                    # "cid": c.get("commentId"),
                    # "time": c.get('publishedTimeText').get('runs')[0].get('text'),
                    # "author": c.get('authorEndpoint').get('browseEndpoint').get('browseId', ''),
                    # "votes": c.get('voteCount', {}).get('simpleText', '0'),
                })
            time.sleep(0.5)
        # print('scrolling done')
        return pd.DataFrame(results)



def get_spam():
    if sidebar_text:
            spam.extend([i.strip() for i in sidebar_text.split(',')])
            return spam
    else:
        return spam


# ### sidebar area    
spam = ['랭솔팅배', '이게임드', '이게임롤', '이게임벳', '이게임벴', '이게임뱃', '이게임뱄']

st.sidebar.write('**현재 검사 목록**')
st.sidebar.write(', '.join(spam))
st.sidebar.markdown("---")

sidebar_text = st.sidebar.text_input("추가하고 싶은 SPAM 이름이 있다면 콤마로 구분해서 추가하세요")
button_in_sidebar = st.sidebar.button("추가")



if sidebar_text and button_in_sidebar:
    spam.extend([i.strip() for i in sidebar_text.split(',')])
    st.sidebar.write('**최종 검사 목록**')
    st.sidebar.write(', '.join(spam))



### main area
st.header('Spam comment checker')
st.text("Example)")
st.code("secheppo")
st.code("chlwlals1gyul")

st.write("**유튜버의 아이디를 입력하세요**")
col1, col2 = st.columns([3,1])
with col1:
    user_input1 = st.text_area("예시를 확인하세요, 10개를 확인하면 시간이 걸립니다")
with col2:
    st.write(" ")
    st.write(" ")
    button1 = st.button('Check Videos')
    button3 = st.button('Run 10 Videos(1-2m)')
try:
    if user_input1 and button1:
        if user_input1[0] == '@':
            user_input1 = user_input1[1:]
        st.write(get_url(user_input1.strip()))
except Exception as e:
    print(e)
    st.write('Please check the name again')

try:
    if user_input1 and button3:
        if user_input1[0] == '@':
            user_input1 = user_input1[1:]
        df = pd.DataFrame()

        # df 전체 합치기
        for value in get_url(user_input1.strip())['value'].to_list():
            s_df = get_youtube_comments(value)
            df = pd.concat([df,s_df])

        df.reset_index(drop=True, inplace=True)
        # 길이 설정
        df = df[df['comment'].apply(lambda x : 4 < len(x) < 100)].reset_index(drop=True)

        # 한글, 숫자, 영어만 남기고 제거
        df['check'] = df['comment'].apply(lambda x: re.sub(r'[^0-9a-zA-Zㄱ-ㅎ 가-힣]', '', x))
        
        # 스팸 리스트 확인
        df = df[df['check'].apply(lambda x: any(word in x for word in get_spam()))]
        del df['check']
        if len(df) != 0:
            st.write("**중복을 제거한 리스트**")
            st.write(pd.DataFrame({"unique_comment":df['comment'].unique().tolist()}))
            st.markdown("---")
            st.write('Spam Comment List')
            st.write(df.reset_index(drop=True))

        else:
            st.write("**스팸 메시지가 없습니다!**")
            
except Exception as e:
    print(e)
    st.write('Pleas Check the name agian')




st.markdown("---")

st.write("**원하는 동영상의 Value 값을 입력하세요**")
user_input2 = st.text_area("위의 표에서 확인하세요")
button2 = st.button('Run Model')
###

try:
    if user_input2 and button2:
        # preprocessing
        user_input = user_input2.strip()
        if user_input[0] == '@':
            user_input = user_input[1:]

        df = get_youtube_comments(user_input2)

        # 길이 설정
        df = df[df['comment'].apply(lambda x : 4 < len(x) < 100)].reset_index(drop=True)

        # 한글, 숫자, 영어만 남기고 제거
        df['check'] = df['comment'].apply(lambda x: re.sub(r'[^0-9a-zA-Zㄱ-ㅎ 가-힣]', '', x))
        
        # 스팸 리스트 확인
        df = df[df['check'].apply(lambda x: any(word in x for word in get_spam()))]
        del df['check']
        if len(df) != 0:
            st.write("**중복을 제거한 리스트**")
            st.write(pd.DataFrame({"unique_comment":df['comment'].unique().tolist()}))
            st.markdown("---")
            st.write('Spam Comment List')
            st.write(df.reset_index(drop=True))

        else:
            st.write("**스팸 메시지가 없습니다!**")
            
except Exception as e:
    print(e)
    st.write('Pleas Check the value agian')