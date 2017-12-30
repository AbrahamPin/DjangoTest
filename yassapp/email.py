from django.core.mail import EmailMessage

def sendEmail(subject, recipient_list, message):
    from_email = 'noreply@yaas.com'
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.send()