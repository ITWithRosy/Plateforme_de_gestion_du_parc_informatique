import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

ZABBIX_URL = os.getenv('ZABBIX_URL')
ZABBIX_TOKEN = os.getenv('ZABBIX_TOKEN')

if ZABBIX_TOKEN:
    ZABBIX_TOKEN = ZABBIX_TOKEN.strip().strip("'").strip('"')

#Appel API JSON-RPC au serveur Zabbix avec jetons d'accès.
def _zabbix_request(method, params, request_id=1):

    if not ZABBIX_URL or not ZABBIX_TOKEN:
        return None
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id,
    }
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {ZABBIX_TOKEN}"
    }
    try:
        response = requests.post(ZABBIX_URL, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            return None
        return data.get("result", [])
    except Exception:
        return None

#Récupère les hôtes supervisés ainsi que leurs métriques instantanées.
def obtenir_statut_hotes():
    params = {
        "output": ["hostid", "host", "name", "status"],
        "selectInterfaces": ["ip", "available", "type"],
        "selectItems": ["key_", "lastvalue"],
    }

    resultat = _zabbix_request("host.get", params, request_id=1)
    if resultat is None:
        return []
    
    hotes = []
    for item in resultat:
        ip = "N/A"
        est_disponible = False
        status_admin = str(item.get("status", "1"))

        if item.get("interfaces"):
            interface = item["interfaces"][0]
            ip = interface.get("ip", "N/A")
            avail = str(interface.get("available", "0"))

            if avail == "1":
                est_disponible = True
            elif avail == "0" and status_admin == "0":
                est_disponible = True

        if ip == "127.0.0.1":
            ip = "192.168.10.5"

        nom_affiche = item.get("name") or item.get("host") or ip

        # Extraction des métriques de performance
        cpu_val = "--"
        ram_val = "--"

        for z_item in item.get("items", []):
            key = z_item.get("key_", "")
            val = z_item.get("lastvalue", "")

            # Traitement clé CPU
            if any(k in key for k in ["system.cpu.util", "system.cpu.load", "perf_counter"]):
                try:
                    cpu_val = f"{float(val):.1f}%"
                except (ValueError, TypeError):
                    pass

            # Traitement clé Mémoire RAM
            if any(k in key for k in ["memory.util", "memory.size", "vm.memory"]):
                try:
                    val_num = float(val)
                    if val_num <= 100:
                        ram_val = f"{val_num:.1f}%"
                except (ValueError, TypeError):
                    pass
                
        hotes.append({
            "id": item.get("hostid"),
            "nom": nom_affiche,
            "host": nom_affiche,
            "name": nom_affiche,
            "ip": ip,
            "statut": "UP" if est_disponible else "DOWN",
            "etat": "UP" if est_disponible else "DOWN",
            "cpu": cpu_val,
            "ram": ram_val
        })
    return hotes

#Interroge Zabbix pour remonter les problèmes actifs et synchronise la BDD localement.
def obtenir_alertes_actives():
    params = {
        "output": ["eventid", "name", "severity", "clock"],
        "selectHosts": ["hostid", "name", "host"],
        "sortfield": "eventid",
        "sortorder": "DESC"
    }

    resultat = _zabbix_request("problem.get", params, request_id=2)
    if not resultat:
        return []

    # Imports différés pour éviter les imports circulaires lors de l'initialisation de l'application
    from models import db
    from models.alerte import Alerte
    from models.equipement import Equipement

    alertes = []
    for item in resultat:
        sev = int(item.get("severity", 0))
        if sev >= 4:
            niveau = "Critique"
        elif sev == 3:
            niveau = "Moyen"
        elif sev == 2:
            niveau = "Avertissement"
        else:
            niveau = "Info"

        titre = item.get("name", "Alerte inconnue")
        
        host_name = None
        if item.get("hosts"):
            host_info = item["hosts"][0]
            host_name = host_info.get("name") or host_info.get("host")

        # Recherche de l'équipement dans la base de données
        equipement = None
        if host_name:
            equipement = Equipement.query.filter(
                (Equipement.nom == host_name) | (Equipement.adresseIP == host_name)
            ).first()

        id_equipement = equipement.idEquipement if equipement else None

        # Synchronisation et enregistrement en base de données local
        alerte_existante = Alerte.query.filter_by(titre=titre, statut="En cours").first()
        if not alerte_existante:
            nouvelle_alerte = Alerte(
                titre=titre,
                description=f"Alerte détectée par Zabbix sur l'hôte : {host_name or 'Inconnu'}",
                niveau=niveau,
                type="Disponibilité",
                statut="En cours",
                idEquipement=id_equipement
            )
            db.session.add(nouvelle_alerte)

        alertes.append({
            "id": item.get("eventid"),
            "titre": titre,
            "niveau": niveau,
            "idEquipement": id_equipement
        })

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return alertes

def obtenir_metriques_globales():
    """Calcule la charge moyenne CPU et l'utilisation RAM de l'ensemble du parc."""
    params = {
        "output": ["itemid", "key_", "lastvalue"],
        "filter": {
            "key_": [
                "system.cpu.util",
                "vm.memory.utilization",
                "system.cpu.load[percpu,avg1]",
                "vm.memory.size[pavailable]"
            ]
        }
    }
    resultat = _zabbix_request("item.get", params, request_id=3)
    if not resultat:
        return {"cpu_moyen": 0, "ram_moyenne": 0}

    cpu_vals = []
    ram_vals = []

    for item in resultat:
        key = item.get("key_", "")
        try:
            val = float(item.get("lastvalue", 0))
        except (ValueError, TypeError):
            continue

        if "system.cpu.util" in key or "system.cpu.load" in key:
            cpu_vals.append(val)
        elif "vm.memory.utilization" in key:
            ram_vals.append(val)
        elif "vm.memory.size[pavailable]" in key:
            ram_vals.append(100.0 - val)

    cpu_moyen = round(sum(cpu_vals) / len(cpu_vals), 1) if cpu_vals else 0
    ram_moyenne = round(sum(ram_vals) / len(ram_vals), 1) if ram_vals else 0

    return {
        "cpu_moyen": cpu_moyen,
        "ram_moyenne": ram_moyenne
    }