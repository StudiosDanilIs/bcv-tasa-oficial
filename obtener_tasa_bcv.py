import requests
from bs4 import BeautifulSoup

def obtener_tasas_bcv():
    """
    Esta función se conecta a la página principal del BCV para extraer
    las tasas de cambio del dólar, euro y otras divisas, manejando
    posibles cambios en la estructura del sitio.
    """
    url = 'https://www.bcv.org.ve/'
    print("Conectando con el Banco Central de Venezuela...")

    # Ignora la verificación SSL, útil para entornos de prueba
    # En producción, se recomienda gestionar los certificados correctamente.
    session = requests.Session()
    session.verify = False 

    try:
        # Realiza la solicitud GET a la URL.
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción si la respuesta es un error HTTP.

        # Analiza el contenido HTML de la página.
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Extraer las tasas de las principales divisas (Dólar y Euro) ---
        print("\n--- Tasas de Referencia ---")

        # Buscar el contenedor del dólar
        dolar_container = soup.find('div', id='dolar')
        if dolar_container:
            dolar_valor = dolar_container.find('strong').text.strip()
            dolar_fecha = dolar_container.find('span').text.strip()
            print(f"Dólar (USD): {dolar_valor} Bs.S")
            print(f"Fecha: {dolar_fecha}")
        else:
            print("No se encontró la tasa del Dólar. La estructura del sitio puede haber cambiado.")

        # Buscar el contenedor del euro
        euro_container = soup.find('div', id='euro')
        if euro_container:
            euro_valor = euro_container.find('strong').text.strip()
            euro_fecha = euro_container.find('span').text.strip()
            print(f"Euro (EUR): {euro_valor} Bs.S")
            print(f"Fecha: {euro_fecha}")
        else:
            print("No se encontró la tasa del Euro. La estructura del sitio puede haber cambiado.")

        # --- Extraer las tasas de otras divisas ---
        print("\n--- Otras Tasas ---")

        # Buscar el contenedor que agrupa a las demás divisas
        otras_divisas_container = soup.find('div', class_='col-sm-6 col-xs-6')
        if otras_divisas_container:
            # Encontrar todas las tarjetas de divisas dentro de ese contenedor
            divisas_cards = otras_divisas_container.find_all('div', class_='col-sm-4')
            for card in divisas_cards:
                nombre_divisa_tag = card.find('p', class_='name')
                valor_divisa_tag = card.find('strong')

                if nombre_divisa_tag and valor_divisa_tag:
                    nombre_divisa = nombre_divisa_tag.text.strip()
                    valor_divisa = valor_divisa_tag.text.strip()
                    print(f"{nombre_divisa}: {valor_divisa} Bs.S")
        else:
            print("No se encontraron otras tasas. La estructura del sitio puede haber cambiado.")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: No se pudo acceder a la página del BCV. {e}")
    except AttributeError:
        print("Error de análisis: No se encontró la información esperada. La estructura HTML de la página pudo haber cambiado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    obtener_tasas_bcv()