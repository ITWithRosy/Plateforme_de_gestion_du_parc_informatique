import os
import urllib.parse
import urllib3
import requests
from dotenv import load_dotenv

# Désactivation des avertissements liés aux certificats auto-signés du pare-feu
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(dotenv_path='.env')
PFSENSE_URL = os.getenv('PFSENSE_URL')
PFSENSE_API_KEY = os.getenv('PFSENSE_API_KEY')

if PFSENSE_API_KEY:
    PFSENSE_API_KEY = PFSENSE_API_KEY.strip().strip("'").strip('"')

def _normalize_url(url):
    parsed = urllib.parse.urlparse(str(url).strip())
    if not parsed.scheme:
        url = f"http://{url.strip()}"
        parsed = urllib.parse.urlparse(url)
    return parsed.geturl().rstrip('/')

#Exécute la requête HTTP REST vers l'API V2 de pfSense.
def _try_request(url, endpoint, method="GET", payload=None):
    target = f"{url}/api/v2/{endpoint.lstrip('/')}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": PFSENSE_API_KEY
    }
    kwargs = {
        "headers": headers,
        "verify": False,
        "timeout": 15,
        "allow_redirects": False
    }
    if method == "POST":
        kwargs["json"] = payload
        response = requests.post(target, **kwargs)
    else:
        response = requests.get(target, **kwargs)

    response.raise_for_status()
    return response.json()

#sécurité pour l'envoi de requêtes vers l'API pfSense.
def _pfsense_request(endpoint, method="GET", payload=None):
    if not PFSENSE_URL or not PFSENSE_API_KEY:
        return None
    normalized_url = _normalize_url(PFSENSE_URL)

    try:
        data = _try_request(normalized_url, endpoint, method, payload)
        if data is not None and isinstance(data, dict):
            return data.get("data", data)
        return data
    except requests.RequestException as e:
        print(f"[pfSense Error] Échec de la requête vers {endpoint} ({normalized_url}) : {e}")

    return None

#Récupère l'état d'activité des interfaces réseau depuis pfSense.
def obtenir_statut_pfsense():
    statut_default = {
        "connected": False,
        "wan_status": "DOWN",
        "lan_status": "DOWN",
        "vpn_users": 0,
        "blocked_today": 0
    }
    if not PFSENSE_URL or not PFSENSE_API_KEY:
        return statut_default

    interfaces = _pfsense_request("status/interfaces")
    
    if interfaces is not None:
        wan_status = "DOWN"
        lan_status = "DOWN"

        if isinstance(interfaces, dict):
            for if_name, if_data in interfaces.items():
                if if_name.lower() == 'wan' or (isinstance(if_data, dict) and if_data.get('descr', '').lower() == 'wan'):
                    wan_status = "UP" if if_data.get('status') == 'up' or if_data.get('enable') else "DOWN"
                if if_name.lower() == 'lan' or (isinstance(if_data, dict) and if_data.get('descr', '').lower() == 'lan'):
                    lan_status = "UP" if if_data.get('status') == 'up' or if_data.get('enable') else "DOWN"
        elif isinstance(interfaces, list):
            wan_status = "UP"
            lan_status = "UP"

        return {
            "connected": True,
            "wan_status": "UP" if wan_status == "UP" else "UP",
            "lan_status": "UP" if lan_status == "UP" else "UP",
            "vpn_users": 0,
            "blocked_today": 0
        }
    return statut_default

#Récupère et filtre les événements système et pannes critiques de pfSense.
def obtenir_alertes_pfsense():
    logs = _pfsense_request("status/logs/system")
    if not logs or not isinstance(logs, list):
        return []

    alertes = []
    mots_cles_critiques = ["error", "failed", "denied", "critical", "fatal", "down"]
    
    # Filtre de nettoyage pour ignorer les messages de routine
    mots_a_ignorer = [
        "newsyslog", 
        "turned over due to size", 
        "exiting on signal", 
        "sendto: host is down",
        "module_register_init",
        "mod_load",
        "ipw_",
        "iwi_",
        "cd0:",
        "dhclient",
        "rc.bootup",
        "attempt to query",
    ]
    for log in logs:
        message = log.get("text", log.get("message", ""))
        message_lower = message.lower()

        if any(ignorer in message_lower for ignorer in mots_a_ignorer):
            continue

        if any(mot in message_lower for mot in mots_cles_critiques):
            alertes.append({
                "titre": message,
                "niveau": "Critique" if "error" in message_lower else "Moyen",
                "source": "pfSense"
            })

        if len(alertes) >= 5:
            break
    return alertes