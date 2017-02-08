"""AlayaNotes

Usage:
  main.py [run]
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
        app.run(use_reloader=True)
