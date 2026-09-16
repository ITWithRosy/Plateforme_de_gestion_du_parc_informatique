from datetime import datetime, timezone
from models import db

class JournalAudit(db.Model):
    __tablename__ = 'journaux_audit'

    idJournal = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(150), nullable=False)
    dateCreation = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    adresseIP = db.Column(db.String(50), nullable=False)
    resultat = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relation avec l'utilisateur ayant exécuté l'action
    idUtilisateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.idUtilisateur'), nullable=False)
    utilisateur = db.relationship('Utilisateur', backref='logs')

    def __repr__(self):
        return f"<JournalAudit {self.action} par ID {self.idUtilisateur}>"