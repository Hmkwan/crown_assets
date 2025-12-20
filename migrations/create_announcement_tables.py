from app import db
from app.models import Announcement, AnnouncementAttachment

def create_tables():
    db.create_all()
    print("✓ 公告相关表已创建")

if __name__ == "__main__":
    create_tables()