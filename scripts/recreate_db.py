from app.database import recreate_database, SessionLocal
from app.models import Categoria, Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_dados_iniciais():
    db = SessionLocal()
    try:
        # Criar categorias iniciais
        categorias = [
            Categoria(nome="Romance", descricao="Livros de romance"),
            Categoria(nome="Ficção", descricao="Livros de ficção"),
            Categoria(nome="Não Ficção", descricao="Livros de não ficção"),
            Categoria(nome="Técnico", descricao="Livros técnicos")
        ]
        db.add_all(categorias)
        
        # Criar usuário administrador
        admin = Usuario(
            nome="Administrador",
            email="admin@biblioteca.com",
            senha_hash=pwd_context.hash("admin"),
            tipo="Admin"
        )
        db.add(admin)
        
        db.commit()
    except Exception as e:
        print(f"Erro ao criar dados iniciais: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Recriando o banco de dados...")
    recreate_database()
    print("Criando dados iniciais...")
    criar_dados_iniciais()
    print("Banco de dados recriado com sucesso!") 