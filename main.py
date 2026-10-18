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

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Catálogo e Inventario Pollería (5 Tablas)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint auxiliar para poblar los dropdowns en el formulario frontend
@app.get("/api/v1/catalogos")
def get_catalogos(db: Session = Depends(get_db)):
    medidas = db.query(models.Medida).all()
    tipos = db.query(models.TipoProducto).all()
    pollerias = db.query(models.Polleria).all()
    return {
        "medidas": [{"id": m.id_medida, "nombre": m.descripcion} for m in medidas],
        "tipos": [{"id": t.id_tipo_producto, "nombre": t.descripcion} for t in tipos],
        "pollerias": [{"id": p.id_polleria, "nombre": p.nombre} for p in pollerias]
    }

# GET: Listado combinando Producto + Medida + Tipo + Stock
@app.get("/api/v1/products", response_model=List[schemas.ProductoRead])
def list_products(db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    resultado = []
    for prod in productos:
        stock_val = sum([s.stock_actual for s in prod.stocks]) if prod.stocks else 0
        resultado.append(schemas.ProductoRead(
            id_producto=prod.id_producto,
            nombre=prod.nombre,
            descripcion=prod.descripcion,
            precio_venta=float(prod.precio_venta),
            categoria=prod.tipo_producto.descripcion if prod.tipo_producto else "General",
            medida=prod.medida.abreviatura if prod.medida else "UND",
            stock_actual=float(stock_val),
            image_url=prod.image_url
        ))
    return resultado

# POST: Crea el producto e inicializa su stock en la sucursal asignada
@app.post("/api/v1/products", status_code=status.HTTP_201_CREATED)
def create_product(prod: schemas.ProductoCreate, db: Session = Depends(get_db)):
    nuevo_prod = models.Producto(
        nombre=prod.nombre,
        descripcion=prod.descripcion,
        precio_venta=prod.precio_venta,
        id_medida=prod.id_medida,
        id_tipo_producto=prod.id_tipo_producto,
        image_url=prod.image_url
    )
    db.add(nuevo_prod)
    db.commit()
    db.refresh(nuevo_prod)

    # Registro simultáneo en tabla STOCK
    nuevo_stock = models.Stock(
        id_producto=nuevo_prod.id_producto,
        id_polleria=prod.id_polleria,
        stock_actual=prod.stock_inicial,
        stock_minimo=5
    )
    db.add(nuevo_stock)
    db.commit()

    # Integración con Slack (Herramienta 2)
    if SLACK_WEBHOOK_URL:
        try:
            requests.post(SLACK_WEBHOOK_URL, json={
                "text": f"🍗 *Nuevo Ítem en Menú:* {nuevo_prod.nombre} | Precio: Bs. {nuevo_prod.precio_venta} | Stock inicial: {prod.stock_inicial}"
            })
        except Exception:
            pass

    return {"message": "Producto y Stock creados exitosamente", "id": nuevo_prod.id_producto}