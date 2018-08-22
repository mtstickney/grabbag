from .models import User

class UserExistsException(Exception):
    pass

class DBUserRepo:
    def get_all_users(self):
        return User.objects.all()

    def create_user(self, username, password, email):
        if User.objects.filter(username=username).exists():
            raise UserExistsException("User with username '{}' already exists.".format(username))

        user = User(id=None, username=username, email=email)
        user.set_password(password)
        user.save()
        return user

    def delete_user(self, user):
        user.delete()

    def get_user_by_id(self, user_id):
        return User.objects.get(id=user_id)
