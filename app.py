from flask import Flask, g, render_template, flash, url_for, redirect, abort
from flask_login import LoginManager, login_user, login_required, current_user,logout_user, AnonymousUserMixin
from flask_bcrypt import check_password_hash

import forms
import models

DEBUG = True
PORT = 8000
HOST = '127.0.0.1'


app = Flask(__name__)
app.secret_key = 'asdASDVCXnjdj12i5nfiefASwinASDf!njf3·#@€dnjasnd1'

##SI NO HAY UN USUARIO REGISTRADO
class Anonyimous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Invitado'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonyimous


@login_manager.user_loader
def  load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

#FUNCION PARA CONECTAR A LA BASE DE DATOS
@app.before_request
def before_request():
    """ Conecta a la base de datos antes de cada request """
    # if not hasattr(g, 'db'):
    g.db = models.DATABASE
    if g.db.is_closed():
        g.db.connect()
        g.user = current_user

#FUNCION PARA CERRAR SESION DE LA BASE DE DATOS
@app.after_request
def after_request(response):
    """ Cerramos la conexion a la DB """
    g.db.close()
    return response

##RUTA Y FUNCION PARA VER EL POST
@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream = posts)

##RUTA Y FUNCION PARA SEGUIR A UN USUARIO
@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user= g.user._get_current_object(),
                to_user = to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash('Ahora siguesa  {}'.format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))

##RUTA Y FUNCION PARA DEJAR DE SEGUIR AUN USUARIO
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user.__get_current_object(),
                to_user = to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash('Has dejado de seguir a {}'.format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))

##RUTA Y FUNCION PARA REGISTRAR A UN USUARIO
@app.route('/register', methods = ('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Fuiste Registrado con exito!!" "success")
        models.User.create_user(
            username= form.username.data,
            email= form.email.data,
            password= form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form = form)

##RUTA Y FUNCION PARA HACER LOGIN 
@app.route('/login',methods=('GET','POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Error el ingresar verifique usuario o contraseña','error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Has iniciado sesion', 'success')
                return redirect(url_for('index'))
    return render_template('login.html', form = form)

##RUTA Y FUNCION PARA CERRAR SESION
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesion", 'success')
    return redirect(url_for('index'))

##RUTA Y FUNCION PARA CREAR UN NUEVO POST
@app.route('/new_post', methods=('GET','POST'))
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(
            user = g.user._get_current_object(),
            content = form.content.data.strip())
        flash('Mensaje Creado', 'Success')
        return redirect(url_for('index'))
    return render_template('post.html', form = form)

#RUTA Y FUNCION PARA IR AL INDEX
@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream = stream)

##RUTA  Y FUNCION PARA VER UN USUARIO EN ESPECIFICO
@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream = stream, user = user)

#RUTA Y FUNCION PARA EL ERROR 404
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'),404



if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = 'aldo',
            email = 'aldo@hotmail.com',
            password= 'aldo123',
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
