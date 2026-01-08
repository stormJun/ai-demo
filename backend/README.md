# 职能沟通翻译助手 - 后端

基于 FastAPI 的后端服务,提供翻译、场景识别等 API。

## 快速开始

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 填写 QWEN_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
```

## Docker

```bash
docker build -t translator-backend .
docker run -d -p 8100:8100 -e QWEN_API_KEY=your_api_key translator-backend
```
