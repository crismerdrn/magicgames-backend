import os
import requests
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

import models
import schemas
from database import engine, get_db

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Crea las tablas si no existen en Supabase
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Magic Games API - Ludoteca e Inventario (5 Tablas)",
    version="2.0.0",
    description="Backend modular conectado a PostgreSQL en Supabase con persistencia relacional"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def enviar_slack(mensaje: str):
    if SLACK_WEBHOOK_URL:
        try:
            requests.post(SLACK_WEBHOOK_URL, json={"text": mensaje}, timeout=5)
        except Exception as e:
            print(f"Error despachando Slack: {e}")

@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "sistema": "Magic Games API (5 Tablas Relacionales)",
        "administrador": "Carlos Ivan Salgado Flores",
        "docs": "/docs"
    }

# Endpoint para cargar categorías, medidas y sucursales en los selects del frontend
@app.get("/api/v1/catalogos", response_model=schemas.CatalogosResponse, tags=["Catálogos"])
def get_catalogos(db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    medidas = db.query(models.Medida).all()
    ludotecas = db.query(models.Ludoteca).all()
    return {
        "categorias": [{"id": c.id_categoria, "nombre": c.nombre} for c in categorias],
        "medidas": [{"id": m.id_medida, "nombre": f"{m.descripcion} ({m.abreviatura})"} for m in medidas],
        "ludotecas": [{"id": l.id_ludoteca, "nombre": l.nombre} for l in ludotecas]
    }

# GET: Consulta cruzada entre las 5 tablas
@app.get("/api/v1/products", response_model=List[schemas.ProductRead], tags=["Inventario"])
def list_products(db: Session = Depends(get_db)):
    productos = db.query(models.Product).order_by(models.Product.id.asc()).all()
    respuesta = []
    for prod in productos:
        total_stock = sum([s.stock_actual for s in prod.stocks]) if prod.stocks else 0
        respuesta.append(schemas.ProductRead(
            id=prod.id,
            name=prod.name,
            price=float(prod.price),
            categoria=prod.categoria.nombre if prod.categoria else "General",
            medida=prod.medida.abreviatura if prod.medida else "UND",
            stock_actual=total_stock,
            image_url=prod.image_url
        ))
    return respuesta

# POST: Transacción atómica en Product + Stock y alerta en Slack
@app.post("/api/v1/products", status_code=status.HTTP_201_CREATED, tags=["Inventario"])
def create_product(prod: schemas.ProductCreate, db: Session = Depends(get_db)):
    nuevo_producto = models.Product(
        name=prod.name,
        price=prod.price,
        id_categoria=prod.id_categoria,
        id_medida=prod.id_medida,
        image_url=prod.image_url
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    # Inserción en tabla Stock vinculada a la sucursal
    nuevo_stock = models.Stock(
        id_producto=nuevo_producto.id,
        id_ludoteca=prod.id_ludoteca,
        stock_actual=prod.stock_inicial,
        stock_minimo=2
    )
    db.add(nuevo_stock)
    db.commit()

    # Notificación inmediata al canal de Slack
    enviar_slack(
        f"🎲 *Nuevo Registro en Magic Games:* {nuevo_producto.name} | "
        f"Precio: Bs. {nuevo_producto.price:.2f} | "
        f"Stock ingresado: {prod.stock_inicial} unid/copias | "
        f"Resp: Carlos Ivan Salgado Flores"
    )

    return {"message": "Producto y Stock inicial registrados exitosamente", "id": nuevo_producto.id}