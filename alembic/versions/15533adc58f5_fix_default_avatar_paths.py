"""fix default avatar paths

Revision ID: 15533adc58f5
Revises: efb5d68316ee
Create Date: 2026-10-03 15:40:05.896902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15533adc58f5'
down_revision: Union[str, Sequence[str], None] = 'efb5d68316ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    stmt = """
        UPDATE users
        SET avatar_path = '/static/assets/avatars/default-user.webp'
        WHERE avatar_path = '/assets/avatars/default-user.webp'
        """
    op.execute(stmt)
    


def downgrade() -> None:
    """Downgrade schema."""
    stmt = """
        UPDATE users
        SET avatar_path = '/assets/avatars/default-user.webp'
        WHERE avatar_path = '/static/assets/avatars/default-user.webp'
        """
    op.execute(stmt)
