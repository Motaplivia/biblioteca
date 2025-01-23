from pydantic import BaseModel

# Pydantic Models para Livro
class LivroBase(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int
    categoria_id: int

class Livro(LivroBase):
    id: int

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

    class Config:
        orm_mode = True

class EmprestimoCreate(EmprestimoBase):
    pass
