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