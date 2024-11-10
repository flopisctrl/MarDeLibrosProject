from flask_mail import Mail, Message
from flask import current_app

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