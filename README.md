# KPT AI Manager

Notion KPT Database를 읽어 My GPT Actions에서 분석할 수 있도록 JSON으로 반환하는 FastAPI 서버입니다.

## Endpoints

- `/` : 서버 상태 확인
- `/health` : 헬스 체크
- `/kpt/items` : Notion KPT 데이터 조회

## Render 환경변수

- `NOTION_TOKEN` : Notion 연결 액세스 토큰
- `NOTION_DATA_SOURCE_ID` : KPT 데이터 원본 ID

## Render 설정

- Build Command

```bash
pip install -r requirements.txt
```

- Start Command

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## My GPT Action

`openapi.yaml` 파일의 서버 주소를 Render 주소로 바꾼 뒤 Actions에 붙여넣으세요.
