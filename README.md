# Interface Gráfica Farmácia API

---

## Como Clonar

1. **Clone o Repositório**:
   - No terminal, execute o comando abaixo para clonar a branch específica do projeto:   
   ```
   git clone --branch jinja2 https://github.com/Leititcia/farmaAPI.git
   ```

2. **Crie e Ative um Ambiente Virtual**:
   - Com o diretório do projeto aberto crie o ambiente virtual com o comando abaixo:
    ```bash
      python -m venv venv
     ```
      - Para ativar
          - No windows:
            ```bash
              venv\Scripts\activate
             ```
          - No Linux/macOS:
            ```bash
              source venv/bin/activate
             ```

4. **Instale as Dependências**:
    ```bash
    pip install -r requirements.txt
    ```
     
5. **Execute a API**:
     ```bash
     uvicorn app.main:app --reload
     ```

---

## Autora
Letícia Vale.
