import csv
from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db
from models.journal import JournalAudit

journal_bp = Blueprint('journal', __name__)

def logger_action(action, description, resultat="Succès"):
    """Fonction utilitaire globale pour enregistrer une action dans le journal d'audit."""
    user_id = getattr(current_user, 'idUtilisateur', None)
    if user_id:
        try:
            log = JournalAudit(
                action=action,
                description=description,
                resultat=resultat,
                adresseIP=request.remote_addr or "127.0.0.1",
                idUtilisateur=user_id
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur enregistrement log : {e}")

@journal_bp.route('/journal')
@login_required
@admin_required
def journal():
    """Consulte l'historique d'audit avec options de recherche et de filtres par dates."""
    date_debut_str = request.args.get('date_debut')
    date_fin_str = request.args.get('date_fin')
    heure_debut_str = request.args.get('heure_debut', '00:00')
    heure_fin_str = request.args.get('heure_fin', '23:59')
    recherche = request.args.get('q', '').strip()

    query = JournalAudit.query
    if date_debut_str:
        try:
            d_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            h_debut = datetime.strptime(heure_debut_str, '%H:%M').time()
            query = query.filter(JournalAudit.dateCreation >= datetime.combine(d_debut, h_debut))
        except ValueError:
            pass

    if date_fin_str:
        try:
            d_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
            h_fin = datetime.strptime(heure_fin_str, '%H:%M').time()
            query = query.filter(JournalAudit.dateCreation <= datetime.combine(d_fin, h_fin))
        except ValueError:
            pass

    if recherche:
        query = query.filter(
            (JournalAudit.action.ilike(f"%{recherche}%")) | 
            (JournalAudit.description.ilike(f"%{recherche}%"))
        )
    logs = query.order_by(JournalAudit.dateCreation.desc()).all()

    return render_template(
        'journal.html', 
        logs_list=logs,
        date_debut=date_debut_str,
        date_fin=date_fin_str,
        heure_debut=heure_debut_str,
        heure_fin=heure_fin_str,
        recherche=recherche
    )

@journal_bp.route('/journal/exporter')
@login_required
@admin_required
def exporter_journal():
    """Exporte l'ensemble des événements du journal d'audit au format CSV."""
    logger_action(
        action="Exportation des logs", 
        description="L'utilisateur a téléchargé l'historique du journal d'audit au format CSV."
    )
    logs = JournalAudit.query.order_by(JournalAudit.dateCreation.desc()).all()

    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['ID Log', 'Date Creation (UTC)', 'ID Utilisateur', 'Utilisateur', 'Action', 'Resultat', 'Adresse IP', 'Description'])

    for log in logs:
        nom_user = f"{log.utilisateur.prenom} {log.utilisateur.nom}" if log.utilisateur else "Inconnu"
        date_str = log.dateCreation.strftime('%d/%m/%Y %H:%M:%S') if log.dateCreation else ''
        writer.writerow([log.idJournal, date_str, log.idUtilisateur, nom_user, log.action, log.resultat, log.adresseIP, log.description or ''])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=journal_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )