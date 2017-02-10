"""AlayaNotes

Usage:
  main.py [run] [--host=<ip>] [--port=<port>] [--debug]
  main.py initdb
  main.py initmigrate
  main.py migrate
"""
from docopt import docopt

from alayatodo import app, connect_db
import migrations


def _run_sql(filename):
    db = connect_db()
    with open(filename, 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        with app.app_context():
            _run_sql('resources/database.sql')
            _run_sql('resources/fixtures.sql')
        print 'AlayaTodo: Database initialized.'
    elif args['initmigrate']:
        already = False
        with app.app_context():
            try:
                _run_sql('resources/migrations.sql')
            except Exception as e:
                if 'already exists' in e.message:
                    already = True
                else:
                    raise
        print 'AlayaTodo: Migrations {}initialized.'.format('already ' if already else '')
    elif args['migrate']:
        with app.app_context():
            last_version = migrations.run(_run_sql)
        if last_version:
            print 'AlayaTodo: Upgraded to version {}'.format(last_version)
        else:
            print 'AlayaTodo: No migrations to run'
    else:
        host = args['--host'] or '127.0.0.1'
        try:
            port = int(args['--port'])
        except Exception:
            port = 5000
        app.run(host=host, port=port, debug=args['--debug'])
