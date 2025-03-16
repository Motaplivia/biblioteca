from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models
from .database import engine, get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import RedirectResponse
from . import schemas
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.sql import func

from .routers.livros import router as routerLivros
from .routers.categorias import router as routerCategorias
from .routers.emprestimos import router as routerEmprestimos
from .routers.usuarios import router as routerUsuarios

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Criar as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routerLivros, tags=['livros'], prefix='/api')
app.include_router(routerCategorias, tags=['categorias'], prefix='/api')
app.include_router(routerEmprestimos, tags=['emprestimos'], prefix='/api')
app.include_router(routerUsuarios, tags=['usuarios'], prefix='/api')

@app.get("/", tags=["Root"])
def root(request: Request, db: Session = Depends(get_db)):
    # Total de livros
    total_livros = db.query(models.Livro).count()
    
    # Total de empréstimos ativos
    emprestimos_ativos = db.query(models.Emprestimo).filter(
        models.Emprestimo.status == "Ativo"
    ).count()
    
    # Total de empréstimos atrasados
    emprestimos_atrasados = db.query(models.Emprestimo).filter(
        models.Emprestimo.status == "Ativo",
        models.Emprestimo.data_devolucao_prevista < date.today()
    ).count()
    
    # Total de categorias
    total_categorias = db.query(models.Categoria).count()
    
    # Livros mais emprestados (top 5)
    livros_mais_emprestados = db.query(
        models.Livro.titulo,
        func.count(models.Emprestimo.id).label('total_emprestimos')
    ).select_from(models.Livro).join(
        models.Emprestimo
    ).group_by(
        models.Livro.id, models.Livro.titulo
    ).order_by(
        func.count(models.Emprestimo.id).desc()
    ).limit(5).all()
    
    # Categorias mais populares
    categorias_populares = db.query(
        models.Categoria.nome,
        func.count(models.Emprestimo.id).label('total_emprestimos')
    ).select_from(models.Categoria).join(
        models.Livro
    ).join(
        models.Emprestimo
    ).group_by(
        models.Categoria.id, models.Categoria.nome
    ).order_by(
        func.count(models.Emprestimo.id).desc()
    ).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_livros": total_livros,
        "emprestimos_ativos": emprestimos_ativos,
        "emprestimos_atrasados": emprestimos_atrasados,
        "total_categorias": total_categorias,
        "livros_mais_emprestados": {
            "labels": [livro[0] for livro in livros_mais_emprestados],
            "data": [livro[1] for livro in livros_mais_emprestados]
        },
        "categorias_populares": {
            "labels": [cat[0] for cat in categorias_populares],
            "data": [cat[1] for cat in categorias_populares]
        }
    })

# Livros
@app.get("/livros")
async def listar_livros(request: Request, busca: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Livro).options(joinedload(models.Livro.categoria))
    
    if busca:
        query = query.filter(models.Livro.titulo.ilike(f"%{busca}%"))
    
    livros = query.all()
    return templates.TemplateResponse("livros.html", {"request": request, "livros": livros})

