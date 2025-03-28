from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import date, timedelta
from ..auth import obter_usuario_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/livros-disponiveis")
async def listar_livros_disponiveis(
    request: Request,
    busca: str = None,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    query = db.query(models.Livro).filter(models.Livro.exemplares_disponiveis > 0)
    
    if busca:
        query = query.filter(models.Livro.titulo.ilike(f"%{busca}%"))
    
    livros = query.all()
    return templates.TemplateResponse(
        "leitor/livros_disponiveis.html",
        {
            "request": request,
            "livros": livros,
            "usuario": usuario_atual
        }
    )

@router.get("/livro/{livro_id}")
async def detalhes_livro(
    livro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Buscar resenhas do livro
    resenhas = db.query(models.Resenha).filter(models.Resenha.livro_id == livro_id).all()
    
    # Verificar se o usuário já tem este livro emprestado
    emprestimo_atual = db.query(models.Emprestimo).filter(
        models.Emprestimo.livro_id == livro_id,
        models.Emprestimo.usuario_id == usuario_atual.id,
        models.Emprestimo.data_devolucao_efetiva == None
    ).first()
    
    return templates.TemplateResponse(
        "leitor/detalhes_livro.html",
        {
            "request": request,
            "livro": livro,
            "resenhas": resenhas,
            "emprestimo_atual": emprestimo_atual,
            "usuario": usuario_atual
        }
    )

@router.post("/livro/{livro_id}/emprestar")
async def emprestar_livro(
    livro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    if livro.exemplares_disponiveis <= 0:
        return templates.TemplateResponse(
            "leitor/detalhes_livro.html",
            {
                "request": request,
                "livro": livro,
                "error": "Livro não disponível para empréstimo",
                "usuario": usuario_atual
            }
        )
    
    # Criar novo empréstimo
    novo_emprestimo = models.Emprestimo(
        livro_id=livro_id,
        usuario_id=usuario_atual.id,
        data_emprestimo=date.today(),
        data_devolucao_prevista=date.today() + timedelta(days=14),
        status="Ativo"
    )
    
    # Atualizar quantidade de exemplares disponíveis
    livro.exemplares_disponiveis -= 1
    
    db.add(novo_emprestimo)
    db.commit()
    
    return RedirectResponse(url="/meus-emprestimos", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/meus-emprestimos")
async def meus_emprestimos(
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    emprestimos = db.query(models.Emprestimo).filter(
        models.Emprestimo.usuario_id == usuario_atual.id
    ).all()
    
    return templates.TemplateResponse(
        "leitor/meus_emprestimos.html",
        {
            "request": request,
            "emprestimos": emprestimos,
            "usuario": usuario_atual
        }
    )

@router.post("/emprestimo/{emprestimo_id}/renovar")
async def renovar_emprestimo(
    emprestimo_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    emprestimo = db.query(models.Emprestimo).filter(
        models.Emprestimo.id == emprestimo_id,
        models.Emprestimo.usuario_id == usuario_atual.id,
        models.Emprestimo.data_devolucao_efetiva == None
    ).first()
    
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    # Renovar por mais 14 dias
    emprestimo.data_devolucao_prevista = date.today() + timedelta(days=14)
    db.commit()
    
    return RedirectResponse(url="/meus-emprestimos", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/livro/{livro_id}/resenha")
async def adicionar_resenha(
    livro_id: int,
    request: Request,
    texto: str = Form(...),
    avaliacao: int = Form(...),
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Verificar se o usuário já fez uma resenha para este livro
    resenha_existente = db.query(models.Resenha).filter(
        models.Resenha.livro_id == livro_id,
        models.Resenha.usuario_id == usuario_atual.id
    ).first()
    
    if resenha_existente:
        return templates.TemplateResponse(
            "leitor/detalhes_livro.html",
            {
                "request": request,
                "livro": livro,
                "error": "Você já fez uma resenha para este livro",
                "usuario": usuario_atual
            }
        )
    
    # Criar nova resenha
    nova_resenha = models.Resenha(
        livro_id=livro_id,
        usuario_id=usuario_atual.id,
        texto=texto,
        avaliacao=avaliacao,
        data_criacao=date.today()
    )
    
    db.add(nova_resenha)
    db.commit()
    
    return RedirectResponse(url=f"/livro/{livro_id}", status_code=status.HTTP_303_SEE_OTHER) 