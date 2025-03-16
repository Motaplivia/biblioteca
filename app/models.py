from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Date, func
from sqlalchemy.orm import relationship
from .database import Base  

class Livro(Base):
    __tablename__ = 'livros'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    ano_publicacao = Column(Integer)
    isbn = Column(String, unique=True)
    quantidade = Column(Integer, default=1)
    exemplares_disponiveis = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    data_cadastro = Column(DateTime, default=func.now())

    categoria = relationship("Categoria", back_populates="livros")
    emprestimos = relationship("Emprestimo", back_populates="livro")

    def __init__(self, **kwargs):
        if 'quantidade' in kwargs:
            kwargs['exemplares_disponiveis'] = kwargs['quantidade']
        super().__init__(**kwargs)

    @property
    def disponivel(self):
        return self.exemplares_disponiveis > 0

    __table_args__ = {
        'extend_existing': True
    }

# Modelo para a tabela Categoria
class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    descricao = Column(String)

    # Relacionamento com a tabela Livro
    livros = relationship("Livro", back_populates="categoria")

# Modelo para a tabela Emprestimo
class Emprestimo(Base):
    __tablename__ = 'emprestimos'

    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey('livros.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    data_emprestimo = Column(Date, default=func.current_date())
    data_devolucao_prevista = Column(Date)
    data_devolucao_efetiva = Column(Date, nullable=True)
    status = Column(String, default="Ativo")

    livro = relationship("Livro", back_populates="emprestimos")
    usuario = relationship("Usuario", back_populates="emprestimos")

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    tipo = Column(String)  # Admin, Bibliotecário, Leitor
    data_registro = Column(DateTime, default=func.now())

    emprestimos = relationship("Emprestimo", back_populates="usuario")