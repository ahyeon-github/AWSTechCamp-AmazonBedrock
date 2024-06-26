# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Video Shortform: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import streamlit as st
import requests
import boto3
import os


ALB_URL = os.environ.get('ALB_URL')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

API_URL = f'http://{ALB_URL}/shortform'


s3 = boto3.client('s3')

st.set_page_config(
    page_title='Gen AI - ShortForm',
)
st.title('비디오 숏폼')
model_name = """
*Anthropic Claude 3 Sonnet*
"""
st.info(f"""**사용 모델**
{model_name}""", icon='📙')

uploaded_file = st.file_uploader("파일을 선택하세요", type=['mp4'])


if uploaded_file is not None:
    st.video(uploaded_file)

summary_prompt = """
당신은 비디오 자막 스크립트의 요약 작업을 합니다.
<script> 에는 비디오에서 추출한 자막 스크립트가 있습니다.
<script> 에서 주요 키워드 10개를 추출하고, 요약을 만듭니다.
답변은 JSON 형식으로 출력합니다.
JSON 형식:
{    
    "요약": "요약",
    "주요 키워드": ["키워드", ...]
}
"""

st.success(f"""**자막 요약 Prompt**
{summary_prompt}""", icon='📌')

shorten_prompt = """
<script> 에는 WEBVTT 형식의 자막 스크립트가 있습니다.
<script> 에서 상품을 설명하는 부분만 선별합니다.
선별된 부분은 원본의 형식을 유지합니다.
선별된 부분의 각 스크립트의 시간은 2초를 넘어야 합니다.
선별된 부분을 연결했을 때 각 부분이 겹치지 말아야 하고 시간순으로 정렬되어야 합니다.
선별된 부분의 시간을 다 합치면 60초에서 90초가 되도록 만듭니다.
답변은 WEBVTT형식으로 츨력합니다.

<script>비디오 자막 스크립트</script>
"""

st.success(f"""**비디오 숏폼 Prompt**
{shorten_prompt}""", icon='📌')

with st.form('shortform_form', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Loading...'):
            if uploaded_file is None:
                st.error('파일을 선택하세요')
            else:                
                s3.upload_fileobj(
                    uploaded_file,
                    BUCKET_NAME,
                    f'videos/{uploaded_file.name}'
                )

                data = {'name': uploaded_file.name}
                response = requests.post(API_URL, json=data)

                result = response.json()
                print(result)

                st.json(result['summary'])
                print(result['shortened'])

                video_object = s3.get_object(Bucket=BUCKET_NAME, Key=result['shortened'])    
                st.video(video_object['Body'].read())

