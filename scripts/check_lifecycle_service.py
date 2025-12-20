from app import create_app

app = create_app()
with app.app_context():
    from app.services import LifecycleService
    stats = LifecycleService.get_lifecycle_dashboard()
    print('lifecycle dashboard stats:')
    print(stats)
