from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import engine, Base, get_db
from .models import User
from .schemas import UserCreate, UserOut, Token, ChatRequest, ChatResponse
from . import auth
from .config import settings
from . import ai
from . import payments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI SaaS MVP Template", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ---- Auth helpers ----


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise cred_exc
    return user


# ---- Routes ----


@app.post("/auth/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        hashed_password=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token}


@app.post("/auth/login", response_model=Token)
def login(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token}


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest, user: User = Depends(get_current_user)
):
    try:
        reply = await ai.ask_ai(req.message)
    except ai.AIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"reply": reply}


@app.post("/billing/checkout")
def checkout(user: User = Depends(get_current_user)):
    try:
        url = payments.create_checkout_session(user.email)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e}")
    return {"url": url}


@app.post("/billing/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = payments.verify_webhook(payload, sig)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")
    if event.get("type") == "checkout.session.completed":
        email = event["data"]["object"].get("customer_email")
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.is_premium = True
            db.commit()
    return JSONResponse({"status": "ok"})


# ---- Frontend ----
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    with open("app/static/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health():
    return {"status": "ok"}
