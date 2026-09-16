from datetime import datetime, timezone
from models import db

class Alerte(db.Model):
    __tablename__ = 'alertes'

    idAlerte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    niveau = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    dateCreation = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    statut = db.Column(db.String(20), default="Non résolue")
    
    # Clé étrangère liée à l'équipement
    idEquipement = db.Column(db.Integer, db.ForeignKey('equipements.idEquipement'), nullable=True)
    equipement = db.relationship('Equipement', backref='alertes')

    def __repr__(self):
        return f"<Alerte [{self.niveau}] {self.titre}>"