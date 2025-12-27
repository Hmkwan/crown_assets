#!/usr/bin/env python3
"""
安全脚本：将缺失 AssetCost 的 Equipment 的 price 写入 AssetCost 表
用法：
  python scripts/populate_assetcost_from_equipment.py --dry-run
  python scripts/populate_assetcost_from_equipment.py --apply

默认只做 dry-run，列出将要创建的记录并计数；使用 --apply 才会实际写入数据库。
"""
import argparse
from datetime import datetime, timezone

from app import create_app, db
from app.models import Equipment, AssetCost


def main(dry_run=True, default_lifespan=5, default_purchase_date=None):
    app = create_app()
    with app.app_context():
        equipments = Equipment.query.outerjoin(AssetCost, Equipment.id == AssetCost.equipment_id).filter(AssetCost.id == None).all()
        to_create = []
        for eq in equipments:
            price = float(eq.price or 0)
            if price <= 0:
                continue
            purchase_date = getattr(eq, 'purchase_date', None) or default_purchase_date or datetime.now(timezone.utc).date()
            payload = {
                'equipment_id': eq.id,
                'purchase_price': price,
                'maintenance_cost': 0,
                'depreciation_rate': 0.2,
                'expected_lifespan': default_lifespan,
                'purchase_date': purchase_date
            }
            to_create.append((eq, payload))

        print(f"Found {len(to_create)} equipments without AssetCost and with positive price.")
        if not to_create:
            return

        for eq, payload in to_create:
            print(f"Equipment id={eq.id} name={eq.name} price={payload['purchase_price']} purchase_date={payload['purchase_date']}")

        if dry_run:
            print("Dry-run mode: no changes applied. Use --apply to write records to DB.")
            return

        # apply
        for eq, payload in to_create:
            ac = AssetCost(
                equipment_id=payload['equipment_id'],
                purchase_price=payload['purchase_price'],
                maintenance_cost=payload['maintenance_cost'],
                depreciation_rate=payload['depreciation_rate'],
                expected_lifespan=payload['expected_lifespan'],
                purchase_date=payload['purchase_date']
            )
            db.session.add(ac)
        db.session.commit()
        print(f"Inserted {len(to_create)} AssetCost records.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Populate AssetCost from Equipment.price')
    parser.add_argument('--apply', action='store_true', help='Actually write records to DB')
    parser.add_argument('--lifespan', type=int, default=5, help='Default expected lifespan in years')
    args = parser.parse_args()
    main(dry_run=not args.apply, default_lifespan=args.lifespan)
