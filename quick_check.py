from app import create_app
from app.models import User
from app.chat_models import ChatParticipant, ChatConversation
import sys

try:
    app = create_app()
    with app.app_context():
        admin = User.query.first()
        parts = ChatParticipant.query.filter_by(user_id=admin.id, is_left=False).all()
        msg = f'用户 {admin.username} (ID:{admin.id}) 参与了 {len(parts)} 个会话'
        print(msg, flush=True)
        sys.stdout.flush()
        for p in parts:
            conv = p.conversation
            line = f'  会话{conv.id}: {conv.name} ({conv.conversation_type})'
            print(line, flush=True)
            sys.stdout.flush()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
