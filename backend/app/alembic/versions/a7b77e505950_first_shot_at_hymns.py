"""first shot at hymns

Revision ID: a7b77e505950
Revises: 5c124fadc268
Create Date: 2021-03-01 14:17:03.420038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b77e505950'
down_revision = '5c124fadc268'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hymn',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hymn_id'), 'hymn', ['id'], unique=False)
    op.create_index(op.f('ix_hymn_rubrics'), 'hymn', ['rubrics'], unique=False)
    op.create_index(op.f('ix_hymn_title'), 'hymn', ['title'], unique=False)
    op.create_table('hymn_verse',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hymn_verse_id'), 'hymn_verse', ['id'], unique=False)
    op.create_index(op.f('ix_hymn_verse_rubrics'), 'hymn_verse', ['rubrics'], unique=False)
    op.create_index(op.f('ix_hymn_verse_title'), 'hymn_verse', ['title'], unique=False)
    op.create_table('hymnline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('prefix', sa.String(), nullable=True),
    sa.Column('suffix', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hymnline_content'), 'hymnline', ['content'], unique=False)
    op.create_index(op.f('ix_hymnline_id'), 'hymnline', ['id'], unique=False)
    op.create_index(op.f('ix_hymnline_prefix'), 'hymnline', ['prefix'], unique=False)
    op.create_index(op.f('ix_hymnline_rubrics'), 'hymnline', ['rubrics'], unique=False)
    op.create_index(op.f('ix_hymnline_suffix'), 'hymnline', ['suffix'], unique=False)
    op.create_table('hymn_line_association_table',
    sa.Column('hymn_line_id', sa.Integer(), nullable=False),
    sa.Column('hymn_verse_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hymn_line_id'], ['hymnline.id'], ),
    sa.ForeignKeyConstraint(['hymn_verse_id'], ['hymn_verse.id'], ),
    sa.PrimaryKeyConstraint('hymn_line_id', 'hymn_verse_id')
    )
    op.create_table('hymn_verse_association_table',
    sa.Column('hymn_verse_id', sa.Integer(), nullable=False),
    sa.Column('hymn_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hymn_id'], ['hymn.id'], ),
    sa.ForeignKeyConstraint(['hymn_verse_id'], ['hymn_verse.id'], ),
    sa.PrimaryKeyConstraint('hymn_verse_id', 'hymn_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hymn_verse_association_table')
    op.drop_table('hymn_line_association_table')
    op.drop_index(op.f('ix_hymnline_suffix'), table_name='hymnline')
    op.drop_index(op.f('ix_hymnline_rubrics'), table_name='hymnline')
    op.drop_index(op.f('ix_hymnline_prefix'), table_name='hymnline')
    op.drop_index(op.f('ix_hymnline_id'), table_name='hymnline')
    op.drop_index(op.f('ix_hymnline_content'), table_name='hymnline')
    op.drop_table('hymnline')
    op.drop_index(op.f('ix_hymn_verse_title'), table_name='hymn_verse')
    op.drop_index(op.f('ix_hymn_verse_rubrics'), table_name='hymn_verse')
    op.drop_index(op.f('ix_hymn_verse_id'), table_name='hymn_verse')
    op.drop_table('hymn_verse')
    op.drop_index(op.f('ix_hymn_title'), table_name='hymn')
    op.drop_index(op.f('ix_hymn_rubrics'), table_name='hymn')
    op.drop_index(op.f('ix_hymn_id'), table_name='hymn')
    op.drop_table('hymn')
    # ### end Alembic commands ###
