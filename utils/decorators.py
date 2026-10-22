from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

#Décorateur de sécurité restreignant l'accès d'une route aux seuls utilisateurs possédant le rôle Administrateur.
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.nomRole != 'Administrateur':
            flash("Vous ne disposez pas des droits nécessaires pour effectuer cette action.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
