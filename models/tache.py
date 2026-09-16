from datetime import datetime, timezone
from models import db

class TacheAutomatisee(db.Model):
    """Modèle représentant les tâches automatiques et scripts de maintenance."""
    __tablename__ = 'taches_automatisees'

    idTache = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    script = db.Column(db.String(150), nullable=False)
    dateExecution = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    statut = db.Column(db.String(50), default="En attente")
    
    # Utilisateur responsable du lancement de la tâche
    idUtilisateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.idUtilisateur'), nullable=False)

    def __repr__(self):
        return f"<TacheAutomatisee {self.nom} - {self.statut}>"