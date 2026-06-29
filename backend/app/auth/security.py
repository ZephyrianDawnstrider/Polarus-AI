from passlib.context import CryptContext


password_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether a plain password matches a bcrypt hash."""

    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt."""

    return password_context.hash(password)
