from oauth2client.client import Credentials

from django_extensions.db.fields import encrypted


class CredentialsField(encrypted.EncryptedTextField):
    """
    Represents an encrypted credentials field.
    """
    def to_python(self, value):
        if isinstance(value, Credentials):
            return value
        else:
            char = super(CredentialsField, self).to_python(value)
            return Credentials.new_from_json(char)

    def get_db_prep_value(self, value, connection, prepared=False):
        # Store the value as encrypted JSON.
        value = value.to_json()
        return super(CredentialsField, self).get_db_prep_value(value, connection, prepared)
