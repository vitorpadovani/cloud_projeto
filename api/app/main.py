from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import base64
import requests
from jose import jwt

app = FastAPI()

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class JWTToken(BaseModel):
    jwt: str


# lista global para armazenar usuários
usuarios_lista = []

# cria um usuário e o armazena em uma lista
def criaUsuario(usuario: Usuario) -> Usuario:
    usuarios_lista.append(usuario)
    print(f"Usuário {usuario.nome} criado com sucesso!")
    return usuario


# verifica o JWT e retorna o usuário correspondente
def verificaJWT(token) -> Optional[Usuario]:
    try:
        decodificado = jwt.decode(token, 'secret', algorithms=['HS256'])
        return Usuario(
            nome=decodificado["nome"],
            email=decodificado["email"],
            senha=decodificado["senha"]
        )
    
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None


# registra um novo usuário
@app.post("/registrar", response_model=JWTToken)
def registrar(usuario: Usuario) -> JWTToken:
    if usuario in usuarios_lista:
        raise HTTPException(status_code=409, detail="Usuário já registrado")
    
    payload = {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": usuario.senha
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    return JWTToken(jwt=token)

# faz login do usuário e retorna um JWT
@app.post("/login", response_model=JWTToken)
def login(usuario: UsuarioLogin) -> JWTToken:
    if not usuario.email or not usuario.senha:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    payload = { 
        "email": usuario.email,
        "senha": usuario.senha
    }
    
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return JWTToken(jwt=token)

# consulta o usuário com base no JWT
@app.get("/consultar", response_model=Usuario)
def consultar(jwt: str) -> Usuario:
    usuario = verificaJWT(jwt)
    if usuario:
        return usuario
    else:
        #erro 403
        raise HTTPException(status_code=403, detail="JWT inválido ou expirado")

