import datetime
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

#CREAMOS EL NOMBRE DE NUESTRA BASE DE DATOS
DATABASE = SqliteDatabase('social.db')

#CREAMOS NUESTRA TABLA USUARIO Y SUS ATRIBUTOS
class User( Model,UserMixin):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=250)
    joined_at = DateTimeField(default = datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
    
    def get_posts(self):
        return Post.select().where(Post.user == self)
    
    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )
    
    def following(self):
        """Los usuarios que estamos siguiendo"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """Obtener los usuarios que me siguen"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )


    @classmethod
    def create_user(cls,username, email, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username = username, 
                    email = email,
                    password = generate_password_hash(password),
                )
        except IntegrityError:
            # pass
            raise ValueError('User already exists')

#CREAMOS LA TABLA DE POST
class Post(Model):
    user = ForeignKeyField(
        User,
        related_name='posts',
    )
    timestamp = DateTimeField(default = datetime.datetime.now)
    content = TextField()

    class Meta:
        database = DATABASE 
        order_by = ('-joined_at',)

#CRAMOS LA TABLA RELATIONSHIP
class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            (('from_user', 'to_user'), True),
        )

##CREACION DE LAS TABLAS Y CONEXIONES A LAS BASE DATOS (CONECTAR Y CERRAR)
def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()