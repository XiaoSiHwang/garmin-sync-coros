class LoginUser:
    def __init__(self, email, password) -> None:
        self._email = email
        self._password = password
    
    @property
    def email(self):
        return self._email
    
    @property
    def password(self):
        return self._password