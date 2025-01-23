from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Livro(Base):
    __tablename__ = 'livros'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    ano_publicacao = Column(Integer)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # Relacionamento com a tabela Categoria
    categoria = relationship("Categoria", back_populates="livros")

# Modelo para Categoria
from sqlalchemy import Column, Integer, String
from .database import Base

class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    descricao = Column(String)

    # Relacionamento com a tabela Livro
    livros = relationship("Livro", back_populates="categoria")

class Emprestimo(Base):
    __tablename__ = 'emprestimos'

    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey('livros.id'))
    cliente_nome = Column(String, index=True)
    data_emprestimo = Column(String, index=True)

    livro = relationship("Livro")
