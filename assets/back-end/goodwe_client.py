# goodwe_client.py
"""
Starter mínimo para acessar a API do SEMS Portal (GoodWe).
⚠️ Educacional. Endpoints e contratos podem mudar. Use credenciais próprias.
"""
from __future__ import annotations
import os
import json
import base64
import requests
from typing import Literal, Dict, Any

Region = Literal["us", "eu"]

BASE = {
    "us": "https://us.semsportal.com",
    "eu": "https://eu.semsportal.com",
}

def _initial_token() -> str:
    """
    Gera o Token inicial (pré-login). Mesmo formato do exemplo do professor.
    """
    original = {"uid": "", "timestamp": 0, "client": "web", "version": "", "language": "us"}
    b = json.dumps(original).encode("utf-8")
    return base64.b64encode(b).decode("utf-8")

def crosslogin(account: str, pwd: str, region: Region = "us") -> str:
    """
    Faz o crosslogin e devolve o Token válido (Base64 do campo 'data' da resposta).
    """
    url = f"{BASE[region]}/api/v2/common/crosslogin"
    headers = {"Token": _initial_token(), "Content-Type": "application/json", "Accept": "*/*"}
    payload = {
        "account": account,
        "pwd": pwd,
        "agreement_agreement": 0,
        "is_local": False
    }
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    js = r.json()
    if "data" not in js or js.get("code") not in (0, 1, 200):
        raise RuntimeError(f"Login falhou: {js}")
    data_to_string = json.dumps(js["data"])
    token = base64.b64encode(data_to_string.encode("utf-8")).decode("utf-8")
    return token

def get_inverter_data_by_column(token: str, inv_id: str, column: str, date: str, region: Region = "us") -> Dict[str, Any]:
    """
    Chama o endpoint GetInverterDataByColumn.
    Ex.: column='Cbattery1', date='YYYY-MM-DD HH:MM:SS', inv_id='5010KETU229W6177'
    """
    url = f"{BASE[region]}/api/PowerStationMonitor/GetInverterDataByColumn"
    headers = {"Token": token, "Content-Type": "application/json", "Accept": "*/*"}
    payload = {"date": date, "column": column, "id": inv_id}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

plant_id = "7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a"

def get_plant_detail(token: str, plant_id: str, region: Region = "us") -> Dict[str, Any]:
    """
    Chama o endpoint GetPlantDetailByPowerstationId.
    Ex.: plant_id='7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a'
    """
    url = f"{BASE[region]}/api/v3/PowerStation/GetPlantDetailByPowerstationId"
    headers = {"Token": token, "Content-Type": "application/json", "Accept": "*/*"}
    payload = {"powerStationId": "7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a"}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def get_monitor_detail(token: str, plant_id: str, region: Region = "us") -> Dict[str, Any]:
    """
    Chama o endpoint GetMonitorDetailByPowerstationId.
    Ex.: plant_id='7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a'
    """
    url = f"{BASE[region]}/api/v3/PowerStation/GetMonitorDetailByPowerstationId"
    headers = {"Token": token, "Content-Type": "application/json", "Accept": "*/*"}
    payload = {"powerStationId": "7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a"}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def client_from_env() -> Dict[str, str]:
    """
    Lê variáveis de ambiente SEMS_ACCOUNT, SEMS_PASSWORD, SEMS_REGION (us|eu).
    """
    acc = os.getenv("SEMS_ACCOUNT", "")
    pwd = os.getenv("SEMS_PASSWORD", "")
    region = os.getenv("SEMS_REGION", "us")
    if not acc or not pwd:
        raise RuntimeError("Defina SEMS_ACCOUNT e SEMS_PASSWORD no ambiente.")
    return {"account": acc, "password": pwd, "region": region}

def fetch_data_from_sems(account: str, password: str, inverter_sn: str, req_date: str, column: str, login_region: str, data_region: str) -> Dict[str, Any]:
    """
    Busca dados de uma única coluna do SEMS.
    Essa função será chamada pela nossa API.
    """
    try:
        token = crosslogin(account, password, login_region)
        data = get_inverter_data_by_column(token, inverter_sn, column, req_date, data_region)
        return data
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return {"code": -1, "msg": str(e), "data": None}


if __name__ == "__main__":
    # Exemplo (somente se você definiu as variáveis de ambiente):
    try:
        cfg = client_from_env()
        token = crosslogin(cfg["account"], cfg["password"], cfg["region"])
        print("Login OK. Token pronto.")
        # Exemplo de leitura (ajuste IDs/coluna/data antes de rodar):
        # resp = get_inverter_data_by_column(token, "5010KETU229W6177", "Cbattery1", "2025-08-12 00:21:01", "eu")
        # print(resp)
    except Exception as e:
        print("Aviso:", e)