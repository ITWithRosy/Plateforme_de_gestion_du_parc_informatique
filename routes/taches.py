import os
import subprocess
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db
from models.tache import TacheAutomatisee
from routes.journal import logger_action

taches_bp = Blueprint('taches', __name__)

@taches_bp.route('/taches')
@login_required
@admin_required
def taches():
    """Affiche le panneau de gestion et de suivi des tâches automatisées."""
    taches_list = TacheAutomatisee.query.order_by(TacheAutomatisee.idTache.desc()).all()
    
    total = len(taches_list)
    en_attente = len([t for t in taches_list if t.statut in ['En attente', 'Planifié']])
    terminees = len([t for t in taches_list if t.statut in ['Terminé', 'Succès']])

    return render_template(
        'taches.html', 
        taches=taches_list, 
        total=total, 
        en_attente=en_attente, 
        terminees=terminees
    )

@taches_bp.route('/taches/ajouter', methods=['POST'])
@login_required
@admin_required
def ajouter_tache():
    """Enregistre un nouveau script ou tâche d'automatisation."""
    nom = request.form.get('nom')
    script = request.form.get('script')
    description = request.form.get('description')
    user_id = getattr(current_user, 'idUtilisateur', None)

    if nom and script:
        nouvelle_tache = TacheAutomatisee(
            nom=nom,
            script=script,
            description=description,
            statut="En attente",
            idUtilisateur=user_id
        )
        db.session.add(nouvelle_tache)
        db.session.commit()

        logger_action(
            action=f"Création de la tâche {nom}",
            description=f"Script associé: {script}"
        )

        flash("La tâche automatique a été enregistrée avec succès.", "success")
    else:
        flash("Veuillez renseigner le nom et le script de la tâche.", "danger")

    return redirect(url_for('taches.taches'))

@taches_bp.route('/taches/executer/<int:id>', methods=['POST'])
@login_required
@admin_required
def executer_tache(id):
    """Exécute manuellement le script associé à une tâche et enregistre le résultat."""
    tache = db.session.get(TacheAutomatisee, id)

    if not tache:
        flash("Tâche introuvable.", "danger")
        return redirect(url_for('taches.taches'))

    script_path = tache.script.strip()
    
    # Vérification de l'existence physique du fichier script
    if not os.path.exists(script_path):
        tache.statut = "Échec (Fichier introuvable)"
        resultat_log = "Échec"
        msg = f"Impossible de trouver le fichier script à l'emplacement : {script_path}"
        flash_type = "danger"
    else:
        try:
            process = subprocess.run(
                [script_path], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if process.returncode == 0:
                tache.statut = "Terminé"
                resultat_log = "Succès"
                msg = f"La tâche '{tache.nom}' a été exécutée avec succès."
                flash_type = "success"
            else:
                tache.statut = "Échec"
                resultat_log = "Échec"
                msg = f"Erreur lors de l'exécution du script (Code {process.returncode}) : {process.stderr}"
                flash_type = "warning"

        except Exception as e:
            tache.statut = "Échec"
            resultat_log = "Échec"
            msg = f"Exception système : {str(e)}"
            flash_type = "danger"

    tache.dateExecution = datetime.now(timezone.utc)

    logger_action(
        action=f"Exécution tâche #{id} ({tache.nom})",
        description=msg[:255],
        resultat=resultat_log
    )
    db.session.commit()

    flash(msg, flash_type)
    return redirect(url_for('taches.taches'))


@taches_bp.route('/taches/modifier/<int:id>', methods=['POST'])
@login_required
@admin_required
def modifier_tache(id):
    """Met à jour les paramètres d'une tâche d'automatisation."""
    tache = db.session.get(TacheAutomatisee, id)
    if tache:
        nom_ancien = tache.nom
        tache.nom = request.form.get('nom')
        tache.script = request.form.get('script')
        tache.description = request.form.get('description')
        
        db.session.commit()
        
        logger_action(
            action=f"Modification tâche #{id}",
            description=f"Mise à jour de la tâche '{nom_ancien}' -> '{tache.nom}'"
        )
        flash(f"La tâche '{tache.nom}' a été modifiée avec succès.", "success")
    else:
        flash("Tâche introuvable.", "danger")

    return redirect(url_for('taches.taches'))


@taches_bp.route('/taches/supprimer/<int:id>', methods=['POST'])
@login_required
@admin_required
def supprimer_tache(id):
    """Supprime définitivement une tâche d'automatisation."""
    tache = db.session.get(TacheAutomatisee, id)
    if tache:
        nom_tache = tache.nom
        db.session.delete(tache)
        db.session.commit()

        logger_action(
            action=f"Suppression tâche #{id}",
            description=f"Suppression de la tâche '{nom_tache}'"
        )
        flash("La tâche a été supprimée.", "info")
    else:
        flash("Tâche introuvable.", "danger")

    return redirect(url_for('taches.taches'))