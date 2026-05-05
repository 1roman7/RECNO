from app.db.database import SessionLocal, engine
from app.db.models import Base, Admin
from app.api.endpoints.auth import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Check if admin exists
admin = db.query(Admin).filter(Admin.username == "admin").first()
if not admin:
    print("Creating admin user...")
    admin = Admin(username="admin", hashed_password=get_password_hash("0a2819811ab8"))
    db.add(admin)
    db.commit()
else:
    print("Admin exists, updating password...")
    admin.hashed_password = get_password_hash("0a2819811ab8")
    db.commit()

print("Admin configured")
