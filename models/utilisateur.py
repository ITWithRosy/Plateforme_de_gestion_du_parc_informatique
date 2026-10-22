from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'

    idUtilisateur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    motDePasse = db.Column(db.String(255), nullable=False)
    dateCreation = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    statut = db.Column(db.String(20), default="Actif")
    
    # Relation avec la table des rôles
    idRole = db.Column(db.Integer, db.ForeignKey('roles.idRole'), nullable=False)
    role = db.relationship('Role', backref='utilisateurs')

#Hachage du mot de passe avant enregistrement en base de données.
    def set_password(self, password):
        self.motDePasse = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.motDePasse, password)
    

    def get_id(self):
        #Retourne l'identifiant sous forme de chaîne pour Flask-Login.
        return str(self.idUtilisateur)

    def __repr__(self):
        return f"<Utilisateur {self.email}>"