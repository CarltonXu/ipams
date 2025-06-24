import argparse
from flask import Flask
from app.core.config.settings import Config
from app.models.models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def create_user(username, email, password, is_admin=False, avatar=None):
    app = create_app()
    with app.app_context():
        if User.query.filter_by(email=email).first():
            print(f"User with email '{email}' already exists.")
            return
        new_user = User(
            username=username,
            email=email,
            avatar=avatar or "/src/assets/avatar.jpeg",
            is_admin=is_admin
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Command-line tool to create a user in the database.",
        epilog="Example: python create_user.py -u admin -e admin@example.com -p admin123 -a -v /path/to/avatar.png"
    )
    parser.add_argument("-u", "--username", required=True, help="The username for the new user.")
    parser.add_argument("-e", "--email", required=True, help="The email address for the new user.")
    parser.add_argument("-p", "--password", required=True, help="The password for the new user.")
    parser.add_argument("-a", "--admin", action="store_true", help="Set the user as an administrator.")
    parser.add_argument("-v", "--avatar", help="Path to the user's avatar image.", default=None)

    args = parser.parse_args()

    create_user(
        username=args.username,
        email=args.email,
        password=args.password,
        is_admin=args.admin,
        avatar=args.avatar
    )
