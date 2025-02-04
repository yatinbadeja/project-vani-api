"""------------------------------------------------------------------------------------------------------------------------
                                                  EMAILER MODULE
------------------------------------------------------------------------------------------------------------------------"""

import smtplib
import ssl

# Email Dependencies
from email.message import EmailMessage

# Environment Variables Dependencies
from app.Config import ENV_PROJECT
from app.utils.templates.parser import Template


class Emailer:
    """
    EMAILER
    -------
    Email Sever on SMTP with Secure SSL

    ATTRIBUTES
    ----------
    - EMAIL_ADDRESS
    - EMAIL_PASSWORD
    - MAIL_SERVER
    - PORT

    """

    # ------------------------------------------------------------------------------------------------------------

    def __init__(
        self,
    ) -> None:
        # Initialise Email Server Credentials
        self.EMAIL_ADDRESS = ENV_PROJECT.EMAIL_ADDRESS
        self.EMAIL_PASSWORD = ENV_PROJECT.EMAIL_PASSWORD
        self.MAIL_SERVER = ENV_PROJECT.EMAIL_SERVER
        self.PORT = 465

    # ------------------------------------------------------------------------------------------------------------

    def send(
        self,
        subject,
        email,
        content,
    ) -> None:
        """
        send
        ------

        Sends Email to Clients.

        ATTRIBUTES
        ----------
        - subject
        - email
        - content

        """

        # Initialise Message & SSL Context
        ssl_context = ssl.create_default_context()
        msg = EmailMessage()

        # Email Constructor
        msg["From"] = "DristiDocs App <{email}>".format(email=self.EMAIL_ADDRESS)
        msg["To"] = email
        msg["Subject"] = subject
        msg.add_alternative(
            content,
            subtype="html",
        )

        # Send Mail
        with smtplib.SMTP_SSL(
            self.MAIL_SERVER,
            self.PORT,
            context=ssl_context,
        ) as smtp:
            smtp.login(
                self.EMAIL_ADDRESS,
                self.EMAIL_PASSWORD,
            )
            smtp.send_message(msg)


template = Template(ENV_PROJECT.FRONTEND_DOMAIN, ENV_PROJECT.ENV)
mail = Emailer()
