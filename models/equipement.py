from datetime import datetime, timezone
from models import db

class Equipement(db.Model):
    __tablename__ = 'equipements'

    idEquipement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    adresseIP = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    systeme = db.Column(db.String(50), nullable=True)
    hostid_zabbix = db.Column(db.String(50), nullable=True)
    etat = db.Column(db.String(20), nullable=False, default='inconnu')
    dateAjout = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Equipement {self.nom} - {self.adresseIP}>"