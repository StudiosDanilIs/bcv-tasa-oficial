# bcv_api.py

"""
BCV-API
Desarrollado por Studios Daniels
Licencia MIT (https://opensource.org/licenses/MIT)
"""

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

# --- Configuración de la API ---
app = FastAPI(
    title="BCV-API",
    description="API que proporciona las tasas de cambio oficiales del Banco Central de Venezuela.",
    version="1.0.0"
)

# --- Modelo de datos (Pydantic) ---
class Tasa(BaseModel):
    valor: str
    fecha: str

class TasasOficiales(BaseModel):
    dolar: Tasa
    euro: Tasa
    otras: dict

# --- Cache de datos ---
cache_data = None
cache_timestamp = None
CACHE_DURATION_MINUTES = 30  # Actualizar datos cada 30 minutos

# --- Lógica de Web Scraping ---
def obtener_tasas_bcv():
    """
    Función que extrae las tasas de cambio del sitio web del BCV.
    """
    url = 'https://www.bcv.org.ve/'
    print("Obteniendo tasas desde el BCV...")

    # Ignora la verificación SSL.
    session = requests.Session()
    session.verify = False

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tasas = {
            "dolar": None,
            "euro": None,
            "otras": {}
        }

        # Extraer Dólar y Euro
        for div_id in ['dolar', 'euro']:
            container = soup.find('div', id=div_id)
            if container:
                valor = container.find('strong').text.strip()
                fecha = container.find('span').text.strip()
                tasas[div_id] = {"valor": valor, "fecha": fecha}

        # Extraer otras divisas
        otras_divisas_container = soup.find('div', class_='col-sm-6 col-xs-6')
        if otras_divisas_container:
            for card in otras_divisas_container.find_all('div', class_='col-sm-4'):
                nombre_divisa_tag = card.find('p', class_='name')
                valor_divisa_tag = card.find('strong')
                if nombre_divisa_tag and valor_divisa_tag:
                    nombre = nombre_divisa_tag.text.strip()
                    valor = valor_divisa_tag.text.strip()
                    tasas["otras"][nombre] = valor

        return tasas

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el BCV: {e}")
    except AttributeError:
        raise HTTPException(status_code=500, detail="La estructura del sitio del BCV ha cambiado. No se pudo analizar la información.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado: {e}")

# --- Endpoint de la API ---
@app.get("/", response_model=TasasOficiales, summary="Obtener las tasas oficiales del BCV")
def get_tasas_oficiales():
    """
    Este endpoint devuelve las tasas de cambio oficiales del Banco Central de Venezuela.
    Los datos se actualizan cada 30 minutos.
    """
    global cache_data, cache_timestamp

    # Verificar si la caché está vigente
    if cache_data and cache_timestamp and (datetime.now() - cache_timestamp) < timedelta(minutes=CACHE_DURATION_MINUTES):
        print("Datos obtenidos desde la caché.")
        return cache_data

    # Si la caché ha expirado, obtener nuevos datos
    try:
        data = obtener_tasas_bcv()
        if not data["dolar"] or not data["euro"]:
            raise HTTPException(status_code=500, detail="No se pudieron obtener las tasas principales.")

        # Actualizar la caché
        cache_data = data
        cache_timestamp = datetime.now()

        return cache_data
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor al procesar la solicitud.")

# --- Ejecutar la API ---
# Para ejecutar la API, usa el siguiente comando en tu terminal:
# uvicorn bcv_api:app --reload