# Youtube Comment checker- BERT multilingual fine tuned

현재 버전: https://youtube-comment.streamlit.app

### optional) 추가하고 싶은 SPAM 값 지정
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/75a38393-5115-44ba-a020-4aa8db922c9d)


### 1. 유튜버의 아이디를 입력하고 동영상 리스트를 확인
---
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/21734961-4277-458b-9d5f-cbb4f42c0ba3)

### 2. 동영상 리스트 중 하나의 Value 값을 선택
---
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/c1a9141d-8013-46b9-921f-2c69b6f4bc62)

### 3. 중복이 제거된 댓글의 내용을 복사
---
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/a5bb4772-65c9-4f2e-85e6-7962ba6d2a16)

### 4. 유튜브 댓글의 내용을 찾아서 제거
---
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/e1e70d9b-ddf8-488d-a1b9-379d22c98f46)


---
# web 작동 확인
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/1cdd2118-b048-4be1-bf6a-775090769d51)



--- 
### problems..
BERT모델을 사용하면 작은 변동 랭솔팅배 -> 랭솔딩배 를 감지할 수 있지만
streamlit 서버 할당량이 적어서 받아오는 댓글의 수가 많을 경우 터져버림
현재는 어쩔 수 없이 MODEL을 사용하지 않는 APP2.PY를 사용해서 댓글 선별
