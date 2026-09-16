from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.alerte import Alerte
from models.equipement import Equipement
from models.journal import JournalAudit
from services.zabbix import obtenir_statut_hotes

alertes_bp = Blueprint('alertes', __name__)

@alertes_bp.route('/alertes')
@login_required
def alertes():
    """Consulte et filtre le panneau d'alertes réseau synchronisé avec Zabbix."""
    filtre = request.args.get('filtre', 'tous')

    # Synchronisation des hôtes hors ligne (DOWN) détectés par Zabbix
    try:
        hotes_zabbix = obtenir_statut_hotes() or []
        for hote in hotes_zabbix:
            if hote.get('statut') == 'DOWN':
                nom_machine = hote.get('nom')
                ip_machine = hote.get('ip')
                titre_incident = f"Équipement {nom_machine or 'Inconnu'} hors ligne (DOWN)"
                
                alerte_existante = Alerte.query.filter_by(titre=titre_incident, statut="En cours").first()
                if not alerte_existante:
                    equipement = Equipement.query.filter(
                        (Equipement.nom == nom_machine) | 
                        (Equipement.adresseIP == ip_machine)
                    ).first()
                    
                    id_eq = equipement.idEquipement if equipement else None

                    nouvelle_alerte = Alerte(
                        titre=titre_incident,
                        description=f"L'hôte {nom_machine} (IP: {ip_machine}) ne répond plus aux requêtes Zabbix.",
                        niveau="Critique",
                        type="Disponibilité",
                        statut="En cours",
                        idEquipement=id_eq
                    )
                    db.session.add(nouvelle_alerte)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erreur Sync Alertes Zabbix : {e}")

    # Application des filtres de recherche
    query = Alerte.query
    if filtre == 'critique':
        query = query.filter_by(niveau="Critique")
    elif filtre == 'avertissement':
        query = query.filter_by(niveau="Avertissement")

    alertes_list = query.order_by(Alerte.idAlerte.desc()).all()

    # Formatage de la structure de données pour le rendu HTML
    alertes_formatted = []
    for a in alertes_list:
        nom_equipement = a.equipement.nom if getattr(a, 'equipement', None) else "Non attribué"
        alertes_formatted.append({
            'id': a.idAlerte,
            'titre': a.titre,
            'description': getattr(a, 'description', a.titre),
            'niveau': a.niveau or 'Avertissement',
            'type': a.type or 'Réseau',
            'statut': a.statut or 'En cours',
            'equipement': nom_equipement,
            'date': getattr(a, 'dateCreation', None)
        })

    return render_template('alertes.html', alertes=alertes_formatted, filtre_actif=filtre)


@alertes_bp.route('/alertes/acquitter/<int:id>', methods=['POST'])
@login_required
def acquitter_alerte(id):
    """Marque une alerte active comme résolue et enregistre l'action d'acquittement."""
    alerte = db.session.get(Alerte, id)
    if not alerte:
        flash("Alerte introuvable.", "danger")
        return redirect(url_for('alertes.alertes'))
        
    alerte.statut = "Résolue"

    # Journalisation de l'action dans l'audit
    user_id = getattr(current_user, 'idUtilisateur', None)
    log_audit = JournalAudit(
        action=f"Acquittement alerte ID {id}",
        adresseIP=request.remote_addr or "127.0.0.1",
        resultat="Succès",
        description=f"Alerte '{alerte.titre}' acquittée/résolue.",
        idUtilisateur=user_id
    )
    db.session.add(log_audit)
    db.session.commit()
    
    flash("L'alerte a été marquée comme résolue.", "success")
    return redirect(url_for('alertes.alertes'))