# app.py
# -------------------------------------------------------------------
# Servidor Flask unificado: HTML + API GoodWe
# -------------------------------------------------------------------
from flask import Flask, jsonify, request
import json
from flask_cors import CORS
import os
from datetime import datetime, time as dtime
import requests

# Módulos locais
from goodwe_client import fetch_data_from_sems, client_from_env, get_plant_detail, crosslogin, get_monitor_detail

# Importa o blueprint das rotas HTML
from html_routes import html_bp

# Inicializa o Flask
app = Flask(__name__, template_folder='../pages/', static_folder='../../assets/')
CORS(app)  # Habilita CORS para requisições do HTML local

# Configurações de ambiente
try:
    CONFIG = client_from_env()
except RuntimeError as e:
    CONFIG = {}
    print(f"Aviso: {e}. Usando credenciais fornecidas pela Goodwe.")
    CONFIG["account"] = "ecopower.management@gmail.com"
    CONFIG["password"] = "Goodwe2018"
    CONFIG["region"] = "us"

# Registra o blueprint das rotas HTML
app.register_blueprint(html_bp)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta do app.py
ARQUIVO_JSON = os.path.join(BASE_DIR, "../dispositivos/dispositivos.json")

@app.route('/ler-json', methods=['GET'])
def ler_json():
    if not os.path.exists(ARQUIVO_JSON):
        return "Arquivo JSON não encontrado", 404

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except json.JSONDecodeError:
        return "Arquivo JSON inválido", 400

    return jsonify(dados)


@app.route("/atualizar-json", methods=["POST"])
def atualizar_json():
    dispositivo = request.json

    with open(ARQUIVO_JSON, "r") as f:
        dados = json.load(f)

    for d in dados:
        if d["id"] == dispositivo["id"]:
            d["nome"] = dispositivo["nome"]
            d["prioridade"] = dispositivo["prioridade"]
            break

    with open(ARQUIVO_JSON, "w") as f:
        json.dump(dados, f, indent=4)

    return jsonify({"status": "ok", "mensagem": "Dispositivo atualizado!"})

@app.route("/dados")
def get_dados():
    inverter_sn = request.args.get("sn", "53600ERN238W0001")
    column = request.args.get("col")
    req_date_str = request.args.get("date")

    if not column or not req_date_str:
        return jsonify({"error": "Parâmetros 'col' e 'date' são obrigatórios"}), 400

    try:
        req_date = datetime.strptime(req_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    dt_str = datetime.combine(req_date, dtime(0, 0)).strftime("%Y-%m-%d %H:%M:%S")
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
    plant_id = request.args.get("plantId")
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400

    try:
        token = crosslogin(CONFIG["account"], CONFIG["password"], CONFIG["region"])
        data = get_plant_detail(token, plant_id, region="us")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Falha ao buscar detalhes da usina", "details": str(e)}), 500

@app.route("/detalhes-monitor")
def get_detalhes_monitor():
    plant_id = request.args.get("plantId")
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400

    try:
        token = crosslogin(CONFIG["account"], CONFIG["password"], CONFIG["region"])
        data = get_monitor_detail(token, plant_id, region="us")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Falha ao buscar detalhes do monitor", "details": str(e)}), 500

@app.route("/previsao-tempo")
def get_previsao_tempo():
    plant_id = request.args.get("plantId")
    if not plant_id:
        return jsonify({"error": "Parâmetro 'plantId' é obrigatório"}), 400

    try:
        url = f"http://127.0.0.1:5000/detalhes-monitor?plantId={plant_id}"
        monitor_resp = requests.get(url)
        monitor_data = monitor_resp.json()

        if "data" not in monitor_data or "info" not in monitor_data["data"]:
            return jsonify({"error": "Latitude e longitude não encontrados"}), 404

        latitude = monitor_data["data"]["info"]["latitude"]
        longitude = monitor_data["data"]["info"]["longitude"]

        API_KEY = "e30f65d5c490822248b696c846d33704"  # sua chave OpenWeather
        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=pt_br"
        )
        weather_resp = requests.get(weather_url)
        weather_data = weather_resp.json()

        return jsonify({
            "localizacao": {"latitude": latitude, "longitude": longitude},
            "previsao": weather_data
        })

    except Exception as e:
        return jsonify({"error": "Falha ao buscar previsão do tempo", "details": str(e)}), 500

# Inicialização do servidor
if __name__ == "__main__":
    # Baixa o JSON direto usando o goodwe_client
    try:
        plant_id_demo = "7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a"
        token = crosslogin(CONFIG["account"], CONFIG["password"], CONFIG["region"])
        dados_monitor = get_monitor_detail(token, plant_id_demo, region="us")

        arquivo_saida = os.path.join(BASE_DIR, "detalhes_monitor.json")
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            json.dump(dados_monitor, f, indent=4, ensure_ascii=False)
        print(f"JSON de detalhes do monitor salvo em {arquivo_saida}")
    except Exception as e:
        print(f"Falha ao baixar detalhes do monitor: {e}")

    # Depois inicia o servidor Flask normalmente
    print("Servidor web iniciado. Acesse http://127.0.0.1:5000/ no navegador.")
    app.run(host="0.0.0.0", port=5000, debug=True)
