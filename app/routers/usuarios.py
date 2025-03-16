from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

@router.post("/usuarios/", response_model=schemas.Usuario)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    hashed_password = get_password_hash(usuario.senha)
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hashed_password,
        tipo=usuario.tipo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/usuarios/", response_model=List[schemas.Usuario])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def atualizar_usuario(usuario_id: int, usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o novo email já existe (se foi alterado)
    if usuario.email != db_usuario.email:
        email_exists = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email já registrado")
    
    db_usuario.nome = usuario.nome
    db_usuario.email = usuario.email
    db_usuario.tipo = usuario.tipo
    if usuario.senha:  # Só atualiza a senha se uma nova foi fornecida
        db_usuario.senha_hash = get_password_hash(usuario.senha)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o usuário tem empréstimos ativos
    emprestimos_ativos = db.query(models.Emprestimo).filter(
        models.Emprestimo.usuario_id == usuario_id,
        models.Emprestimo.status == "Ativo"
    ).first()
    
    if emprestimos_ativos:
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar um usuário com empréstimos ativos"
        )
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário deletado com sucesso"} 