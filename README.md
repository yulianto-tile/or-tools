# FastAPI with Google OR-Tools

API untuk optimization menggunakan Google OR-Tools

## Endpoints

- `GET /` - Info API
- `GET /health` - Health check
- `POST /solve-vrp` - Vehicle Routing Problem
- `POST /solve-linear` - Linear Programming

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
