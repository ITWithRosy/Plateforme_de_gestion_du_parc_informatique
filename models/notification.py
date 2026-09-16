from datetime import datetime, timezone
from models import db

class Notification(db.Model):
    """Modèle gérant l'historique d'envoi des notifications d'alertes."""
    __tablename__ = 'notifications'

    idNotification = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.Text, nullable=False)
    dateEnvoi = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    canal = db.Column(db.String(50), nullable=False)
    statut = db.Column(db.String(20), default="Envoyé")
    
    # Lien avec l'alerte concernée
    idAlerte = db.Column(db.Integer, db.ForeignKey('alertes.idAlerte'), nullable=False)

    def __repr__(self):
        return f"<Notification {self.idNotification} - {self.statut}>"