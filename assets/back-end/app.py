# app.py
# -------------------------------------------------------------------
# FIAP x GoodWe – Servidor API para HTML
# -------------------------------------------------------------------
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime, time as dtime
import requests

# Módulos locais
from goodwe_client import fetch_data_from_sems, client_from_env, get_plant_detail, crosslogin, get_monitor_detail

app = Flask(__name__)
# Habilita CORS para permitir que a página HTML (executada localmente)
# possa fazer requisições para este servidor.
CORS(app) 

# Variáveis de ambiente
try:
    CONFIG = client_from_env()
except RuntimeError as e:
    CONFIG = {}
    print(f"Aviso: {e}. Usando credenciais demo.")
    # Use credenciais demo se as variáveis de ambiente não estiverem configuradas
    CONFIG["account"] = "ecopower.management@gmail.com"
    CONFIG["password"] = "Goodwe2018"
    CONFIG["region"] = "us"


@app.route("/")
def index():
    """Serve a página HTML principal."""
    return send_from_directory('.', 'teste3.html')


@app.route("/dados")
def get_dados():
    """Endpoint da API para buscar dados do SEMS."""
    inverter_sn = request.args.get("sn", "53600ERN238W0001")
    column = request.args.get("col")
    req_date_str = request.args.get("date")

    if not column or not req_date_str:
        return jsonify({"error": "Parâmetros 'col' e 'date' são obrigatórios"}), 400

    try:
        req_date = datetime.strptime(req_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # SEMS costuma exigir datetime com horário; usamos meia-noite local
    dt_str = datetime.combine(req_date, dtime(0, 0)).strftime("%Y-%m-%d %H:%M:%S")

    # Chama a função de busca do goodwe_client.py
    data = fetch_data_from_sems(
        account=CONFIG["account"],
        password=CONFIG["password"],
        inverter_sn=inverter_sn,
        req_date=dt_str,
        column=column,
        login_region="us",
        data_region="us"
    )

    if data.get("code") in (0, 1, 200) or ("data" in data and data["data"]):
        return jsonify(data)
    else:
        return jsonify({"error": "Falha ao buscar dados", "details": data.get("msg", "Desconhecido")}), 500


@app.route("/detalhes-usina")
def get_detalhes_usina():
    """Endpoint da API para buscar detalhes da usina."""
    plant_id = request.args.get("plantId")
    
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400
    
    try:
        # Reutiliza o token do crosslogin para a nova chamada
        token = crosslogin(CONFIG["account"], CONFIG["password"], CONFIG["region"])
        
        # Chama a nova função do goodwe_client
        data = get_plant_detail(token, plant_id, region="us")
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Falha ao buscar detalhes da usina", "details": str(e)}), 500


@app.route("/detalhes-monitor")
def get_detalhes_monitor():
    """Endpoint da API para buscar detalhes do monitor."""
    plant_id = request.args.get("plantId")
    
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400
    
    try:
        # Reutiliza o token do crosslogin para a nova chamada
        token = crosslogin(CONFIG["account"], CONFIG["password"], CONFIG["region"])
        
        # Chama a nova função do goodwe_client
        data = get_monitor_detail(token, plant_id, region="us")
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Falha ao buscar detalhes do monitor", "details": str(e)}), 500

@app.route("/previsao-tempo")
def get_previsao_tempo():
    """Endpoint da API para buscar previsão do tempo via OpenWeather."""
    plant_id = request.args.get("plantId")
    
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400

    try:
        # Primeiro pega os dados do monitor (onde está latitude e longitude)
        url = f"http://localhost:5000/detalhes-monitor?plantId={plant_id}"
        monitor_resp = requests.get(url)
        monitor_data = monitor_resp.json()

        # Verifica se os dados existem
        if "data" not in monitor_data or "info" not in monitor_data["data"]:
            return jsonify({"error": "Latitude e longitude não encontrados"}), 404

        latitude = monitor_data["data"]["info"]["latitude"]
        longitude = monitor_data["data"]["info"]["longitude"]

        # Chamada à API do OpenWeather
        API_KEY = "e30f65d5c490822248b696c846d33704"  # coloque sua chave aqui
        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=pt_br"
        )
        weather_resp = requests.get(weather_url)
        weather_data = weather_resp.json()

        return jsonify({
            "localizacao": {
                "latitude": latitude,
                "longitude": longitude
            },
            "previsao": weather_data
        })

    except Exception as e:
        return jsonify({"error": "Falha ao buscar previsão do tempo", "details": str(e)}), 500


if __name__ == "__main__":
    # Para rodar: python app.py
    # O servidor será iniciado em http://127.0.0.1:5000/
    print("Servidor web iniciado. Acesse http://127.0.0.1:5000/ no seu navegador.")
    app.run(debug=True)