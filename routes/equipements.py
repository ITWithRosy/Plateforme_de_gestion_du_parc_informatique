from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db
from models.equipement import Equipement
from models.journal import JournalAudit
from services.zabbix import obtenir_statut_hotes

equipements_bp = Blueprint('equipements', __name__)

@equipements_bp.route('/equipements')
@login_required
def equipements():
    """Affiche la liste dynamique et l'état des équipements du parc informatique."""
    try:
        hosts_zabbix = obtenir_statut_hotes()
        zabbix_dict = {h.get('nom'): h for h in hosts_zabbix} if hosts_zabbix else {}
    except Exception as e:
        print(f"Erreur Zabbix : {e}")
        zabbix_dict = {}

    equipements_db = Equipement.query.all()

    # Synchronisation initiale automatique avec Zabbix si la BDD est vide
    if not equipements_db and zabbix_dict:
        try:
            for nom_hote, data in zabbix_dict.items():
                nouvel_eq = Equipement(
                    nom=nom_hote,
                    adresseIP=data.get('ip', '127.0.0.1'),
                    type="Serveur/Hôte",
                    systeme="Linux/Windows",
                    etat="actif",
                    hostid_zabbix=str(data.get('hostid', ''))
                )
                db.session.add(nouvel_eq)
            db.session.commit()
            equipements_db = Equipement.query.all()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur auto-population BDD : {e}")

    # Fusion des données de la BDD et des métriques Zabbix
    liste_combinee = []
    for eq in equipements_db:
        info_zabbix = zabbix_dict.get(eq.nom, {})
        liste_combinee.append({
            'id': eq.idEquipement,
            'idEquipement': eq.idEquipement,
            'nom': eq.nom,
            'adresseIP': eq.adresseIP or info_zabbix.get('ip', 'N/A'),
            'type': eq.type or 'N/A',
            'systeme': eq.systeme or 'N/A',
            'modele': eq.systeme or 'N/A',
            'etat': eq.etat or 'inconnu',
            'statut': info_zabbix.get('statut', eq.etat or 'inconnu'),
            'cpu': info_zabbix.get('cpu', '--'),
            'ram': info_zabbix.get('ram', '--')
        })

    return render_template('equipements.html', equipements=liste_combinee)


@equipements_bp.route('/equipements/ajouter', methods=['POST'])
@login_required
@admin_required
def ajouter_equipement():
    """Ajoute un nouvel équipement dans l'inventaire."""
    nom = request.form.get('nom')
    adresse_ip = request.form.get('adresseIP')
    type_eq = request.form.get('type')
    modele = request.form.get('modele')

    if nom and adresse_ip:
        nouvel_eq = Equipement(
            nom=nom,
            adresseIP=adresse_ip,
            type=type_eq,
            systeme=modele,
            etat="actif"
        )
        db.session.add(nouvel_eq)

        log_audit = JournalAudit(
            action=f"Ajout de l'équipement {nom}",
            adresseIP=request.remote_addr or "127.0.0.1",
            resultat="Succès",
            description=f"IP: {adresse_ip}, Type: {type_eq}",
            idUtilisateur=getattr(current_user, 'idUtilisateur', None)
        )
        db.session.add(log_audit)
        db.session.commit()

        flash(f"L'équipement {nom} a été ajouté avec succès !", "success")
    else:
        flash("Veuillez remplir tous les champs obligatoires.", "danger")

    return redirect(url_for('equipements.equipements'))


@equipements_bp.route('/equipements/supprimer/<int:id>', methods=['POST'])
@login_required
@admin_required
def supprimer_equipement(id):
    """Supprime un équipement du parc."""
    eq = db.session.get(Equipement, id)
    if not eq:
        flash("Équipement introuvable.", "danger")
        return redirect(url_for('equipements.equipements'))
    
    nom_eq = eq.nom
    db.session.delete(eq)
    
    log_audit = JournalAudit(
        action=f"Suppression de l'équipement {nom_eq}",
        adresseIP=request.remote_addr or "127.0.0.1",
        resultat="Succès",
        description=f"Équipement ID {id} supprimé",
        idUtilisateur=getattr(current_user, 'idUtilisateur', None)
    )
    db.session.add(log_audit)
    db.session.commit()

    flash(f"L'équipement {nom_eq} a été supprimé.", "info")
    return redirect(url_for('equipements.equipements'))


@equipements_bp.route('/equipements/modifier/<int:id>', methods=['POST'])
@login_required
@admin_required
def modifier_equipement(id):
    """Met à jour les caractéristiques d'un équipement."""
    eq = db.session.get(Equipement, id)
    if not eq:
        flash("Équipement introuvable.", "danger")
        return redirect(url_for('equipements.equipements'))

    nom = request.form.get('nom')
    adresse_ip = request.form.get('adresseIP')
    type_eq = request.form.get('type')
    modele = request.form.get('modele')

    if nom and adresse_ip:
        eq.nom = nom
        eq.adresseIP = adresse_ip
        eq.type = type_eq
        eq.systeme = modele

        log_audit = JournalAudit(
            action=f"Modification de l'équipement {nom}",
            adresseIP=request.remote_addr or "127.0.0.1",
            resultat="Succès",
            description=f"Nouvelle IP: {adresse_ip}, Type: {type_eq}",
            idUtilisateur=getattr(current_user, 'idUtilisateur', None)
        )
        db.session.add(log_audit)
        db.session.commit()

        flash(f"L'équipement {nom} a été mis à jour.", "success")
    else:
        flash("Veuillez remplir tous les champs obligatoires.", "danger")

    return redirect(url_for('equipements.equipements'))