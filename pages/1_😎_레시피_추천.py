import streamlit as st
import requests
import json
import configparser
import http.client
from PIL import Image
from io import BytesIO
import os

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = '66e534cc55d74b979a363bc810a93c4f'

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/completions/LK-D', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['text']
        else:
            return 'Error'


config = configparser.ConfigParser()
config.sections()
config.read('./your_apikey.ini')

completion_executor = CompletionExecutor(
    host=config['CLOVA']['host'],
    api_key=config['CLOVA']['api_key'],
    api_key_primary_val=config['CLOVA']['api_key_primary_val'],
    request_id=config['CLOVA']['request_id']
)

# 네이버 CLOVA Face Recognition API 정보
client_id = 'j1vl4z56a0'
client_secret = 'ZXW9V04SINE1nHFMTEPmxqiDAnwn2nqKqOcEaIWL'
url = "https://naveropenapi.apigw.ntruss.com/vision/v1/face" 
headers = {'X-NCP-APIGW-API-KEY-ID': client_id, 'X-NCP-APIGW-API-KEY': client_secret }

preset_input = '가지고 있는 재료에 적합한 요리와 레시피를 추천해드립니다. (일부 재료는 추가될 수 있으며, 필요 없는 재료는 제외합니다.)\n필요한 재료의 양을 정확하게 알려 준다\n\n재료:계란, 밀가루, 아몬드 가루, 설탕\n-요리:마카롱\n-재료준비:계란 1개, 설탕 30g, 밀가루 3컵, 아몬드 약간\n-레시피:1. 체친 아몬드가루와 슈가파우더는 미리 섞어놓습니다.\n2. 계란흰자는 40초간 휘핑 후 설탕 30g를 한번에 넣고 천천히 휘핑합니다. 이어서  5분간 휘핑 후 색소를 넣고 추가로 1분간 휘핑합니다.\n3. 마카로나주를 하세요.\n4. 마카롱을 짜주머니에 놓고 테프론시트위에 짠후 오븐에 넣어 건조합니다.  50도 예열 후 5분 건조를 추천합니다.\n5. 낮은 석쇠에 팬을 넣고 240도로 예열을 합니다. 예열완료 소리가 나면 1분더 돌립니다.\n6. 예열 완료후 마카롱을 넣고 170도로 7분, 150도로 5분 돌려주세요'

# Streamlit 앱 생성
st.title('레시피 추천')

question = st.text_area(
    '재료', 
    placeholder='가지고 있는 음식 재료를 입력해 주세요  예)돼지고기, 김치, 호박', 
)

if preset_input and question:
    preset_text = f'{preset_input}\n\n###\n재료:{question}'

    request_data = {
        'text': preset_text,
        'maxTokens': 500,
        'temperature': 0.05,
        'topK': 0,
        'topP': 0.8,
        'repeatPenalty': 3.0,
        'start': '\n요리:',
        'stopBefore': ['###', '재료:', '###\n'],
        'includeTokens': True,
        'includeAiFilters': True,
        'includeProbs': False
    }

    response_text = completion_executor.execute(request_data)
    # print(preset_text)
    print(response_text)
#    st.markdown(response_text.split('###')[1])

    st.header("추천요리 : :blue["+response_text.split("###")[1].split("\n")[2].split(":")[1]+" ]")

    st.markdown(response_text.split("###")[1].split("\n")[3])
    st.markdown("-레시피:"+response_text.split("###")[1].split("-레시피:")[1])