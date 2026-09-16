from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models.utilisateur import Utilisateur
from routes.journal import logger_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    """Gère l'authentification sécurisée des utilisateurs et la journalisation des accès."""
    if request.method == 'POST':
        email_saisi = request.form.get('email')
        password_saisi = request.form.get('password')
        
        user = Utilisateur.query.filter_by(email=email_saisi).first()
        
        if user and user.check_password(password_saisi):
            login_user(user)
            logger_action(
                action="Connexion au système", 
                description=f"L'utilisateur {user.prenom} {user.nom} s'est connecté."
            )
            return redirect(url_for('dashboard.dashboard'))
        else:
            logger_action(
                action="Échec de connexion", 
                description=f"Tentative de connexion échouée avec l'adresse : {email_saisi}",
                resultat="Échec"
            )
            return render_template('login.html', erreur="Identifiants incorrects")
             
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnecte l'utilisateur courant de sa session."""
    logger_action(
        action="Déconnexion du système", 
        description=f"L'utilisateur {current_user.prenom} {current_user.nom} s'est déconnecté."
    )
    logout_user()
    return redirect(url_for('auth.login'))