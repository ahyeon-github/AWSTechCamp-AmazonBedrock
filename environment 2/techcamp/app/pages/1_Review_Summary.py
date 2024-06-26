# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Review Summary: MIT-0
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
import os


ALB_URL = os.environ.get('ALB_URL')
API_URL = f'http://{ALB_URL}/summary'

st.set_page_config(
    page_title='Gen AI - Summarization',
)
st.title('상품 리뷰 요약')
model_name = """
*Anthropic Claude 3 Sonnet*
"""
st.info(f"""**사용 모델**
{model_name}""", icon='📙')

st.write('판매자에게 유용한 정보를 색상, 핏, 소재, 세탁, 가격으로 요약합니다.')

reviews = st.text_area('Enter reviews', '', height=200)

summary_prompt = """
당신은 상품 판매자입니다.
<review> 는 상품 구매자들이 작성한 것입니다.
<review> 를 읽고 판매자에게 유용한 정보를 색상, 핏, 소재, 세탁, 가격으로 요약합니다.

<review>상품 리뷰들</review>
"""
st.success(f"""**사용하는 Prompt**
{summary_prompt}""", icon='📌')

with st.form('review_summary_form', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Loading...'):
            data = {'body': reviews}
            response = requests.post(API_URL, json=data)
            st.info(response.text)


st.markdown('\n')
st.markdown('### 상품 리뷰 (복사하여 위의 입력창에 붙여넣으세요) ')
st.code("""
1. 핏이 좋고 편안합니다.하지만 세탁 후 색이 번졌어요.그리고 권장대로 세탁했어요.
이제 사방에 커다란 분홍색 얼룩이 생겼어요.
2. 너무 편안하고 귀엽고 스타일리시합니다.마음에 들어요!
3. 이 스웨터가 마음에 들어요.소재는 훌륭하지만 조금 짧았습니다.
4. 분명히 위험하다는 건 알았지만 다른 사람들에게서 봤을 때 위글 공간이 조금 더 있을지도 모른다고 생각했지만 XL이 생겼고 예상대로 더 오버사이즈였으면 좋겠어요.
그러니 덩치가 큰 제 딸들에게는 생각처럼 오버사이즈가 아니라는 걸 명심하세요!아직 엄청 귀엽고 부드러워요. 하지만 이거 자연 건조할게요!!!
5. 마음에 들어요, 멋진 오버사이즈 핏, 귀여운 색상!!
""")
