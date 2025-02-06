from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base  

# Modelo para a tabela Livro
class Livro(Base):
    __tablename__ = 'livros'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    ano_publicacao = Column(Integer)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # Relacionamento com a tabela Categoria
    categoria = relationship("Categoria", back_populates="livros")

    # Relacionamento com a tabela Emprestimo
    emprestimos = relationship("Emprestimo", back_populates="livro")

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
    cliente_nome = Column(String, index=True)
    data_emprestimo = Column(String, index=True)

    # Relacionamento com a tabela Livro
    livro = relationship("Livro", back_populates="emprestimos")
