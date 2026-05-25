from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.schemas.usuario import UsuarioCreate, Usuario, Token
from app.models.usuario import UsuarioDB
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])

@router.post("/register", response_model=Usuario)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe username o email
    if db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
    if db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed = get_password_hash(usuario.password)
    db_usuario = UsuarioDB(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed,
        rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}