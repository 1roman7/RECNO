from app.db.database import engine, SessionLocal
from app.db.models import Base, Admin, PanelConfig
from app.api.endpoints.auth import get_password_hash

try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Admin).first():
        admin = Admin(username='admin', hashed_password=get_password_hash('admin' * 20)) # Test > 72 bytes
        db.add(admin)
    db.commit()
    db.close()
    print("DB Test Passed")
except Exception as e:
    print(f"DB Test Failed: {e}")
