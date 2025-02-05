# coordikitty-ML-DL
### 개요
- coordikitty는 사용자가 가진 의상에 기반해서 코디를 추천해주는 플랫폼을 개발하는 프로젝트

### 팀원
FE-WEB : [최은성](https://github.com/ches0703)  
FE-APP : [최서연](https://github.com/SyeonC)  
BE : [이태훈](https://github.com/Tentennball), [이호준](https://github.com/hotteok00)  
ML/DL : [정민관](https://github.com/minganin99), [김채일](https://github.com/LES8638)  

## :white_check_mark: 프로젝트 전체 구성도
![서버 구조도 drawio](https://github.com/user-attachments/assets/8b86d819-5d9f-4baa-9d13-8df79ef3c201)

### 주요 기능
- 자신의 옷장에 있는 옷을 등록하여 해당 옷을 기반으로 날씨/스타일에 따라 코디를 추천받는 플랫폼
- 자신의 코디를 post에 게시하여 커뮤니티 기능 활성화(개발중)
- post에 있는 옷들 + 옷장에 있는 옷 기반으로 날씨/스타일에 따라 코디 추천(개발중)
- 기본 auth기능(회원가입/로그인/로그아웃/회원탈퇴)

# 패션 추천 시스템

이 프로젝트는 Selenium을 사용하여 무신사에서 다양한 카테고리의 의류 이미지를 수집하고, 자동으로 라벨링 파일을 JSON 형식으로 생성. 또한, ResNeXt 아키텍처를 통해 수집된 의류 이미지를 학습하고, 입력된 이미지에 대해 스타일을 분류하는 모델을 구축.
## 개발환경
- VSC
- JupyterNotebook
## 주요 기능

### 1. 이미지 수집 및 라벨링
- **Selenium**을 활용하여 무신사 웹사이트에서 의류 이미지를 수집.
- 수집된 이미지에 대한 라벨링을 자동으로 수행하고, 결과는 **JSON 파일**로 저장.

### 2. 스타일 분류
- **ResNeXt 아키텍처**를 사용하여 의류 이미지를 학습하고, 입력된 이미지에 대해 스타일을 분류하는 모델을 학습.

### 3. 옷 추천 알고리즘
- **날씨 기반 추천**: 사용자의 위치에 따라 현재 온도와 의류의 두께를 확인하여 적합한 코디를 추천.
- **스타일 기반 추천**: 사용자가 선호하는 스타일에 맞추어 코디를 추천.

### 4. 인기 게시글 활용
- 코디 추천 시, 인기 게시글에서 코디를 불러와 비슷한 의류로 추천.
- 이 과정에서 **YOLOv5 모델**을 사용하여 게시글의 상의와 하의를 분리.
- **YOLOv5 모델**은 이미 사람을 감지하는 모델에서 상의/하의를 분리하는 모델로 전이학습

### 5. 알고리즘 흐름도
<img width="1442" alt="알고리즘 흐름도" src="https://github.com/user-attachments/assets/31e2c0c8-2727-43d1-a0a6-e5254ab069b0">


