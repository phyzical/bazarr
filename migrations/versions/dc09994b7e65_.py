"""empty message

Revision ID: dc09994b7e65
Revises: 
Create Date: 2023-04-12 14:50:25.281288

"""
from alembic import op
import sqlalchemy as sa

try:
    from psycopg2.errors import UndefinedObject
except ImportError:
    pass

from bazarr.app.database import TableHistory, TableHistoryMovie, TableBlacklist, TableBlacklistMovie, TableEpisodes, \
    TableShows, TableMovies, TableLanguagesProfiles

# revision identifiers, used by Alembic.
revision = 'dc09994b7e65'
down_revision = None
branch_labels = None
depends_on = None

bind = op.get_context().bind
insp = sa.inspect(bind)


def column_exists(table_name, column_name):
    columns = insp.get_columns(table_name)
    return any(c["name"] == column_name for c in columns)


def column_type(table_name, column_name):
    _type = [x['type'].python_type for x in insp.get_columns(table_name) if x['name'] == column_name]
    return _type[0] if _type else None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # Update announcements table
    with op.batch_alter_table('table_announcements', recreate='always') as batch_op:
        batch_op.execute('DROP INDEX IF EXISTS tableannouncements_hash')
        if not column_exists('table_announcements', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))

    # Update system table
    with op.batch_alter_table('system', recreate='always') as batch_op:
        if not column_exists('system', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))

    # Update custom_score_profile_conditions table
    with op.batch_alter_table('table_custom_score_profile_conditions') as batch_op:
        batch_op.execute('DROP INDEX IF EXISTS tablecustomscoreprofileconditions_profile_id')
        batch_op.alter_column('profile_id', index=False)
        batch_op.execute('DROP INDEX IF EXISTS ix_table_custom_score_profile_conditions_profile_id;')

    # Update notifier table
    with op.batch_alter_table('table_settings_notifier') as batch_op:
        batch_op.alter_column('name', existing_type=sa.TEXT(), nullable=False)

    # Update series table
    with op.batch_alter_table('table_shows') as batch_op:
        if bind.engine.name == 'postgresql':
            batch_op.execute('ALTER TABLE table_shows DROP CONSTRAINT IF EXISTS table_shows_pkey;')
        batch_op.execute(sa.update(TableShows)
                         .values({TableShows.profileId: None})
                         .where(TableShows.profileId.not_in(sa.select(TableLanguagesProfiles.profileId))))
        batch_op.create_primary_key(constraint_name='pk_table_shows', columns=['sonarrSeriesId'])
        batch_op.create_foreign_key(constraint_name='fk_series_profileId_languages_profiles',
                                    referent_table='table_languages_profiles',
                                    local_cols=['profileId'],
                                    remote_cols=['profileId'],
                                    ondelete='SET NULL')
        batch_op.alter_column(column_name='imdbId', server_default=None)
        batch_op.alter_column(column_name='tvdbId', existing_type=sa.INTEGER(), nullable=True)
        if column_exists('table_shows', 'alternateTitles'):
            batch_op.alter_column(column_name='alternateTitles', new_column_name='alternativeTitles')
        batch_op.execute('DROP INDEX IF EXISTS tableshows_path')
        batch_op.execute('DROP INDEX IF EXISTS tableshows_profileId')
        batch_op.execute('DROP INDEX IF EXISTS tableshows_sonarrSeriesId')
        batch_op.create_unique_constraint(constraint_name='unique_table_shows_path', columns=['path'])

    # Update episodes table
    with op.batch_alter_table('table_episodes') as batch_op:
        if bind.engine.name == 'postgresql':
            batch_op.execute('ALTER TABLE table_episodes DROP CONSTRAINT IF EXISTS table_episodes_pkey;')
        batch_op.execute(sa.delete(TableEpisodes).where(TableEpisodes.sonarrSeriesId.not_in(
            sa.select(TableShows.sonarrSeriesId))))
        batch_op.create_primary_key(constraint_name='pk_table_episodes', columns=['sonarrEpisodeId'])
        batch_op.create_foreign_key(constraint_name='fk_sonarrSeriesId_episodes',
                                    referent_table='table_shows',
                                    local_cols=['sonarrSeriesId'],
                                    remote_cols=['sonarrSeriesId'],
                                    ondelete='CASCADE')
        batch_op.alter_column(column_name='file_size', server_default='0')
        if column_exists('table_episodes', 'scene_name'):
            batch_op.alter_column(column_name='scene_name', new_column_name='sceneName')
        batch_op.alter_column(column_name='sonarrSeriesId', existing_type=sa.INTEGER(), nullable=True)
        batch_op.execute('DROP INDEX IF EXISTS tableepisodes_sonarrEpisodeId')

    # Update series history table
    table_history_timestamp_altered = False
    with op.batch_alter_table('table_history', recreate='always') as batch_op:
        batch_op.execute(sa.delete(TableHistory).where(TableHistory.sonarrEpisodeId.not_in(
            sa.select(TableEpisodes.sonarrEpisodeId))))
        batch_op.execute(sa.delete(TableHistory).where(TableHistory.sonarrSeriesId.not_in(
            sa.select(TableShows.sonarrSeriesId))))
        batch_op.alter_column(column_name='sonarrEpisodeId', existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column(column_name='sonarrSeriesId', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_foreign_key(constraint_name='fk_sonarrEpisodeId_history',
                                    referent_table='table_episodes',
                                    local_cols=['sonarrEpisodeId'],
                                    remote_cols=['sonarrEpisodeId'],
                                    ondelete='CASCADE')
        batch_op.create_foreign_key(constraint_name='fk_sonarrSeriesId_history',
                                    referent_table='table_shows',
                                    local_cols=['sonarrSeriesId'],
                                    remote_cols=['sonarrSeriesId'],
                                    ondelete='CASCADE')
        if not column_exists('table_history', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))
        if column_type('table_history', 'score') == str:
            batch_op.alter_column(column_name='score', existing_type=sa.Text, type_=sa.Integer)
        if column_type('table_history', 'timestamp') == int:
            table_history_timestamp_altered = True
            batch_op.alter_column(column_name='timestamp', existing_type=sa.Integer, type_=sa.DateTime)
    with op.batch_alter_table('table_history') as batch_op:
        # must be run after alter_column as been committed
        if table_history_timestamp_altered:
            batch_op.execute(sa.text("UPDATE table_history SET timestamp = datetime(timestamp, 'unixepoch')"))

    # Update series blacklist table
    table_blacklist_timestamp_altered = False
    with op.batch_alter_table('table_blacklist', recreate="always") as batch_op:
        batch_op.execute(sa.delete(TableBlacklist).where(TableBlacklist.sonarr_episode_id.not_in(
            sa.select(TableEpisodes.sonarrEpisodeId))))
        batch_op.execute(sa.delete(TableBlacklist).where(TableBlacklist.sonarr_series_id.not_in(
            sa.select(TableShows.sonarrSeriesId))))
        batch_op.create_foreign_key(constraint_name='fk_sonarrEpisodeId_blacklist',
                                    referent_table='table_episodes',
                                    local_cols=['sonarr_episode_id'],
                                    remote_cols=['sonarrEpisodeId'],
                                    ondelete='CASCADE')
        batch_op.create_foreign_key(constraint_name='fk_sonarrSeriesId_blacklist',
                                    referent_table='table_shows',
                                    local_cols=['sonarr_series_id'],
                                    remote_cols=['sonarrSeriesId'],
                                    ondelete='CASCADE')
        if not column_exists('table_blacklist', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))
        if column_type('table_blacklist', 'timestamp') == int:
            table_blacklist_timestamp_altered = True
            batch_op.alter_column(column_name='timestamp', existing_type=sa.Integer, type_=sa.DateTime, nullable=True)
        else:
            batch_op.alter_column('timestamp', existing_type=sa.DATETIME(), nullable=True)
    with op.batch_alter_table('table_blacklist') as batch_op:
        # must be run after alter_column as been committed
        if table_blacklist_timestamp_altered:
            batch_op.execute(sa.text("UPDATE table_blacklist SET timestamp = datetime(timestamp, 'unixepoch')"))

    # Update series rootfolder table
    with op.batch_alter_table('table_shows_rootfolder') as batch_op:
        if bind.engine.name == 'postgresql':
            batch_op.execute('ALTER TABLE table_shows_rootfolder DROP CONSTRAINT IF EXISTS table_shows_rootfolder_pkey;')
        batch_op.alter_column(column_name='id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.create_primary_key(constraint_name='pk_table_shows_rootfolder', columns=['id'])

    # Update movies table
    with op.batch_alter_table('table_movies') as batch_op:
        if bind.engine.name == 'postgresql':
            batch_op.execute('ALTER TABLE table_movies DROP CONSTRAINT IF EXISTS table_movies_pkey;')
        batch_op.execute(sa.update(TableMovies)
                         .values({TableMovies.profileId: None})
                         .where(TableMovies.profileId.not_in(sa.select(TableLanguagesProfiles.profileId))))
        batch_op.create_primary_key(constraint_name='pk_table_movies', columns=['radarrId'])
        batch_op.create_foreign_key(constraint_name='fk_movies_profileId_languages_profiles',
                                    referent_table='table_languages_profiles',
                                    local_cols=['profileId'],
                                    remote_cols=['profileId'],
                                    ondelete='SET NULL')
        batch_op.alter_column(column_name='file_size', server_default='0')
        batch_op.execute('DROP INDEX IF EXISTS tablemovies_path')
        batch_op.execute('DROP INDEX IF EXISTS tablemovies_profileId')
        batch_op.execute('DROP INDEX IF EXISTS tablemovies_radarrId')
        batch_op.execute('DROP INDEX IF EXISTS tablemovies_tmdbId')
        batch_op.create_unique_constraint(constraint_name='unique_table_movies_path', columns=['path'])
        batch_op.create_unique_constraint(constraint_name='unique_table_movies_tmdbId', columns=['tmdbId'])

    # Update movies history table
    table_history_movie_timestamp_altered = False
    with op.batch_alter_table('table_history_movie', recreate='always') as batch_op:
        batch_op.execute(sa.delete(TableHistoryMovie).where(TableHistoryMovie.radarrId.not_in(
            sa.select(TableMovies.radarrId))))
        batch_op.alter_column(column_name='radarrId', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_foreign_key(constraint_name='fk_radarrId_history_movie',
                                    referent_table='table_movies',
                                    local_cols=['radarrId'],
                                    remote_cols=['radarrId'],
                                    ondelete='CASCADE')
        if not column_exists('table_history_movie', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))
        if column_type('table_history_movie', 'score') == str:
            batch_op.alter_column(column_name='score', existing_type=sa.Text, type_=sa.Integer)
        if column_type('table_history_movie', 'timestamp') == int:
            table_history_movie_timestamp_altered = True
            batch_op.alter_column(column_name='timestamp', existing_type=sa.Integer, type_=sa.DateTime)
    with op.batch_alter_table('table_history_movie') as batch_op:
        # must be run after alter_column as been committed
        if table_history_movie_timestamp_altered:
            batch_op.execute(sa.text("UPDATE table_history_movie SET timestamp = datetime(timestamp, 'unixepoch')"))

    # Update movies blacklist table
    table_blacklist_movie_timestamp_altered = False
    with op.batch_alter_table('table_blacklist_movie', recreate='always') as batch_op:
        batch_op.execute(sa.delete(TableBlacklistMovie).where(TableBlacklistMovie.radarr_id.not_in(
            sa.select(TableMovies.radarrId))))
        batch_op.create_foreign_key(constraint_name='fk_radarrId_blacklist_movie',
                                    referent_table='table_movies',
                                    local_cols=['radarr_id'],
                                    remote_cols=['radarrId'],
                                    ondelete='CASCADE')
        if not column_exists('table_blacklist_movie', 'id'):
            batch_op.add_column(sa.Column('id', sa.Integer, primary_key=True))
        if column_type('table_blacklist_movie', 'timestamp') == int:
            table_blacklist_movie_timestamp_altered = True
            batch_op.alter_column(column_name='timestamp', existing_type=sa.Integer, type_=sa.DateTime, nullable=True)
        else:
            batch_op.alter_column('timestamp', existing_type=sa.DATETIME(), nullable=True)
    with op.batch_alter_table('table_blacklist_movie') as batch_op:
        # must be run after alter_column as been committed
        if table_blacklist_movie_timestamp_altered:
            batch_op.execute(sa.text("UPDATE table_blacklist_movie SET timestamp = datetime(timestamp, 'unixepoch')"))

    # Update movies rootfolder table
    with op.batch_alter_table('table_movies_rootfolder') as batch_op:
        if bind.engine.name == 'postgresql':
            batch_op.execute('ALTER TABLE table_movies_rootfolder DROP CONSTRAINT IF EXISTS table_movies_rootfolder_pkey;')
        batch_op.alter_column(column_name='id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.create_primary_key(constraint_name='pk_table_movies_rootfolder', columns=['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
