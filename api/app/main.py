from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from jose import jwt, JWTError
import re, requests, cloudscraper
from bs4 import BeautifulSoup

app = FastAPI()
SECRET = "secret" 

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

usuarios_lista: List[Usuario] = []

def criaUsuario(usuario: Usuario):
    usuarios_lista.append(usuario)

def buscaUsuario(email: str) -> Optional[Usuario]:
    for u in usuarios_lista:
        if u.email == email:
            return u
    return None

def verificaJWT(token: str) -> Optional[Usuario]:
    try:
        dados = jwt.decode(token, SECRET, algorithms=['HS256'])
        return Usuario(**dados)
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

@app.post("/registrar", response_model=JWTToken)
def registrar(usuario: Usuario):
    if buscaUsuario(usuario.email):
        raise HTTPException(status_code=409, detail="Usuário já registrado")
    criaUsuario(usuario)
    token = jwt.encode(usuario.dict(), SECRET, algorithm='HS256')
    return JWTToken(jwt=token)

@app.post("/login", response_model=JWTToken)
def login(credenciais: UsuarioLogin):
    user = buscaUsuario(credenciais.email)
    if not user or user.senha != credenciais.senha:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    token = jwt.encode(user.dict(), SECRET, algorithm='HS256')
    return JWTToken(jwt=token)

@app.get("/consultar", response_model=List[Crypto])
def consultar(jwt: str):
    if not verificaJWT(jwt):
        raise HTTPException(status_code=403, detail="JWT inválido ou expirado")
    return get_top10_expensive_cryptos_cmc()
