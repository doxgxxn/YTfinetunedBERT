import streamlit as st
import numpy as np
import pandas as pd
import requests
import torch
from transformers import BertTokenizer as bt, BertForSequenceClassification as bc
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
        print('scrolling done')
        return pd.DataFrame(results)

# def make_df(value):
#     video_url = get_url(nickname, video_num)
#     total_df = pd.DataFrame()

#     for i in video_url:
#         video = get_youtube_comments(i)
#         total_df = pd.concat([total_df, pd.DataFrame(video)], axis=0, ignore_index=True)

#     return total_df

@st.cache_resource(show_spinner=True)
def get_model():
    tokenizer = bt.from_pretrained('bert-base-multilingual-cased')
    model = bc.from_pretrained('doxgxxn/YoutubeModel')
    return tokenizer, model

tokenizer, model = get_model()

### input and button
st.header('Spam comment checker')
st.text("Example)")
st.code("secheppo")
st.code("chlwlals1gyul")

user_input1 = st.text_area("Enter the id of Game Youtuber")
button1 = st.button('Check videos')
try:
    if user_input1 and button1:
        if user_input1[0] == '@':
            user_input1 = user_input1[1:]
        st.write(get_url(user_input1.strip()))
except Exception as e:
    print(e)
    st.write('Please check the name again')


st.text("Example)")
st.code("YlgX_GG8Bd8")
user_input2 = st.text_area("Enter the Value of Video")
button2 = st.button('Run Model')
###

try:
    if user_input2 and button2:
        # preprocessing
        user_input = user_input2.strip()
        if user_input[0] == '@':
            user_input = user_input[1:]

        df = get_youtube_comments(user_input2)
        df = df[df['comment'].apply(lambda x : 4 < len(x) < 80)].reset_index(drop=True)
        
        print('length of df :', len(df))
        print('start modeling')
        # predicting
        sample = tokenizer(df['comment'].to_list(), padding=True, truncation=True, max_length=64, return_tensors='pt')
        output = model(**sample)

        print('modeling done')
        
        y_pred = np.argmax(output.logits.detach().numpy(), axis=1)
        predictions = torch.nn.functional.softmax(output.logits, dim=-1)
        predictions = predictions.cpu().detach().numpy()
        
        df['probability'] = [i[y_pred[idx]] for idx, i in enumerate(predictions)]
        df['probability'] = df['probability'].apply(lambda x: str(round(x * 100, 2))+'%')
        spam_idx = [idx for idx, i in enumerate(y_pred) if i == 1]

        comment = df.loc[spam_idx, 'comment'].drop_duplicates()

        result = pd.concat([df.loc[spam_idx, ['id', 'probability']], comment], axis= 1 )
        result.fillna('', inplace=True)
        result.rename(columns={"comment": "comment(distinct)"},inplace=True)
        st.write('Spam comment list')
        st.write(result)
        print('finished!')
        
except Exception as e:
    print(e)
    st.write('스팸 메시지가 없습니다!')