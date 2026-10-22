from flask import Blueprint, render_template, flash
from flask_login import login_required
from models.equipement import Equipement
from models.alerte import Alerte
from models.utilisateur import Utilisateur
from models.tache import TacheAutomatisee
from models.journal import JournalAudit

from services.zabbix import (
    obtenir_statut_hotes,
    obtenir_alertes_actives,
    obtenir_metriques_globales
)
from services.pfsense import obtenir_statut_pfsense, obtenir_alertes_pfsense

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Récupération des données d'infrastructure Zabbix
    try:
        hosts_zabbix = obtenir_statut_hotes() or []
        alertes_zabbix = obtenir_alertes_actives() or []
        metriques = obtenir_metriques_globales() or {"cpu_moyen": 0, "ram_moyenne": 0}
    except Exception as e:
        print(f"Erreur lors de l'interrogation de l'API Zabbix : {e}")
        hosts_zabbix, alertes_zabbix = [], []
        metriques = {"cpu_moyen": 0, "ram_moyenne": 0}
        flash("Connexion à l'API Zabbix indisponible.", "warning")
        
    nb_equipements = len(hosts_zabbix) if hosts_zabbix else Equipement.query.count()
    hosts_up = len([h for h in hosts_zabbix if h.get('statut') == 'UP'])
    hosts_down = len([h for h in hosts_zabbix if h.get('statut') == 'DOWN'])
    
    # Récupération de l'état du pare-feu pfSense
    try:
        pfsense_data = obtenir_statut_pfsense()
        alertes_pfsense_brutes = obtenir_alertes_pfsense() or []
    except Exception as e:
        print(f"Erreur lors de l'interrogation de l'API pfSense : {e}")
        pfsense_data = {
            "connected": False, "wan_status": "DOWN", 
            "lan_status": "DOWN", "vpn_users": 0, "blocked_today": 0
        }
        alertes_pfsense_brutes = []

    # Calcul des métriques KPI stockées en base de données
    alertes_critiques = Alerte.query.filter(Alerte.niveau.ilike("critique"), Alerte.statut == "En cours").count()
    alertes_moyen = Alerte.query.filter(
        (Alerte.niveau.ilike("moyen")) | (Alerte.niveau.ilike("avertissement")), 
        Alerte.statut == "En cours"
    ).count()
    alertes_info = Alerte.query.filter(Alerte.niveau.ilike("info"), Alerte.statut == "En cours").count()
        
    nb_utilisateurs = Utilisateur.query.count()
    try:
        nb_taches = TacheAutomatisee.query.count()
    except Exception:
        nb_taches = 0
        
    # Extraction des activités récentes pour le flux d'audit
    try:
        dernieres_activites = JournalAudit.query.order_by(JournalAudit.dateCreation.desc()).limit(5).all()
    except Exception as e:
        print(f"Erreur lors de la récupération des activités : {e}")
        dernieres_activites = []

    # Fusion et filtrage intelligent des alertes pfSense et Zabbix
    if alertes_zabbix:
        alertes_base = [
            {'titre': a.get('titre', 'Alerte Zabbix'), 'niveau': a.get('niveau', 'Info'), 'source': 'Zabbix'}
            for a in alertes_zabbix
        ]
    else:
        alertes_base = [
            {'titre': a.titre, 'niveau': a.niveau, 'source': 'BDD'} 
            for a in Alerte.query.filter_by(statut="En cours").order_by(Alerte.idAlerte.desc()).limit(5).all()
        ]

    mots_cles_critiques = ["error", "failed", "denied", "critical", "fatal"]
    alertes_pfsense_filtrees = [
        a for a in alertes_pfsense_brutes
        if any(mot in str(a.get('titre', '')).lower() for mot in mots_cles_critiques)
    ]

    alertes_a_afficher = (alertes_base + alertes_pfsense_filtrees)[:6]

    return render_template(
        'dashboard.html',
        equipements_count=nb_equipements,
        alertes_count=alertes_critiques,
        utilisateurs_count=nb_utilisateurs,
        taches_count=nb_taches,
        equipements_zabbix=hosts_zabbix,
        alertes_display=alertes_a_afficher,
        hosts_up=hosts_up,
        hosts_down=hosts_down,
        alertes_critiques=alertes_critiques,
        alertes_moyen=alertes_moyen,
        alertes_info=alertes_info,
        cpu_moyen=metriques.get("cpu_moyen", 0),
        ram_moyenne=metriques.get("ram_moyenne", 0),
        dernieres_activites=dernieres_activites,
        pfsense=pfsense_data
    )