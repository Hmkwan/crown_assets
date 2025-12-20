"""添加系统公告表

Revision ID: add_announcements_table
Revises: 
Create Date: 2025-12-02

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_announcements_table'
down_revision = None  # 根据实际情况修改
branch_labels = None
depends_on = None


def upgrade():
    """创建系统公告表"""
    op.create_table('announcements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, comment='公告标题'),
        sa.Column('content', sa.Text(), nullable=False, comment='公告内容'),
        sa.Column('type', sa.String(length=20), nullable=False, comment='公告类型'),
        sa.Column('priority', sa.String(length=20), nullable=False, comment='优先级'),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, comment='是否置顶'),
        sa.Column('is_published', sa.Boolean(), nullable=True, comment='是否发布'),
        sa.Column('publish_time', sa.DateTime(), nullable=True, comment='发布时间'),
        sa.Column('expire_time', sa.DateTime(), nullable=True, comment='过期时间'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('creator_id', sa.Integer(), nullable=False, comment='创建者ID'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引以优化查询
    op.create_index('idx_announcements_published', 'announcements', ['is_published'])
    op.create_index('idx_announcements_pinned', 'announcements', ['is_pinned'])
    op.create_index('idx_announcements_type', 'announcements', ['type'])
    op.create_index('idx_announcements_publish_time', 'announcements', ['publish_time'])


def downgrade():
    """删除系统公告表"""
    op.drop_index('idx_announcements_publish_time', table_name='announcements')
    op.drop_index('idx_announcements_type', table_name='announcements')
    op.drop_index('idx_announcements_pinned', table_name='announcements')
    op.drop_index('idx_announcements_published', table_name='announcements')
    op.drop_table('announcements')
