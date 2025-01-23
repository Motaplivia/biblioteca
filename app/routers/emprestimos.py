from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

# rotas empréstimos
@router.get("/emprestimos", response_model=List[schemas.Emprestimo])
def list_emprestimos(db: Session = Depends(get_db)):
    emprestimos = db.query(models.Emprestimo).all()
    return emprestimos

@router.get("/emprestimos/{emprestimo_id}", response_model=schemas.Emprestimo)
def get_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    return emprestimo

@router.post("/emprestimos", response_model=schemas.Emprestimo, status_code=status.HTTP_201_CREATED)
def add_emprestimo(emprestimo: schemas.EmprestimoCreate, db: Session = Depends(get_db)):
    new_emprestimo = models.Emprestimo(**emprestimo.dict())
    db.add(new_emprestimo)
    db.commit()
    db.refresh(new_emprestimo)
    return new_emprestimo

@router.put("/emprestimos/{emprestimo_id}", response_model=schemas.Emprestimo)
def update_emprestimo(emprestimo_id: int, updated_emprestimo: schemas.EmprestimoCreate, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    
    for key, value in updated_emprestimo.dict(exclude_unset=True).items():
        setattr(emprestimo, key, value)
    db.commit()
    db.refresh(emprestimo)
    return emprestimo

@router.delete("/emprestimos/{emprestimo_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    db.delete(emprestimo)
    db.commit()
    return {"message": f"Empréstimo com ID {emprestimo_id} deletado com sucesso."}
