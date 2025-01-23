from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from app import models
from .database import engine, get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from . import schemas

from .routers.livros import router as routerLivros
from .routers.categorias import router as routerCategorias
from .routers.emprestimos import router as routerEmprestimos

# Criar as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.include_router(routerLivros, tags=['livros'], prefix='/api')
app.include_router(routerCategorias, tags=['categorias'], prefix='/api')
app.include_router(routerEmprestimos, tags=['emprestimos'], prefix='/api')

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Livros
@app.get("/livros")
async def listar_livros(request: Request, db: Session = Depends(get_db)):
    livros = db.query(models.Livro).all()
    return templates.TemplateResponse("livros.html", {"request": request, "livros": livros})

@app.get("/livros/adicionar")
def add_livro_form(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()  # Recuperar todas as categorias
    return templates.TemplateResponse("adicionar_livro.html", {"request": request, "categorias": categorias})

@app.post("/livros/adicionar")
def add_livro(
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_publicacao: int = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(get_db)
):
    new_livro = models.Livro(titulo=titulo, autor=autor, ano_publicacao=ano_publicacao, categoria_id=categoria_id)
    db.add(new_livro)
    db.commit()
    db.refresh(new_livro)
    return RedirectResponse(url="/livros", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/livros/editar/{livro_id}")
def edit_livro_form(livro_id: int, request: Request, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    categorias = db.query(models.Categoria).all()  # Recuperar todas as categorias
    return templates.TemplateResponse("editar_livro.html", {"request": request, "livro": livro, "categorias": categorias})

@app.post("/livros/editar/{livro_id}")
def edit_livro(
    livro_id: int,
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_publicacao: int = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(get_db)
):
    existing_livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if existing_livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    existing_livro.titulo = titulo
    existing_livro.autor = autor
    existing_livro.ano_publicacao = ano_publicacao
    existing_livro.categoria_id = categoria_id
    
    db.commit()
    db.refresh(existing_livro)
    
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
    emprestimos = db.query(models.Emprestimo).all()
    return templates.TemplateResponse("emprestimos.html", {"request": request, "emprestimos": emprestimos})

@app.get("/emprestimos/adicionar")
def add_emprestimo_form(request: Request, db: Session = Depends(get_db)):
    livros = db.query(models.Livro).all()  # Recuperar todos os livros
    return templates.TemplateResponse("adicionar_emprestimo.html", {"request": request, "livros": livros})

@app.route('/emprestimos/adicionar', methods=['GET', 'POST'])
def adicionar_emprestimo():
    if request.method == 'POST':
        livro_id = request.form.get('livro_id')
        usuario = request.form.get('usuario')
        data_emprestimo = request.form.get('data_emprestimo')
        data_devolucao = request.form.get('data_devolucao')

        # Processa o empréstimo (salva no banco, validações, etc.)
        novo_emprestimo = Emprestimo(
            livro_id=livro_id,
            usuario=usuario,
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao
        )
        db.session.add(novo_emprestimo)
        db.session.commit()
        return redirect('/emprestimos')

    # Carregar livros do banco de dados
    livros = Livro.query.all()
    return render_template('adicionar_emprestimo.html', livros=livros)

@app.get("/emprestimos/editar/{emprestimo_id}")
def edit_emprestimo_form(emprestimo_id: int, request: Request, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    return templates.TemplateResponse("editar_emprestimo.html", {"request": request, "emprestimo": emprestimo})

@app.post("/emprestimos/editar/{emprestimo_id}")
def edit_emprestimo(
    emprestimo_id: int,
    livro_id: int = Form(...),
    cliente_nome: str = Form(...),
    data_emprestimo: str = Form(...),
    db: Session = Depends(get_db)
):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    
    emprestimo.livro_id = livro_id
    emprestimo.cliente_nome = cliente_nome
    emprestimo.data_emprestimo = data_emprestimo
    
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
