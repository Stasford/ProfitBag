from alembic import op
import sqlalchemy as sa

revision = '001_create_users_and_coins'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('telegram_id', sa.BigInteger, nullable=False, unique=True)  # Изменено с Text на BigInteger
    )

    op.create_table(
        'user_coins',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('coin', sa.String(10), nullable=False),
        sa.Column('amount', sa.Numeric(18, 8), nullable=False),
        sa.Column('purchase_price', sa.Numeric(18, 8), nullable=False)
    )

def downgrade():
    op.drop_table('user_coins')
    op.drop_table('users')
