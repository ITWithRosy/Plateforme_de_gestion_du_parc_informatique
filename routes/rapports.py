from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from xhtml2pdf import pisa
from werkzeug.security import check_password_hash

from models import db
from models.rapport import Rapport
from models.equipement import Equipement
from models.alerte import Alerte
from models.journal import JournalAudit
from utils.decorators import admin_required

rapports_bp = Blueprint('rapports', __name__)

@rapports_bp.route('/rapports')
@login_required
def rapports():
    """Affiche les statistiques globales du parc et l'historique des rapports générés."""
    total_equipements = Equipement.query.count()
    types_count = {}
    for eq in Equipement.query.all():
        types_count[eq.type] = types_count.get(eq.type, 0) + 1

    critiques = Alerte.query.filter_by(niveau='Critique').count()
    avertissements = Alerte.query.filter_by(niveau='Avertissement').count()
    infos = Alerte.query.filter_by(niveau='Info').count()
    total_alertes = critiques + avertissements + infos

    historique_rapports = Rapport.query.order_by(Rapport.dateGeneration.desc()).all()

    return render_template(
        'rapports.html',
        total_equipements=total_equipements,
        types_labels=list(types_count.keys()),
        types_values=list(types_count.values()),
        critiques=critiques,
        avertissements=avertissements,
        infos=infos,
        total_alertes=total_alertes,
        rapports=historique_rapports
    )

@rapports_bp.route('/rapports/generer', methods=['POST'])
@login_required
def generer_rapport():
    titre = request.form.get('titre', 'Rapport Synthétique & Interventions')
    type_rapport = request.form.get('type', 'Complet')
    user_id = getattr(current_user, 'idUtilisateur', getattr(current_user, 'id', None))

    equipements = Equipement.query.all()
    # Utilisation directe de dateCreation
    journaux = JournalAudit.query.order_by(JournalAudit.dateCreation.desc()).limit(20).all()

    nouveau_rapport = Rapport(
        titre=titre,
        dateGeneration=datetime.now(),
        type=type_rapport,
        contenu=f"Rapport incluant {len(equipements)} équipements et {len(journaux)} événements.",
        cheminFichier=f"Rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        idUtilisateur=user_id
    )
    db.session.add(nouveau_rapport)
    db.session.commit()

    html_rendered = render_template(
        'pdf_rapport.html',
        equipements=equipements,
        journaux=journaux,
        derniers_evenements=journaux,
        rapport=nouveau_rapport,
        current_user=current_user
    )

    pdf_buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html_rendered.encode("utf-8")), dest=pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=nouveau_rapport.cheminFichier,
        mimetype='application/pdf'
    )

@rapports_bp.route('/rapports/telecharger/<int:id>', methods=['GET'])
@login_required
def telecharger_rapport(id):
    rapport = Rapport.query.get_or_404(id)
    equipements = Equipement.query.all()
    journaux = JournalAudit.query.order_by(JournalAudit.dateCreation.desc()).limit(10).all()

    html_rendered = render_template(
        'pdf_rapport.html',
        equipements=equipements,
        journaux=journaux,
        derniers_evenements=journaux,
        rapport=rapport,
        current_user=current_user
    )

    pdf_buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html_rendered.encode("utf-8")), dest=pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=rapport.cheminFichier or f"Rapport_{rapport.idRapport}.pdf",
        mimetype='application/pdf'
    )

@rapports_bp.route('/rapports/supprimer/<int:id>', methods=['POST'])
@login_required
@admin_required
def supprimer_rapport(id):
    pwd_saisi = request.form.get('password_check')
    if not pwd_saisi or not check_password_hash(current_user.motDePasse, pwd_saisi):
        flash("Mot de passe incorrect ! Action annulée.", "danger")
        return redirect(url_for('rapports.rapports'))
    rapport = db.session.get(Rapport, id)
    
    if rapport:
        db.session.delete(rapport)
        db.session.commit()
        flash("Rapport archivé supprimé.", "info")
    return redirect(url_for('rapports.rapports'))