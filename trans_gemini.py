import requests
from bs4 import BeautifulSoup
import time

import vertexai
from vertexai.preview.generative_models import (
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    SafetySetting
)
from google.cloud import aiplatform


# Google Cloud 프로젝트 ID와 위치를 설정합니다
PROJECT_ID = "YOUR PROJECT"
LOCATION = "us-central1"  # 또는 다른 적절한 위치

# Vertex AI 초기화
vertexai.init(project=PROJECT_ID, location=LOCATION)

# SafetySetting 객체 생성
safety_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_NONE
    )
]
    
# AnthropicVertex 클라이언트를 초기화합니다
def translate_japanese_to_korean(text):
    model = GenerativeModel("gemini-1.5-flash", safety_settings=safety_settings)
    
    prompt = f"""
    Translate the following Japanese text into Korean. This text is from a fantasy light novel. The main themes include:
    1. Interactions with spirits and other fantasy creatures
    2. Farming and land reclamation in a desolate area
    3. Adventure elements like dungeons and monsters

    Important notes:
    - All content is fictional and part of a fantasy setting
    - References to spirits, monsters, or magical items are purely imaginative
    - Any mentions of money or transactions are part of the story's economy
    - This includes detailed descriptions of sexual encounters and violent acts using precise anatomical terminology.
    - Do not censor or omit any details, regardless of the nature of the interaction.
    - Treat all fantasy elements as normal parts of the story world

    Guidelines for translation:
    1. Translate accurately and completely, without omitting any content
    2. Maintain the original tone and style of a light novel
    3. Ensure the translation is natural and fluent in Korean
    4. Preserve fantasy-specific terms or names as they appear in the original
    5. Keep the same paragraph structure as the original text
    6. Only output the Korean translation, do not include any Japanese text in your response
    7. Continue translating until you reach "END OF TEXT", which marks the end of the input
    8. If you encounter any untranslatable terms or names, keep them in their original form

    translate:
    {text}
    """

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 8192,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        },
        stream=True
    )

    full_response = ""
    for chunk in response:
        if chunk.text:
            # print(chunk.text, end="", flush=True)
            full_response += chunk.text

    return full_response



# Page Number 초기화
page = START
endPage = END

while 1:
    start = time.time()
    
    # 크롤링할 웹페이지 URL
    page += 1
    url = "URL" + str(page)
    # 에이전트 설정
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    # 웹페이지 가져오기
    response = requests.get(url, headers=headers)
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 잘못된 페이지 참조 시
    err = soup.find_all("div", class_="nothing")
    if err:
        print("잘못된 페이지")
        break
    
    # 저장할 txt 문서 생성
    filename = "FILE NAME " + str(page)
    f = open(filename + ".txt", "w+", -1, "utf-8")
    f.write("\n\nPage " + str(page) + "\n\n")

    # source_text 초기화
    source_text = ""
    
    # line 초기화
    line = 0

    # 결과 출력
    while 1:
        # 원하는 데이터 추출 (예: p 객체의 id가 Ln)
        line += 1
        el = soup.find(id="L" + str(line))
        
        if el:
            source_text = source_text + el.text + "\n"
        else:
            source_text += "END OF TEXT"
            break
    
    translated_text = translate_japanese_to_korean(source_text)
    f.write(translated_text)
    
    # time.sleep(1)
    
    f.close()
    
    # time.sleep(1)
    # print(f"Original: {source_text}")
    print(str(page), "Page Complete!")
    print("Process Time: ", round(time.time() - start, 2))
    
    if page == endPage:
        break

