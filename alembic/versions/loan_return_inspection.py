"""add loan return inspection fields

Revision ID: loan_return_inspection
Revises: 
Create Date: 2025-12-04 15:15:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'loan_return_inspection'
# attach to the equipment_loan placeholder revision so it's not an independent head
down_revision = 'b0a349fa6c4b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 为 equipment_loan 表添加归还验收相关字段（仅在缺失时添加）
    if 'equipment_loan' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('equipment_loan')}
        with op.batch_alter_table('equipment_loan', schema=None) as batch_op:
            # 归还申请相关
            if 'return_request_date' not in cols:
                batch_op.add_column(sa.Column('return_request_date', sa.DateTime(), nullable=True))
            if 'return_notes' not in cols:
                batch_op.add_column(sa.Column('return_notes', sa.Text(), nullable=True))
            if 'return_condition' not in cols:
                batch_op.add_column(sa.Column('return_condition', sa.String(length=64), nullable=True))

            # 验收相关
            if 'inspected_by' not in cols:
                batch_op.add_column(sa.Column('inspected_by', sa.Integer(), nullable=True))
            if 'inspection_date' not in cols:
                batch_op.add_column(sa.Column('inspection_date', sa.DateTime(), nullable=True))
            if 'inspection_notes' not in cols:
                batch_op.add_column(sa.Column('inspection_notes', sa.Text(), nullable=True))
            if 'inspection_result' not in cols:
                batch_op.add_column(sa.Column('inspection_result', sa.String(length=64), nullable=True))

            # 损坏赔偿相关
            if 'damage_compensation' not in cols:
                batch_op.add_column(sa.Column('damage_compensation', sa.Float(), nullable=True, default=0))
            if 'damage_description' not in cols:
                batch_op.add_column(sa.Column('damage_description', sa.Text(), nullable=True))

            # 添加外键约束（仅当列存在且约束不存在时）
            if 'inspected_by' in inspector.get_columns('equipment_loan'):
                # create_foreign_key will error if constraint exists, so guard by checking pg_constraint for Postgres
                if bind.dialect.name == 'postgresql':
                    fk_exists = bind.execute(sa.text("""
                        SELECT 1 FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        WHERE t.relname = 'equipment_loan' AND c.conname = 'fk_loan_inspector'
                    """)).first() is not None
                    if not fk_exists:
                        batch_op.create_foreign_key('fk_loan_inspector', 'app_user', ['inspected_by'], ['id'])
                else:
                    # Non-postgres: attempt to create safely and ignore errors
                    try:
                        batch_op.create_foreign_key('fk_loan_inspector', 'app_user', ['inspected_by'], ['id'])
                    except Exception:
                        pass
    else:
        # equipment_loan table doesn't exist in this DB snapshot; skip
        pass
    
    # 为 equipment 表添加借用配置字段（仅在缺失时添加）
    if 'equipment' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('equipment')}
        with op.batch_alter_table('equipment', schema=None) as batch_op:
            if 'require_return_inspection' not in cols:
                batch_op.add_column(sa.Column('require_return_inspection', sa.Boolean(), nullable=True, default=False))
            if 'allow_loan' not in cols:
                batch_op.add_column(sa.Column('allow_loan', sa.Boolean(), nullable=True, default=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 删除 equipment 表的字段（如果存在）
    if 'equipment' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('equipment')}
        with op.batch_alter_table('equipment', schema=None) as batch_op:
            if 'allow_loan' in cols:
                batch_op.drop_column('allow_loan')
            if 'require_return_inspection' in cols:
                batch_op.drop_column('require_return_inspection')
    
    # 删除 equipment_loan 表的字段（如果存在）
    if 'equipment_loan' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('equipment_loan')}
        with op.batch_alter_table('equipment_loan', schema=None) as batch_op:
            # drop FK if exists
            if bind.dialect.name == 'postgresql':
                fk_exists = bind.execute(sa.text("""
                    SELECT 1 FROM pg_constraint c
                    JOIN pg_class t ON c.conrelid = t.oid
                    WHERE t.relname = 'equipment_loan' AND c.conname = 'fk_loan_inspector'
                """)).first() is not None
                if fk_exists:
                    batch_op.drop_constraint('fk_loan_inspector', type_='foreignkey')
            else:
                try:
                    batch_op.drop_constraint('fk_loan_inspector', type_='foreignkey')
                except Exception:
                    pass

            if 'damage_description' in cols:
                batch_op.drop_column('damage_description')
            if 'damage_compensation' in cols:
                batch_op.drop_column('damage_compensation')
            if 'inspection_result' in cols:
                batch_op.drop_column('inspection_result')
            if 'inspection_notes' in cols:
                batch_op.drop_column('inspection_notes')
            if 'inspection_date' in cols:
                batch_op.drop_column('inspection_date')
            if 'inspected_by' in cols:
                batch_op.drop_column('inspected_by')
            if 'return_condition' in cols:
                batch_op.drop_column('return_condition')
            if 'return_notes' in cols:
                batch_op.drop_column('return_notes')
            if 'return_request_date' in cols:
                batch_op.drop_column('return_request_date')
