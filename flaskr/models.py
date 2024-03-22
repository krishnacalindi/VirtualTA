from flask_login import UserMixin
from flaskr import login, conn
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id, username, email, passwordhash, ta):
        if id != -1:
            self.id = id
            self.username = username
            self.email = email
            self.passwordhash = passwordhash
            self.ta = ta
        else:
            self.username = username
            self.email = email
            self.passwordhash = passwordhash

    def getUser(username, password):
        cursor = conn.cursor()
        get_user_command = "SELECT * FROM user_info WHERE username = ?;"
        cursor.execute(get_user_command, (username,))
        user_data = cursor.fetchone()
        if user_data is None:
            return None
        if not check_password_hash(user_data[3], password):
            return None
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    
    def getUserFromID(id):
        cursor = conn.cursor()
        user_load_command = "SELECT * FROM user_info WHERE id = ?"
        try:
            cursor.execute(user_load_command, (id,))
            temp_row = cursor.fetchone()
            if temp_row is not None:
                return  User(temp_row[0], temp_row[1], temp_row[2], temp_row[3], temp_row[4])
            else:
                return None
        except:
            return None
    
    def createUser(username, email, passwordhash):
        cursor = conn.cursor()
        register_user_command = "INSERT INTO user_info (username, email, passwordhash) VALUES (?, ?, ?);"
        print(register_user_command, (username, email, passwordhash))
        try:
            cursor.execute(register_user_command)
            conn.commit()
            return User(-1, username, email, passwordhash, -1)
        except:
            return None

@login.user_loader
def load_user(id):
    return User.getUserFromID(id)