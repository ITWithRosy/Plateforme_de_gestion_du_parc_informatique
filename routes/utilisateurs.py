from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db
from models.utilisateur import Utilisateur
from models.role import Role
from routes.journal import logger_action

utilisateurs_bp = Blueprint('utilisateurs', __name__)

@utilisateurs_bp.route('/utilisateurs')
@login_required
@admin_required
def utilisateurs():
    """Affiche la liste complète des comptes utilisateurs et la gestion des rôles."""
    utilisateurs_list = Utilisateur.query.all()
    roles = Role.query.all()
    return render_template('utilisateurs.html', utilisateurs_list=utilisateurs_list, roles=roles)

@utilisateurs_bp.route('/utilisateurs/ajouter', methods=['POST'])
@login_required
@admin_required
def ajouter_utilisateur():
    """Crée un nouvel utilisateur dans le système."""
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    password = request.form.get('motDePasse')
    id_role = request.form.get('idRole')

    if Utilisateur.query.filter_by(email=email).first():
        flash("Cet email est déjà attribué à un autre compte.", "danger")
        return redirect(url_for('utilisateurs.utilisateurs'))

    nouvel_user = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        idRole=id_role
    )
    nouvel_user.set_password(password)

    db.session.add(nouvel_user)
    db.session.commit()

    logger_action(
        action="Création utilisateur", 
        description=f"Création du compte utilisateur : {email}"
    )
    flash("Utilisateur créé avec succès.", "success")
    return redirect(url_for('utilisateurs.utilisateurs'))


@utilisateurs_bp.route('/utilisateurs/modifier/<int:id>', methods=['POST'])
@login_required
@admin_required
def modifier_utilisateur(id):
    """Met à jour les informations ou les droits d'un utilisateur existant."""
    user = db.session.get(Utilisateur, id)
    if user:
        user.nom = request.form.get('nom')
        user.prenom = request.form.get('prenom')
        user.email = request.form.get('email')
        user.idRole = request.form.get('idRole')
        
        new_password = request.form.get('motDePasse')
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        logger_action(
            action="Modification utilisateur", 
            description=f"Mise à jour du compte : {user.email}"
        )
        flash("Compte utilisateur mis à jour avec succès.", "success")
    else:
        flash("Utilisateur introuvable.", "danger")

    return redirect(url_for('utilisateurs.utilisateurs'))

@utilisateurs_bp.route('/utilisateurs/supprimer/<int:id>', methods=['POST'])
@login_required
@admin_required
def supprimer_utilisateur(id):
    """Supprime un compte utilisateur tout en empêchant l'auto-suppression."""
    if id == current_user.idUtilisateur:
        flash("Action impossible : vous ne pouvez pas supprimer votre propre compte.", "warning")
        return redirect(url_for('utilisateurs.utilisateurs'))

    user = db.session.get(Utilisateur, id)
    if user:
        email = user.email
        db.session.delete(user)
        db.session.commit()

        logger_action(
            action="Suppression utilisateur", 
            description=f"Suppression définitive du compte : {email}"
        )
        flash("Utilisateur supprimé de la plateforme.", "info")
    else:
        flash("Utilisateur introuvable.", "danger")

    return redirect(url_for('utilisateurs.utilisateurs'))