"""01_descarga.py – Descarga los informes publicados en https://discord.com/safety-transparency.

- Lee la página oficial y solo descarga enlaces que aparezcan publicados en ella.
- Solo acepta los dominios discord.com y cdn.discordapp.com (también tras redirecciones).
- Guarda en datos/raw/, descomprime los .zip en subcarpetas y conserva los originales.
- Genera datos/raw/MANIFIESTO.csv con nombre, URL, dominio, fecha, tamaño y SHA-256.
Se puede volver a ejecutar: si el archivo ya existe no se vuelve a descargar.
Si la red bloquea cdn.discordapp.com, descargue los archivos a mano desde la página
oficial, cópielos a datos/raw/ con el nombre indicado en nombre_local() y vuelva a
ejecutar: el script verifica, calcula el hash y descomprime.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
import hashlib
import re
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw"
PAGINA = "https://discord.com/safety-transparency"
DOMINIOS = {"discord.com", "cdn.discordapp.com"}
CABECERAS = {"User-Agent": "Mozilla/5.0 (proyecto academico PSO)"}

# Enlaces que pide el plan (el ECA en portugués se omite: duplicado del inglés)
ESPERADOS = [
    "transparency-reports/Discord-Transparency-Report-2026-Updated.pdf",
    "transparency-reports/TCO-Report-2026.pdf",
    "transparency-reports/Discord-Transparency-Report-H1-2024.zip",
    "transparency-reports/Discord-Transparency-Report-Q1-2023.zip",
    "transparency-reports/Discord-Transparency-Report-Q2-2023.zip",
    "transparency-reports/Discord-Transparency-Report-Q3-2023.zip",
    "transparency-reports/Discord-Transparency-Report-Q4-2023.zip",
    "transparency-reports/Discord-Transparency-Report-Q1-2022.zip",
    "transparency-reports/Discord-Transparency-Report-Q2-2022.zip",
    "transparency-reports/Discord-Transparency-Report-Q3-2022.zip",
    "2024/Discord-DSA_Transparency_Report.zip",
    "2025/Discord-DSA_Transparency_Report.July-2026.zip",
    "eca-digital-transparency-reports/english-brazil-eca-report-september-2026.pdf",
]


def nombre_local(url: str) -> str:
    """Nombre de archivo local; los DSA llevan el año como prefijo para no chocar."""
    partes = urlparse(url).path.split("/")
    if partes[-2] in ("2024", "2025"):
        return f"DSA-{partes[-2]}_{partes[-1]}"
    return partes[-1]


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    html = requests.get(PAGINA, headers=CABECERAS, timeout=60).text
    publicados = set(re.findall(r"https?://[^\"'\s<>)]+\.(?:pdf|zip)", html))

    filas, fallos = [], []
    for sufijo in ESPERADOS:
        url = f"https://cdn.discordapp.com/assets/{sufijo}"
        if url not in publicados:
            fallos.append((url, "no aparece publicado en la página de transparencia"))
            continue
        destino = RAW / nombre_local(url)
        try:
            metodo = "archivo existente en raw/ (descarga previa o manual del usuario)"
            if not destino.exists():
                metodo = "script 01_descarga.py"
                r = requests.get(url, headers=CABECERAS, timeout=180, allow_redirects=True)
                dominio_final = urlparse(r.url).hostname
                if dominio_final not in DOMINIOS:
                    fallos.append((url, f"redirige a dominio no permitido: {dominio_final}"))
                    continue
                r.raise_for_status()
                destino.write_bytes(r.content)
            datos = destino.read_bytes()
            filas.append({
                "archivo": destino.name,
                "url": url,
                "dominio": urlparse(url).hostname,
                "fecha_descarga": datetime.fromtimestamp(destino.stat().st_mtime).isoformat(timespec="seconds"),
                "tamano_bytes": len(datos),
                "sha256": hashlib.sha256(datos).hexdigest(),
                "metodo": metodo,
            })
            if destino.suffix == ".zip":
                carpeta = RAW / destino.stem
                if not carpeta.exists():
                    with zipfile.ZipFile(destino) as z:
                        z.extractall(carpeta)
        except Exception as e:  # se registra y se sigue con los demás
            fallos.append((url, repr(e)[:150]))

    campos = ["archivo", "url", "dominio", "fecha_descarga", "tamano_bytes", "sha256", "metodo"]
    with open(RAW / "MANIFIESTO.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    print(f"Descargados/verificados: {len(filas)}")
    for f_ in filas:
        print(f"  {f_['archivo']:60s} {f_['tamano_bytes']:>10,d} B")
    print(f"Fallos: {len(fallos)}")
    for u, e in fallos:
        print(f"  {u} -> {e}")


if __name__ == "__main__":
    main()
