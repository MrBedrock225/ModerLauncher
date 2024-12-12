import requests
import os
import json

def descargar_version_mc(version_id, directorio_destino="src/Versions/"):
    """Descargar una versión específica de Minecraft desde el manifiesto."""
    manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
    manifest_response = requests.get(manifest_url)

    if manifest_response.status_code != 200:
        print("Error al obtener el manifiesto de versiones.")
        return

    manifest_data = manifest_response.json()
    version_info = next((v for v in manifest_data['versions'] if v['id'] == version_id), None)

    if not version_info:
        print(f"La versión {version_id} no se encuentra en el manifiesto.")
        return

    version_url = version_info['url']
    version_response = requests.get(version_url)

    if version_response.status_code != 200:
        print(f"Error al obtener información de la versión {version_id}.")
        return

    version_data = version_response.json()
    jar_url = version_data['downloads']['client']['url']
    jar_response = requests.get(jar_url, stream=True)

    if jar_response.status_code == 200:
        os.makedirs(directorio_destino, exist_ok=True)
        ruta_archivo = os.path.join(directorio_destino, f"{version_id}.jar")
        with open(ruta_archivo, 'wb') as archivo:
            for chunk in jar_response.iter_content(chunk_size=8192):
                archivo.write(chunk)
        print(f"Versión {version_id} descargada exitosamente.")
    else:
        print(f"Error al descargar la versión {version_id}. Código de respuesta: {jar_response.status_code}")

if __name__ == "__main__":
    version_a_descargar = "1.16.5"  # Cambia a la versión deseada
    descargar_version_mc(version_a_descargar)