@app.get("/livros/adicionar")
def add_livro_form(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return templates.TemplateResponse("adicionar_livro.html", {"request": request, "categorias": categorias})

@app.post("/livros/adicionar")
def add_livro(
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_publicacao: int = Form(...),
    isbn: str = Form(...),
    quantidade: int = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(get_db)
):
    new_livro = models.Livro(
        titulo=titulo,
        autor=autor,
        ano_publicacao=ano_publicacao,
        isbn=isbn,
        quantidade=quantidade,
        exemplares_disponiveis=quantidade,
        categoria_id=categoria_id,
        data_cadastro=datetime.now()
    )
    db.add(new_livro)
    db.commit()
    db.refresh(new_livro)
    return RedirectResponse(url="/livros", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/livros/editar/{livro_id}")
def edit_livro_form(livro_id: int, request: Request, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    categorias = db.query(models.Categoria).all()
    return templates.TemplateResponse("editar_livro.html", {"request": request, "livro": livro, "categorias": categorias})

@app.post("/livros/editar/{livro_id}")
def edit_livro(
    livro_id: int,
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_publicacao: int = Form(...),
    isbn: str = Form(...),
    quantidade: int = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(get_db)
):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Calcular a diferença de exemplares disponíveis
    diferenca_quantidade = quantidade - livro.quantidade
    exemplares_emprestados = livro.quantidade - livro.exemplares_disponiveis
    
    livro.titulo = titulo
    livro.autor = autor
    livro.ano_publicacao = ano_publicacao
    livro.isbn = isbn
    livro.quantidade = quantidade
    livro.exemplares_disponiveis = max(0, quantidade - exemplares_emprestados)
    livro.categoria_id = categoria_id
    
    db.commit()
    db.refresh(livro)
    return RedirectResponse(url="/livros", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/livros/deletar/{livro_id}")
def delete_livro_form(livro_id: int, request: Request, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return templates.TemplateResponse("deletar_livro.html", {"request": request, "livro": livro})

@app.post("/livros/deletar/{livro_id}")
def delete_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    db.delete(livro)
    db.commit()
    return RedirectResponse(url="/livros", status_code=status.HTTP_303_SEE_OTHER)

# Categorias
@app.get("/categorias")
async def listar_categorias(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return templates.TemplateResponse("categorias.html", {"request": request, "categorias": categorias})

@app.get("/categorias/adicionar")
def add_categoria_form(request: Request):
    return templates.TemplateResponse("adicionar_categoria.html", {"request": request})

@app.post("/categorias/adicionar")
def add_categoria(
    nome: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    new_categoria = models.Categoria(nome=nome, descricao=descricao)
    db.add(new_categoria)
    db.commit()
    db.refresh(new_categoria)
    return RedirectResponse(url="/categorias", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/categorias/editar/{categoria_id}")
def edit_categoria_form(categoria_id: int, request: Request, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return templates.TemplateResponse("editar_categoria.html", {"request": request, "categoria": categoria})

@app.post("/categorias/editar/{categoria_id}")
def edit_categoria(
    categoria_id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    
    categoria.nome = nome
    categoria.descricao = descricao
    
    db.commit()
    db.refresh(categoria)
    
    return RedirectResponse(url="/categorias", status_code=status.HTTP_303_SEE_OTHER)

# Deletar Categoria
@app.get("/categorias/deletar/{categoria_id}")
def delete_categoria_form(categoria_id: int, request: Request, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return templates.TemplateResponse("deletar_categoria.html", {"request": request, "categoria": categoria})

@app.post("/categorias/deletar/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    db.delete(categoria)
    db.commit()
    return RedirectResponse(url="/categorias", status_code=status.HTTP_303_SEE_OTHER)

# Empréstimos
@app.get("/emprestimos")
async def listar_emprestimos(request: Request, db: Session = Depends(get_db)):
    emprestimos = db.query(models.Emprestimo).options(
        joinedload(models.Emprestimo.livro),
        joinedload(models.Emprestimo.usuario)
    ).all()
    return templates.TemplateResponse("emprestimos.html", {"request": request, "emprestimos": emprestimos})

@app.get("/emprestimos/adicionar")
def add_emprestimo_form(request: Request, db: Session = Depends(get_db)):
    # Buscar apenas livros que têm exemplares disponíveis
    livros = db.query(models.Livro).filter(models.Livro.exemplares_disponiveis > 0).all()
    usuarios = db.query(models.Usuario).all()
    hoje = date.today().strftime('%Y-%m-%d')
    data_padrao = (date.today() + timedelta(days=14)).strftime('%Y-%m-%d')  # 14 dias para devolução
    return templates.TemplateResponse("adicionar_emprestimo.html", {
        "request": request,
        "livros": livros,
        "usuarios": usuarios,
        "hoje": hoje,
        "data_padrao": data_padrao
    })

@app.post("/emprestimos/adicionar")
async def adicionar_emprestimo(
    livro_id: int = Form(...),
    usuario_id: int = Form(...),
    data_devolucao_prevista: date = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar se o livro tem exemplares disponíveis
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro or livro.exemplares_disponiveis <= 0:
        raise HTTPException(status_code=400, detail="Livro não disponível para empréstimo")

    # Verificar se o usuário existe
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    # Verificar se a data de devolução é válida
    if data_devolucao_prevista <= date.today():
        raise HTTPException(status_code=400, detail="A data de devolução deve ser posterior à data atual")

    novo_emprestimo = models.Emprestimo(
        livro_id=livro_id,
        usuario_id=usuario_id,
        data_emprestimo=date.today(),
        data_devolucao_prevista=data_devolucao_prevista,
        status="Ativo"
    )

    # Atualizar quantidade de exemplares disponíveis
    livro.exemplares_disponiveis = max(0, livro.exemplares_disponiveis - 1)
    
    db.add(novo_emprestimo)
    db.commit()
    db.refresh(novo_emprestimo)
    return RedirectResponse(url="/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/emprestimos/{emprestimo_id}/devolver")
async def devolver_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db)
):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    if emprestimo.status != "Ativo":
        raise HTTPException(status_code=400, detail="Este empréstimo já foi finalizado")
    
    emprestimo.status = "Devolvido"
    emprestimo.data_devolucao_efetiva = date.today()
    
    # Atualizar quantidade de exemplares disponíveis
    livro = db.query(models.Livro).filter(models.Livro.id == emprestimo.livro_id).first()
    livro.exemplares_disponiveis = min(livro.quantidade, livro.exemplares_disponiveis + 1)
    
    db.commit()
    return RedirectResponse(url="/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/emprestimos/editar/{emprestimo_id}")
def edit_emprestimo_form(emprestimo_id: int, request: Request, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    return templates.TemplateResponse("editar_emprestimo.html", {"request": request, "emprestimo": emprestimo})

@app.post("/emprestimos/editar/{emprestimo_id}")
async def edit_emprestimo(
    emprestimo_id: int,
    livro_id: int = Form(...),
    usuario_id: int = Form(...),
    data_emprestimo: str = Form(...),
    data_devolucao: str = Form(...),
    db: Session = Depends(get_db)
):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    
    emprestimo.livro_id = livro_id
    emprestimo.usuario_id = usuario_id
    emprestimo.data_emprestimo = data_emprestimo
    emprestimo.data_devolucao = data_devolucao
    
    db.commit()
    db.refresh(emprestimo)
    
    return RedirectResponse(url="/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/emprestimos/deletar/{emprestimo_id}")
def delete_emprestimo_form(emprestimo_id: int, request: Request, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    return templates.TemplateResponse("deletar_emprestimo.html", {"request": request, "emprestimo": emprestimo})

@app.post("/emprestimos/deletar/{emprestimo_id}")
def delete_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    db.delete(emprestimo)
    db.commit()
    return RedirectResponse(url="/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

