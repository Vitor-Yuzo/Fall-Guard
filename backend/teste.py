
import requests

url = "http://127.0.0.1:5000/api/falls"

dados = {
    "evento": "queda",
    "classe": "lie",
    "confianca": 0.94,
    "timestamp": "2026-10-20 20:30:00"
}

try:
    response = requests.post(url, json=dados, timeout=5)

    print("Status:", response.status_code)
    print("Resposta:", response.json())

except requests.exceptions.RequestException as erro:
    print("Erro ao conectar com a API:", erro)
