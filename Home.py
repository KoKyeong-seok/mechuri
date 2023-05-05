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
        self._request_id = request_id

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

preset_input = '사용자 나이, 집밥 또는 외식 메뉴, 성별, 감정, 제철재료 등을 감안하여 음식 메뉴, 감성추천문구, 레시피 추천해서 알려주시오\n\n질문:나이:20~25, 집밥 메뉴, 성별:male, 감정:neutral\n답:-김치찌개\n-추천문구:한국인의 최애 음식!\n-레시피: 1. 김치를 준비한다\n             2. 김치를 잘게 잘라 볶는다\n             3. 기타 채소를 넣고 끓인다\n             4. 맛있게 먹는다\n-주변맛집:둔산동 할머니 김치찌개'

# Streamlit 앱 생성
st.title('AI 메뉴 추천')

option = st.radio(
    "외식메뉴?",
    ('외식메뉴', '집밥메뉴'))

question = ''

picture = st.camera_input("얼굴 사진을 찍어주세요")

# 이미지 전송 및 결과 반환
if picture:
 #   st.image(picture, caption="촬영한 얼굴사진", use_column_width=True)
    img = Image.open(picture)
    img.save('picture.jpg') # 이미지를 저장
    
    files = {'image': open('picture.jpg', 'rb')}
    response = requests.post(url,  files=files, headers=headers)
    result = response.json()

#    st.write('인식 결과')
 
    if 'faces' in response.json():
            result = response.json()['faces']

            for face in result:
               # st.write("성별:", face['gender']['value'])
               # st.write("나이:", face['age']['value'])
               # st.write("표정:", face['emotion']['value'])
                question = "나이:"+face['age']['value']+", "+option+",  성별:"+face['gender']['value']+", 기분:"+face['emotion']['value']

if preset_input and question:
    preset_text = f'{preset_input}\n\n###질문:{question}'

    request_data = {
        'text': preset_text,
        'maxTokens': 150,
        'temperature': 0.5,
        'topK': 0,
        'topP': 0.8,
        'repeatPenalty': 5.0,
        'start': '\n###답:',
        'stopBefore': ['###', '질문:', '답:', '###\n'],
        'includeTokens': True,
        'includeAiFilters': True,
        'includeProbs': True
    }

    response_text = completion_executor.execute(request_data)
    # print(preset_text)

    print(response_text.split('###답:')[1])  

    st.header(response_text.split("###답:")[1].split('-')[2].split(':')[1])

    st.subheader("추천메뉴 : :blue["+response_text.split("###답:")[1].split("\n")[0].split('-')[1]+"]")

    st.markdown(response_text.split("###답:")[1].split("-")[3]) 
    st.markdown(response_text.split("###답:")[1].split("-")[4]) 


 

 #   st.markdown(response_text.split("답: -")[1].split("\n")[0]) 
 

 #   filename = response_text.split("답: -")[1].split("\n")[0] 

 #   if os.path.isfile("img/"+filename+".jpg"):
 #       image = Image.open("img/"+filename+".jpg")
 #       st.image(image)