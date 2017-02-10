import os
import re

from alayatodo.model import DataAccessObject


MIGRATIONS_DIR = 'resources/migrations'


def run(run_sql):
    if not Migration.is_installed():
        print 'Migrations table not installed!'
        return

    try:
        files = os.listdir(MIGRATIONS_DIR)
    except OSError:
        return

    migration_re = re.compile('(\d{3})_(.+)\.sql', re.IGNORECASE)

    existing = {id: name for id, name in Migration.all()}
    to_run = {}
    for filename in files:
        migration_data = migration_re.match(filename)
        if not migration_data:
            continue

        id = int(migration_data.group(1))
        name = migration_data.group(2)

        if id in to_run:
            print 'Migration {}: "{}" already set to run as "{}"'.format(id, name, to_run[id][0])
            continue

        if id in existing:
            if name != existing[id]:
                print 'Migration {}: "{}" already applied as "{}"'.format(id, name, existing[id])
            continue

        to_run[id] = (name, filename)

    max_id = None
    for id in sorted(to_run.keys()):
        name, filename = to_run[id]
        print 'Running migration {}: "{}"'.format(id, name)
        try:
            run_sql(os.path.join(MIGRATIONS_DIR, filename))
            max_id = id
        except Exception as e:
            print 'Failed to run migration {}: {}'.format(id, e.message)
        else:
            Migration.new(id, name)

    return max_id


class Migration(DataAccessObject):
    TABLE = 'migrations'

    @classmethod
    def is_installed(cls):
        try:
            cls.all()
        except Exception:
            return False
        return True

    @classmethod
    def last(cls):
        return cls.one()

    @classmethod
    def new(cls, id, name):
        cls.do(*cls.insert(id=id, name=name))
