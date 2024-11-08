
from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
db = SQLAlchemy()

from models import db, User, Book
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'

db.init_app(app)

with app.app_context():
    db.create_all()

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: #or session.get('user_role') != 'ADMIN'#
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/main", methods=['GET','POST'])
def main():
    
    if request.method == 'POST':
        
        email = request.form["email"]
        password = request.form["password"]
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_role'] = user.rol
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if user.rol == "ADMIN":
                admin_name = User.query.get(session['user_id']).name
                books = Book.query.all()
                users = User.query.all()
                return render_template("admin_main.html", books=books, users=users, admin_name=admin_name)
            else:
                if user.rol == "CLIENT":
                    books = Book.query.all()
                    return render_template("client_main.html", books=books)
        else: 
            error_message = "correo electrónico o contraseña incorrectos"
            return render_template("login.html", error=error_message)
   
    search_query = request.args.get('search')
    if search_query:
        books = Book.query.filter(Book.title.ilike(f'%{search_query}%')).all() or Book.query.filter(Book.author.ilike(f'%{search_query}%')).all() or Book.query.filter(Book.genre.ilike(f'%{search_query}%')).all()
        return render_template("client_main.html", books=books)
    else:
        
        books = Book.query.all()  
        print(f"Número de libros disponibles: {len(books)}")
        return render_template("client_main.html", books=books)



@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/handle_register", methods = ['POST'])
def handle_register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return render_template("error.html", mensaje="El correo electrónico ya está registrado.")
    new_user = User(name = name, password = password, email = email)

    db.session.add(new_user)
    db.session.commit()

    print(f"Usuario {name} guardado")

    return render_template("login.html")

@app.route('/admin', methods=['GET', 'POST'])
@login_required_admin
def admin():
    
    admin_name = User.query.get(session['user_id']).name
    users = User.query.all()
    
    if request.method == 'POST':
        if 'delete_id' in request.form:
            book_id = request.form['delete_id']
            book_to_delete = Book.query.get(book_id)
            if book_to_delete:
                db.session.delete(book_to_delete)
                db.session.commit()
                print(f"Libro {book_to_delete.title} eliminado")
            else:
                print("Libro no encontrado")
        else:
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            cover_image_path = None
            
            if 'cover_image' in request.files:
                file = request.files['cover_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                    file.save(file_path)
                    cover_image_path = f"uploads/{filename}"
                else:
                    cover_image_path = None

            new_book = Book(
                title=title, 
                author=author, 
                genre=genre,
                cover_image=cover_image_path
            )
            db.session.add(new_book)
            db.session.commit()

            print(f"Libro {title} guardado")

    admin_name = User.query.get(session['user_id']).name
    search_query = request.args.get('search')
    if search_query:
        books = Book.query.filter(Book.title.ilike(f'%{search_query}%')).all()
    else:
        books = Book.query.all()

    return render_template('admin_main.html', books=books, users=users, admin_name=admin_name)

@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def loan_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return "Libro no encontrado", 404

    if request.method == 'POST' and book.available:
        #preguntar user en sesion
        book.available = False
        book.requested_by = session['user_id']
        db.session.commit()
        print(f"Solicitando libro {book.title} por el usuario ID: {session['user_id']}")
        flash("Libro solicitado con éxito", "success")
        return redirect('/main')

    return render_template("book.html", book=book)

@app.route("/admin/estudiantes")
@login_required_admin  
def view_users():
    
    users = User.query.all()
    return render_template("view_users.html", users=users)

@app.route('/users/<username>', methods=['GET'])
def user_info(username):
    
    user = User.query.filter_by(name=username).first()
    if not user:
        return redirect(url_for('login'))

    return render_template('user_info.html', user=user)

#@app.route('/logout', methods=['POST'])
#def logout():
    session.pop('user_id', None)  
    return redirect(url_for('login'))  
