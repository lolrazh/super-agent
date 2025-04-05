"""CLI tools for the application."""
import click
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from auth.utils import get_password_hash

@click.group()
def cli():
    """CLI tools for Super Agent."""
    pass

@cli.command()
@click.option('--username', prompt=True, help='Username for the superuser')
@click.option('--email', prompt=True, help='Email for the superuser')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the superuser')
def createsuperuser(username: str, email: str, password: str):
    """Create a superuser account."""
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        click.echo(f"Superuser {username} created successfully!")
    except Exception as e:
        db.rollback()
        click.echo(f"Error creating superuser: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    cli() 