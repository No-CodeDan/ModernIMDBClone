"""Add streaming_services to Movie model

Revision ID: 2d1fb67d5dc7
Revises: e004d6646ebd
Create Date: 2023-10-16 21:56:34.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2d1fb67d5dc7'
down_revision = 'e004d6646ebd'
branch_labels = None
depends_on = None

def upgrade():
    # Add streaming_services column to movie table
    op.add_column('movie', sa.Column('streaming_services', sa.JSON(), nullable=True))
    
    # Add tv_show_id column to rating table
    op.add_column('rating', sa.Column('tv_show_id', sa.Integer(), nullable=True))
    
    # Add media_type column to rating table with a default value
    op.add_column('rating', sa.Column('media_type', sa.String(10), nullable=True))
    
    # Set default value for existing rows
    op.execute("UPDATE rating SET media_type = 'movie' WHERE movie_id IS NOT NULL")
    op.execute("UPDATE rating SET media_type = 'tv' WHERE tv_show_id IS NOT NULL")
    
    # Add NOT NULL constraint to media_type
    op.alter_column('rating', 'media_type', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key(None, 'rating', 'tv_show', ['tv_show_id'], ['id'])

def downgrade():
    op.drop_constraint(None, 'rating', type_='foreignkey')
    op.drop_column('rating', 'media_type')
    op.drop_column('rating', 'tv_show_id')
    op.drop_column('movie', 'streaming_services')
