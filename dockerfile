# Usando a imagem oficial do Python como base
FROM python:3.10-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos do projeto para o contêiner
COPY . /app

# Instalando dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expondo a porta em que o FastAPI estará rodando
EXPOSE 8000

# Comando para rodar o servidor da FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
