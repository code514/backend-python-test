"""AlayaNotes

Usage:
  main.py [run] [--host=<ip>] [--port=<port>] [--debug]
  main.py initdb
"""
from docopt import docopt

from alayatodo import app, connect_db


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
    else:
        host = args['--host'] or '127.0.0.1'
        try:
            port = int(args['--port'])
        except Exception:
            port = 5000
        app.run(host=host, port=port, debug=args['--debug'])
