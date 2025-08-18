
## 1️⃣ Create and Enter Project Directory

```bash
mkdir my_fastapi_project
cd my_fastapi_project
```

---

## 2️⃣ Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux / macOS
# OR
venv\Scripts\activate     # Windows
```

---

## 3️⃣ Install FastAPI and Uvicorn

```bash
pip install fastapi uvicorn
```

For API docs generation with Pydantic v2:

```bash
pip install pydantic[dotenv]
```

---

## 4️⃣ Create Your First App File

**`main.py`**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

---

## 5️⃣ Run the Server

```bash
uvicorn main:app --reload
```

* Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** → You’ll see `{"message": "Hello, FastAPI!"}`
* API docs are automatically at:

  * Swagger UI → `http://127.0.0.1:8000/docs`
  * ReDoc → `http://127.0.0.1:8000/redoc`

---

## 6️⃣ (Optional) Project Structure for Scalability

If you want it **ready for bigger projects**, use:

```
my_fastapi_project/
│── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │    ├── __init__.py
│   │    └── items.py
│   └── models/
│        ├── __init__.py
│        └── item.py
│── requirements.txt
```

Run:

```bash
pip freeze > requirements.txt
```

