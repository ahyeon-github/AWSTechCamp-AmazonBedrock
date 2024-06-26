# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Home: MIT-0
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

st.set_page_config(
    page_title="AWS TechCamp",
)

st.title('2024 AWS TechCamp Generative AI')


st.write(
    """
    안녕하세요. AWS TechCamp Generative AI 워크샾 페이지 입니다. 👋  
    본 워크샾에서는 쇼핑몰의 상품 리뷰들을 요약하는 방법과 
    10분 이상의 상품 소개 비디오를 1분 내외의 숏폼으로 만드는 방법에 대한 예시를 볼 수 있습니다. ✨
    """
)

st.info(
    """
    **Review Summary**  
    상품에 대한 리뷰들을 한번에 모아 분석해서 색상, 핏, 소재, 세탁, 가격등으로 유용한 정보를 요약합니다.
    """,
    icon="🩺",
)

st.success(
    """
    **Video Shortform**  
    상품 소개 비디오의 중요 포인트를 요약해서 1분 내외의 짧은 비디오로 만듭니다.
    """,
    icon="⏱️",
)
