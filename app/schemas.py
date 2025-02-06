from pydantic import BaseModel
from typing import List, Optional

# Pydantic Models para Livro
class LivroBase(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int
    categoria_id: int

class Livro(LivroBase):
    id: int
    categoria: Optional['Categoria']  # Relacionamento com Categoria

    class Config:
        orm_mode = True

class LivroCreate(LivroBase):
    pass

# Pydantic Models para Categoria
class CategoriaBase(BaseModel):
    nome: str
    descricao: str

class Categoria(CategoriaBase):
    id: int
    livros: List[Livro] = []  # Lista de livros relacionados

    class Config:
        orm_mode = True

class CategoriaCreate(CategoriaBase):
    pass

# Pydantic Models para Emprestimo
class EmprestimoBase(BaseModel):
    livro_id: int
    cliente_nome: str
    data_emprestimo: str

class Emprestimo(EmprestimoBase):
    id: int
    livro: Livro  # Relacionamento com o livro

    class Config:
        orm_mode = True

class EmprestimoCreate(EmprestimoBase):
    pass
