from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
from datetime import date, datetime

# Pydantic Models para Livro
class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100, description="Título do livro")
    autor: str = Field(..., min_length=1, max_length=100, description="Nome do autor")
    ano_publicacao: int = Field(..., ge=1000, le=date.today().year, description="Ano de publicação")
    isbn: str = Field(..., min_length=10, description="ISBN do livro")
    quantidade: int = Field(default=1, ge=1, description="Quantidade total")
    exemplares_disponiveis: Optional[int] = Field(None, ge=0, description="Quantidade disponível para empréstimo")
    categoria_id: int = Field(..., gt=0, description="ID da categoria")
    
    @validator('titulo')
    def titulo_nao_vazio(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Título não pode estar vazio')
        return v
    
    @validator('autor')
    def autor_nao_vazio(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Nome do autor não pode estar vazio')
        return v
    
    @validator('exemplares_disponiveis')
    def validar_exemplares_disponiveis(cls, v, values):
        if v is None and 'quantidade' in values:
            return values['quantidade']
        if v is not None and 'quantidade' in values and v > values['quantidade']:
            raise ValueError('Exemplares disponíveis não pode ser maior que a quantidade total')
        return v

class LivroCreate(LivroBase):
    pass

class Livro(LivroBase):
    id: int
    disponivel: bool
    data_cadastro: datetime
    
    class Config:
        from_attributes = True

class LivroFull(Livro):
    categoria: Optional['CategoriaSimples'] = None

# Pydantic Models para Categoria
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50, description="Nome da categoria")
    descricao: str = Field(..., min_length=1, max_length=200, description="Descrição da categoria")
    
    @validator('nome')
    def nome_nao_vazio(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Nome da categoria não pode estar vazio')
        return v

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaSimples(CategoriaBase):
    id: int
    
    class Config:
        from_attributes = True

class Categoria(CategoriaSimples):
    livros: List[Livro] = []

# Pydantic Models para Usuario
class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    tipo: str = Field(..., description="Tipo do usuário (Admin, Bibliotecário, Leitor)")

    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["Admin", "Bibliotecário", "Leitor"]
        if v not in tipos_validos:
            raise ValueError(f'Tipo deve ser um dos seguintes: {", ".join(tipos_validos)}')
        return v

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha do usuário")

class Usuario(UsuarioBase):
    id: int
    data_registro: datetime

    class Config:
        from_attributes = True

# Pydantic Models para Emprestimo
class EmprestimoBase(BaseModel):
    livro_id: int = Field(..., gt=0, description="ID do livro")
    usuario_id: int = Field(..., gt=0, description="ID do usuário")
    data_devolucao_prevista: date = Field(..., description="Data de devolução prevista")
    
    @validator('data_devolucao_prevista')
    def data_devolucao_posterior(cls, v):
        if v < date.today():
            raise ValueError('A data de devolução prevista deve ser posterior à data atual')
        return v

class EmprestimoCreate(EmprestimoBase):
    pass

class Emprestimo(EmprestimoBase):
    id: int
    data_emprestimo: date
    data_devolucao_efetiva: Optional[date] = None
    status: str = Field(..., description="Status do empréstimo (Ativo, Devolvido, Atrasado)")
    
    class Config:
        from_attributes = True

class EmprestimoFull(Emprestimo):
    livro: Optional[Livro] = None
    usuario: Optional[Usuario] = None