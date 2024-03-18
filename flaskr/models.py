import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from flaskr import login, conn
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(60), unique=True, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True, nullable=False)
    passwordhash: so.Mapped[str] = so.mapped_column(sa.String(240), unique=True, nullable=False)
    ta: so.Mapped[int] = so.mapped_column(default=0, nullable=False)

    def __init__(self, id, username, email, passwordhash, ta):
        self.id = id
        self.username = username
        self.email = email
        self.passwordhash = passwordhash
        self.ta = ta

    def __init__(self, username, email, passwordhash):
        self.username = username
        self.email = email
        self.passwordhash = passwordhash

    def getUser(username, password):
        cursor = conn.cursor()
        get_user_command = "SELECT * FROM user_info WHERE username='" + username + "';"
        cursor.execute(get_user_command)
        user_data = cursor.fetchone()
        if user_data is None:
            return None
        if not check_password_hash(user_data['passwordhash'], password):
            return None
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    
    def getUserFromID(id):
        cursor = conn.cursor()
        user_load_command = "SELECT * FROM user_info WHERE id=" + id
        cursor.execute(user_load_command)
        conn.commit()
        return cursor.fetchone()
    
    def createUser(username, email, passwordhash):
        cursor = conn.cursor()
        register_user_command = "INSERT INTO user_info (username, email, passwordhash) VALUES (" + username + ", " + email + ", "
        + passwordhash + ");"
        try:
            cursor.execute(register_user_command)
            conn.commit()
            return User(username, email, passwordhash)
        except:
            return None

@login.user_loader
def load_user(id):
    return User.get_id(int(id))