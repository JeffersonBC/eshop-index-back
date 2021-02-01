from djmail import template_mail


class AccountActivationEmail(template_mail.TemplateMail):
    name = "account_activation"


class AccountPasswordResetEmail(template_mail.TemplateMail):
    name = "account_password_reset"
