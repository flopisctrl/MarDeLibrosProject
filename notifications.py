from flask_mail import Mail, Message
from flask import current_app
from datetime import timedelta, datetime
from models import Book
from extensions import db
import logging

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_notification(subject, recipient, body):
    with current_app.app_context():
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[recipient]
        )
        msg.body = body
        mail.send(msg)

def send_book_request_notification(user_email,book_title):
    with current_app.app_context():
        subject = "Solicitud de libro realizada"
        body = f"""
                Hola!,

                Has solicitado el libro: {book_title}.

                Por favor, recuerda que debes devolverlo en el plazo establecido. 
                ¡Gracias por usar Mar de Libros!

                Atentamente,
                El equipo de Mar de Libros.
                """
        print(f"Correo del destinatario: {user_email}")
        send_notification(subject,user_email,body)

def send_registration_email(user_email):
    with current_app.app_context():
        subject = 'Bienvenido a Mar de Libros'
        body = f'Hola, gracias por registrarte en Mar de Libros. ¡Ya puedes comenzar a explorar los libros disponibles!'

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        msg.body = body

        mail.send(msg)
    
def send_expiration_warnings():
    logging.basicConfig(level=logging.INFO)
    logging.info("Iniciando el proceso de enviar notificaciones.")

    with current_app.app_context():

        warning_threshold = timedelta(hours=48)
        now = datetime.now()

        books = Book.query.filter(
            Book.expiration_date != None,
            Book.notification_sent == False
        ).all()

        for book in books:
            logging.info(f"Procesando libro: {book.title} con expiración: {book.expiration_date}")
            expiration_date= book.expiration_date
            warning_date = expiration_date - warning_threshold


        if warning_date <= now < expiration_date:
            user_email = book.requested_by.email
            book_title = book.title

            subject= "Aviso: El plazo está por vencer"
            body=  f""" Hola, Te recordamos que el plazo para devolver el libro "{book_title}" vence el {expiration_date.strftime('%d/%m/%Y %H:%M')}. Por favor, asegúrate de devolverlo a tiempo para evitar sanciones. ¡Gracias por usar Mar de Libros! Atentamente, El equipo de Mar de Libros."""
            
            send_notification(subject, user_email, body)
            logging.info(f"Correo enviado a {user_email} por el libro {book_title} (Expira: {expiration_date}).")
            book.notification_sent = True
            db.session.commit()