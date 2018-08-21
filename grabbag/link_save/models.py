from django.db import models

import bcrypt
import hashlib
import base64

PW_HASH_ROUNDS=12

class User(models.Model):
    username = models.CharField(max_length=75)
    email = models.EmailField()
    password_hash = models.BinaryField()
    add_date = models.DateField(auto_now_add=True)

    def set_password(self, password):
        # bcrypt only handles 72-char passwords, so hash it first.
        hash = base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest())
        pw_hash = bcrypt.hashpw(hash, bcrypt.gensalt(PW_HASH_ROUNDS))
        self.password_hash = pw_hash

    def password_matches(self, password):
        hash = base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest())
        bcrypt.checkpw(hash, self.password_hash)

class APIToken(models.Model):
    token_id = models.CharField(max_length=100, primary_key=True)
    expiration = models.DateTimeField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
