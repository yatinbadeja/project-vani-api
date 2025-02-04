"""------------------------------------------------------------------------------------------------------------------------
                                                    TEMPLATE MODULE
------------------------------------------------------------------------------------------------------------------------"""

from datetime import datetime
from app.Config import ENV_PROJECT

# import pytz


# def Date_Time(Time_Zone):
#     return datetime.now(pytz.timezone(Time_Zone)).strftime("%d/%m/%Y %H:%M:%S")


class Template:
    """
    TEMPLATE MODULE
    ---------------
    Parser for Dynamic html Render & Storage

    ATTRIBUTES
    ----------
    - directory
    - challenge_html
    - confirmation_html
    - admin_html
    - credentials_html
    - welcome_html
    - recovery_html

    METHODS
    -------
    - render_template( path, parser )
    - Challenge( link, agenda )
    - Credentials( Merchant_ID, Merchant_PIN, API_KEY, agenda )
    - Recovery( today )
    ...
    """

    # --------------------------------------------------------------------------------------------------------------------------

    def __init__(self, domain, env):
        # Initialise html paths
        self.directory = "app/utils/templates/mail/"
        self.domain = domain
        self.onboard_html = self.directory + "onboard.html"
        self.forgot_password = self.directory + "forgot_password.html"
        self.subdomain = "dev" if env == "dev" else ""

    # --------------------------------------------------------------------------------------------------------------------------

    def render_template(self, path, parser):
        """
        RENDER_TEMPLATE
        ---------------
        Renders the html file from *path* by replacing *parser* arguments,
        and returns the rendered string.
        ...
        """

        # Open html file
        with open(
            path,
            "r",
            encoding="utf8",
        ) as html:
            # Extract content
            content = html.read()
            # Replace parser arguments
            for key in parser:
                content = content.replace(
                    "{" + key + "}",
                    str(parser[key]),
                )
            # content = content.replace(
            #     "{domain}",
            #     self.domain,
            # )
            # Return content
            return content

    # --------------------------------------------------------------------------------------------------------------------------

    def Recovery(self, link, agenda=""):
        """
        RECOVERY_TEMPLATE
        --------------------
        ...
        """

        # parser arguments

        parser = {"link": link}

        # return merchant password reset alert html
        if agenda == "forgot":
            return self.render_template(
                self.forgot_password,
                parser,
            )

    # --------------------------------------------------------------------------------------------------------------------------

    def Onboard(self, role, email, password):
        parser = {
            "link": "https://" + self.subdomain + role + self.domain,
            "email": email,
            "password": password,
            "role": role,
        }
        return self.render_template(self.onboard_html, parser)


"""------------------------------------------------------------------------------------------------------------------------
                                                    TEMPLATE MODULE
------------------------------------------------------------------------------------------------------------------------"""
