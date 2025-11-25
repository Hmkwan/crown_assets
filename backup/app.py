from app import create_app, db
from app.models import User, Equipment, RepairOrder, SparePart, PartReplacement

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Equipment': Equipment,
        'RepairOrder': RepairOrder,
        'SparePart': SparePart,
        'PartReplacement': PartReplacement
    }