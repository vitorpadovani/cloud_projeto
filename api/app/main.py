from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from jose import jwt, JWTError
import re, requests, cloudscraper
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()
SECRET = "secret" 


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UsuarioDB(Base):
    __tablename__ = "usuarios" 
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)

Base.metadata.create_all(bind=engine)

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class JWTToken(BaseModel):
    jwt: str

class Crypto(BaseModel):
    name: str
    symbol: str
    price: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def criaUsuario(usuario: Usuario, db: Session):
    usuario_db = UsuarioDB(**usuario.dict())
    db.add(usuario_db)
    db.commit()
    db.refresh(usuario_db)


def buscaUsuario(email: str, db: Session) -> UsuarioDB | None:
    return db.query(UsuarioDB).filter(UsuarioDB.email == email).first()

def verificaJWT(token: str, db: Session) -> Usuario | None:
    try:
        dados = jwt.decode(token, SECRET, algorithms=['HS256'])
        usuario = buscaUsuario(dados['email'], db)
        if not usuario:
            return None
        return Usuario(nome=usuario.nome, email=usuario.email, senha=usuario.senha)
    except JWTError:
        return None

def _get_html(url: str, headers: dict) -> str:
    sess = requests.Session(); sess.headers.update(headers)
    resp = sess.get(url, timeout=20)
    if resp.status_code == 403:
        scraper = cloudscraper.create_scraper(browser={"custom": headers["User-Agent"]})
        resp = scraper.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text

def _parse_price(text: str) -> float:
    return float(re.sub(r"[^\d.]", "", text) or 0)

def get_top10_expensive_cryptos_cmc() -> List[Crypto]:
    url = "https://coinmarketcap.com/"
    headers = {
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/123.0.0.0 Safari/537.36"),
        "Accept-Language": "en-US,en;q=0.8",
    }

    soup = BeautifulSoup(_get_html(url, headers), "html.parser")
    rows = soup.select("table tbody tr")

    cryptos: List[Crypto] = []
    for row in rows:
        name_link = row.find("a", href=re.compile(r"^/currencies/"))
        price_tag = row.find("span", string=lambda s: s and s.strip().startswith("$"))
        if not (name_link and price_tag):
            continue
        symbol_tag = row.find("p", string=re.compile(r"^[A-Z0-9]{2,}$"))
        cryptos.append(
            Crypto(
                name=name_link.get_text(strip=True),
                symbol=symbol_tag.get_text(strip=True) if symbol_tag else "",
                price=_parse_price(price_tag.get_text())
            )
        )

    cryptos.sort(key=lambda c: c.price, reverse=True)
    return cryptos[:10]

# Endpoints
@app.post("/registrar", response_model=JWTToken)
def registrar(usuario: Usuario, db: Session = Depends(get_db)):
    if buscaUsuario(usuario.email, db):
        raise HTTPException(status_code=409, detail="Usuário já registrado")
    criaUsuario(usuario, db)
    token = jwt.encode(usuario.dict(), SECRET, algorithm='HS256')
    return JWTToken(jwt=token)

@app.post("/login", response_model=JWTToken)
def login(credenciais: UsuarioLogin, db: Session = Depends(get_db)):
    user = buscaUsuario(credenciais.email, db)
    if not user or user.senha != credenciais.senha:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    token = jwt.encode({"nome": user.nome, "email": user.email, "senha": user.senha}, SECRET, algorithm='HS256')
    return JWTToken(jwt=token)

@app.get("/consultar", response_model=List[Crypto])
def consultar(jwt: str, db: Session = Depends(get_db)):
    if not verificaJWT(jwt, db):
        raise HTTPException(status_code=403, detail="JWT inválido ou expirado")
    return get_top10_expensive_cryptos_cmc()
