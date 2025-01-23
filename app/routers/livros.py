from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

# rotas livros
@router.get("/livros", response_model=List[schemas.Livro])
def list_livros(db: Session = Depends(get_db)):
    livros = db.query(models.Livro).all()
    return livros

@router.get("/livros/{livro_id}", response_model=schemas.Livro)
def get_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return livro

@router.post("/livros", response_model=schemas.Livro, status_code=status.HTTP_201_CREATED)
def add_livro(livro: schemas.LivroCreate, db: Session = Depends(get_db)):
    new_livro = models.Livro(**livro.dict())
    db.add(new_livro)
    db.commit()
    db.refresh(new_livro)
    return new_livro

@router.put("/livros/{livro_id}", response_model=schemas.Livro)
def update_livro(livro_id: int, updated_livro: schemas.LivroCreate, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    for key, value in updated_livro.dict(exclude_unset=True).items():
        setattr(livro, key, value)
    db.commit()
    db.refresh(livro)
    return livro

@router.delete("/livros/{livro_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    db.delete(livro)
    db.commit()
    return {"message": f"Livro com ID {livro_id} deletado com sucesso."}



