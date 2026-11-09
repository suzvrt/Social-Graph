"""Rules for vertex names typed by the user."""

from socialgraph.config import MAX_NAME_LEN


def normalize_name(raw):
    """Return the canonical form of a typed name: trimmed and capitalized."""
    return raw.strip().capitalize()


def name_error(name):
    """Return a user-facing message explaining why name is invalid, or None if it is valid."""
    if not name:
        return "O nome não pode ser vazio."
    if not name.isalpha():
        return "Números, espaços e símbolos não permitidos."
    if len(name) > MAX_NAME_LEN:
        return "O nome deve ter no máximo %d caracteres." % MAX_NAME_LEN
    return None
