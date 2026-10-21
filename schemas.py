from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Esquema para poblar selectores en el frontend
class CatalogosResponse(BaseModel):
    categorias: List[dict]
    medidas: List[dict]
    ludotecas: List[dict]

# Datos recibidos al registrar un juego/snack
class ProductCreate(BaseModel):
    name: str
    price: float
    id_categoria: int
    id_medida: int
    id_ludoteca: int = 1
    stock_inicial: int
    image_url: Optional[str] = None

# Datos devueltos combinando las 5 tablas para la tabla en Vercel
class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    categoria: str
    medida: str
    stock_actual: int
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)