"""AlayaNotes

Usage:
  main.py [run] [--host=<ip>] [--port=<port>] [--debug]
  main.py initdb
"""
import subprocess
import sys

from docopt import docopt

from alayatodo import app


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError, ex:
        print ex.output
        sys.exit(1)


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        print "AlayaTodo: Database initialized."
    else:
        host = args['--host'] or '127.0.0.1'
        try:
            port = int(args['--port'])
        except Exception:
            port = 5000
        app.run(host=host, port=port, debug=args['--debug'])
