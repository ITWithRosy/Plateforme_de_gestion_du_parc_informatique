from models import db

class Role(db.Model):
    __tablename__ = 'roles'

    idRole = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomRole = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    niveau_acces = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Role {self.nomRole}>'