# Youtube Comment checker- BERT multilingual fine tuned

현재 버전: https://youtube-comment.streamlit.app

### optional) 추가하고 싶은 SPAM 값 지정
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/75a38393-5115-44ba-a020-4aa8db922c9d)


# 1. 유튜버의 아이디를 입력 후 

## A-1: 동영상 리스트 확인 버튼(Check Videos)

![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/1b4331d9-037f-40e3-bffa-f53e982b9401)


## A-2: 동영상 리스트 중 하나의 Value 값을 선택

```참고) https://www.youtube.com/watch?v=65fCx-54N9w << 유튜브 동영상의 " = " 이후마지막 값 입니다```

![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/c1a9141d-8013-46b9-921f-2c69b6f4bc62)

## B: 최근 10개 동영상 검사 버튼 (Run 10Videos) --> 바로 확인 1~2분 소요
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/1b74c1da-23a0-4ab4-ac2a-afb722896e10)


## 2. 중복이 제거된 댓글의 내용을 복사
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/a5bb4772-65c9-4f2e-85e6-7962ba6d2a16)

## 3. 유튜브 댓글의 내용을 찾아서 제거
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/e1e70d9b-ddf8-488d-a1b9-379d22c98f46)
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/dc127fec-fcb7-4ea5-9e2b-549ca89a4c09)

## web 작동 확인
![image](https://github.com/doxgxxn/YTfinetunedBERT/assets/135602281/1cdd2118-b048-4be1-bf6a-775090769d51)



--- 
## problems..
BERT모델을 사용하면 작은 변동 랭솔팅배 -> 랭솔딩배 를 감지할 수 있지만
streamlit 서버 할당량이 적어서 받아오는 댓글의 수가 많을 경우 터져버림
현재는 어쩔 수 없이 MODEL을 사용하지 않는 APP2.PY를 사용해서 추가하고 싶은 SPAM 값을 추가하여 댓글 선별
