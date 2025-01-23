from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

# rotas categorias
@router.get("/categorias", response_model=List[schemas.Categoria])
def list_categorias(db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return categorias

@router.get("/categorias/{categoria_id}", response_model=schemas.Categoria)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return categoria

@router.post("/categorias", response_model=schemas.Categoria, status_code=status.HTTP_201_CREATED)
def add_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    new_categoria = models.Categoria(**categoria.dict())
    db.add(new_categoria)
    db.commit()
    db.refresh(new_categoria)
    return new_categoria

@router.put("/categorias/{categoria_id}", response_model=schemas.Categoria)
def update_categoria(categoria_id: int, updated_categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    
    for key, value in updated_categoria.dict(exclude_unset=True).items():
        setattr(categoria, key, value)
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/categorias/{categoria_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    db.delete(categoria)
    db.commit()
    return {"message": f"Categoria com ID {categoria_id} deletada com sucesso."}