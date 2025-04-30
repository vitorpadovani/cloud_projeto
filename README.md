# Projeto: API RESTful com Cadastro e Autenticação de Usuários

# **Documentação e Descrição do Projeto**
🔗 Link da página:  
[https://vitorpadovani.github.io/CloudJ/projeto/main/](https://vitorpadovani.github.io/CloudJ/projeto/main/)

Este projeto é uma **API RESTful** desenvolvida com FastAPI, capaz de **cadastrar** e **autenticar usuários**, com persistência de dados em um banco PostgreSQL via Docker.

---

##  Como rodar o projeto localmente

### 1. Instale as dependências
```bash
pip install -r api/requirements.txt
```

### 2. Crie e ative o ambiente virtual

#### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.venv\Scripts\Activate.ps1
```

### 3. Execute a API (modo desenvolvimento)
```bash
fastapi dev api/app/main.py
```

---

##  Como rodar o projeto com Docker

### 1. Build da imagem
```bash
docker build -t minha-api ./api
```

### 2. Suba os containers
```bash
docker compose up -d
```

---

##  Docker Hub

### Enviar imagem para o Docker Hub
```bash
docker tag minha-api vitorpadova/projeto_cloud
docker push vitorpadova/projeto_cloud
```

### Ver e remover imagens
```bash
docker images
docker rmi vitorpadova/projeto_cloud
```

### Baixar imagem (pull)
```bash
docker pull vitorpadova/projeto_cloud
```

🔗 Link da imagem:  
[https://hub.docker.com/r/vitorpadova/projeto_cloud](https://hub.docker.com/r/vitorpadova/projeto_cloud)

---

## Acessando o banco de dados no container

1. No terminal, entre no container do banco de dados:
```bash
psql -U usuario -d meu_banco 
```

2. Comandos úteis no `psql`:
```sql
-- Listar tabelas
\dt

-- Visualizar dados da tabela 'usuarios'
SELECT * FROM usuarios;
```

