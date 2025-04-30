# Objetivo
API RESTful que deve ser capaz de cadastrar e autenticar usuários


# Para rodar o projeto
pip install -r api/requirements.txt

python3 -m venv venv

source venv/bin/activate

.\venv\Scripts\Activate.ps1 # Windows

# Para rodar o projeto
fastapi dev api/app/main.py

docker build -t minha-api ./api 
docker compose up

# Para criar a minha imagem docker
docker tag minha-api vitorpadova/projeto_cloud
docker images
docker push vitorpadova/projeto_cloud

## ou
docker rmi vitorpadova/projeto_cloud
docker images
docker pull vitorpadova/projeto_cloud

https://hub.docker.com/r/vitorpadova/projeto_cloud
