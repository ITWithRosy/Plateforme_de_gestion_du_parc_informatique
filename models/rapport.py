from datetime import datetime, timezone
from models import db

class Rapport(db.Model):
    __tablename__ = 'rapports'

    idRapport = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titre = db.Column(db.String(150), nullable=False)
    dateGeneration = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    type = db.Column(db.String(50), nullable=False)
    contenu = db.Column(db.Text, nullable=True)
    cheminFichier = db.Column(db.String(255), nullable=False)
    
    # Relation avec le créateur du rapport
    idUtilisateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.idUtilisateur'), nullable=False)

    def __repr__(self):
        return f"<Rapport {self.titre}>"