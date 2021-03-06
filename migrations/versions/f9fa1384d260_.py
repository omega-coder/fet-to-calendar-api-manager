"""empty message

Revision ID: f9fa1384d260
Revises: 
Create Date: 2019-08-22 20:56:15.225186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9fa1384d260'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calendars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('calendar_id_google', sa.String(length=100), nullable=True),
    sa.Column('summary', sa.String(length=100), nullable=True),
    sa.Column('std_email', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('summary')
    )
    op.create_index(op.f('ix_calendars_calendar_id_google'), 'calendars', ['calendar_id_google'], unique=True)
    op.create_index(op.f('ix_calendars_std_email'), 'calendars', ['std_email'], unique=True)
    op.create_table('demandes',
    sa.Column('demande_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Boolean(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('req_resource', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('demande_id')
    )
    op.create_index(op.f('ix_demandes_created_at'), 'demandes', ['created_at'], unique=False)
    op.create_index(op.f('ix_demandes_req_resource'), 'demandes', ['req_resource'], unique=False)
    op.create_index(op.f('ix_demandes_state'), 'demandes', ['state'], unique=False)
    op.create_table('import_ops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('import_date', sa.DateTime(), nullable=True),
    sa.Column('filename', sa.String(length=100), nullable=True),
    sa.Column('number_events', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resources',
    sa.Column('resource_id', sa.Integer(), nullable=False),
    sa.Column('resource_name', sa.String(length=60), nullable=True),
    sa.Column('gen_resource_name', sa.String(length=60), nullable=True),
    sa.Column('resource_email', sa.String(length=100), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('building', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('resource_id')
    )
    op.create_index(op.f('ix_resources_building'), 'resources', ['building'], unique=False)
    op.create_index(op.f('ix_resources_gen_resource_name'), 'resources', ['gen_resource_name'], unique=True)
    op.create_index(op.f('ix_resources_resource_email'), 'resources', ['resource_email'], unique=True)
    op.create_index(op.f('ix_resources_resource_name'), 'resources', ['resource_name'], unique=True)
    op.create_table('std_mails',
    sa.Column('mail_id', sa.Integer(), nullable=False),
    sa.Column('std_set', sa.String(length=20), nullable=False),
    sa.Column('std_email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('mail_id')
    )
    op.create_index(op.f('ix_std_mails_std_email'), 'std_mails', ['std_email'], unique=True)
    op.create_index(op.f('ix_std_mails_std_set'), 'std_mails', ['std_set'], unique=True)
    op.create_table('teachers',
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('fullname', sa.String(length=60), nullable=True),
    sa.Column('teacher_email', sa.String(length=100), nullable=True),
    sa.Column('fet_name', sa.String(length=40), nullable=True),
    sa.PrimaryKeyConstraint('teacher_id')
    )
    op.create_index(op.f('ix_teachers_teacher_email'), 'teachers', ['teacher_email'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=True)
    op.create_table('events__log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gevent_id', sa.String(length=100), nullable=True),
    sa.Column('gcalendar_id', sa.String(length=100), nullable=True),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.Column('import_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['import_id'], ['import_ops.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('gevent_id')
    )
    op.create_index(op.f('ix_events__log_gcalendar_id'), 'events__log', ['gcalendar_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_events__log_gcalendar_id'), table_name='events__log')
    op.drop_table('events__log')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_teachers_teacher_email'), table_name='teachers')
    op.drop_table('teachers')
    op.drop_index(op.f('ix_std_mails_std_set'), table_name='std_mails')
    op.drop_index(op.f('ix_std_mails_std_email'), table_name='std_mails')
    op.drop_table('std_mails')
    op.drop_index(op.f('ix_resources_resource_name'), table_name='resources')
    op.drop_index(op.f('ix_resources_resource_email'), table_name='resources')
    op.drop_index(op.f('ix_resources_gen_resource_name'), table_name='resources')
    op.drop_index(op.f('ix_resources_building'), table_name='resources')
    op.drop_table('resources')
    op.drop_table('import_ops')
    op.drop_index(op.f('ix_demandes_state'), table_name='demandes')
    op.drop_index(op.f('ix_demandes_req_resource'), table_name='demandes')
    op.drop_index(op.f('ix_demandes_created_at'), table_name='demandes')
    op.drop_table('demandes')
    op.drop_index(op.f('ix_calendars_std_email'), table_name='calendars')
    op.drop_index(op.f('ix_calendars_calendar_id_google'), table_name='calendars')
    op.drop_table('calendars')
    # ### end Alembic commands ###
