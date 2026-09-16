import os
import socket
import webbrowser
from threading import Timer
from dotenv import load_dotenv

from flask import Flask, request
from flask_login import LoginManager, current_user

from models import db
from models.role import Role
from models.utilisateur import Utilisateur

from routes.alertes import alertes_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.equipements import equipements_bp
from routes.journal import journal_bp, logger_action
from routes.rapports import rapports_bp
from routes.taches import taches_bp
from routes.utilisateurs import utilisateurs_bp


app = Flask(__name__)
load_dotenv()

# Configurations de l'application
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adminsysteme:UNDERCOVER@192.168.10.5:5432/plateforme_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')
app.config['TEMPLATES_AUTO_RELOAD'] = True 

# Initialisation de la base de données
db.init_app(app)

# Configuration de la gestion des sessions utilisateurs (Flask-Login)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    """Charge l'utilisateur actuellement connecté via son ID."""
    return db.session.get(Utilisateur, int(user_id))

# Initialisation de la base de données et des rôles par défaut au démarrage
with app.app_context():
    db.create_all()
    if not Role.query.filter_by(nomRole="Administrateur").first():
        admin_role = Role(
            nomRole="Administrateur",
            description="Accès total à la plateforme",
            niveau_acces=2
        )
        db.session.add(admin_role)
        db.session.commit()
        print("Rôle Administrateur initialisé avec succès !")
    else:
        print("Base de données PostgreSQL synchronisée.")

# Traçabilité automatique des accès aux sections principales
@app.after_request
def tracer_navigation(response):
    """Enregistre les accès aux sections principales dans le journal d'audit."""
    if response.status_code == 200 and request.endpoint and request.method == 'GET':
        if current_user and current_user.is_authenticated:
            endpoints_a_tracer = {
                'equipements.equipements': ('Consultation Équipements', "Accès à l'inventaire et état du parc"),
                'alertes.alertes': ('Consultation Alertes', "Consultation du panneau d'incidents"),
                'rapports.rapports': ('Consultation Rapports', "Accès aux bilans et statistiques réseau"),
                'journal.journal': ('Consultation Journal Audit', "Consultation des logs d'activité"),
                'utilisateurs.utilisateurs': ('Consultation Utilisateurs', "Accès à la gestion des comptes"),
                'taches.taches': ('Consultation Tâches', "Accès aux tâches automatisées")
            }
            
            if request.endpoint in endpoints_a_tracer:
                action, desc = endpoints_a_tracer[request.endpoint]
                logger_action(action=action, description=desc)

    return response

# Enregistrement des Blueprints (Routes)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(equipements_bp)
app.register_blueprint(alertes_bp)
app.register_blueprint(taches_bp)
app.register_blueprint(rapports_bp)
app.register_blueprint(utilisateurs_bp)
app.register_blueprint(journal_bp)

def get_local_ip():
    """Détermine l'adresse IP locale active de la machine hôte."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def open_browser():
    """Ouvre automatiquement le navigateur sur l'adresse du serveur."""
    ip_actuelle = get_local_ip()
    webbrowser.open(f'https://{ip_actuelle}:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc', port=5000)