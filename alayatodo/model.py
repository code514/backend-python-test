from flask import g


class DataAccessObject(object):
    # Data access

    @classmethod
    def execute(cls, sql, params=None):
        return g.db.execute(sql, params)

    @classmethod
    def one(cls, sql, params=None):
        return cls.execute(sql, params).fetchone()

    @classmethod
    def many(cls, sql, params=None):
        return cls.execute(sql, params).fetchall()

    @classmethod
    def all(cls):
        return cls.many(*cls.by())

    @classmethod
    def do(cls, sql, params=None):
        cls.execute(sql, params)
        g.db.commit()

    # Query builder

    @classmethod
    def by(cls, **kwargs):
        if not kwargs:
            return 'select * from {}'.format(cls.TABLE), []

        clauses = []
        params = []

        for k, v in kwargs.items():
            clauses.append('{} = ?'.format(k))
            params.append(v)

        sql = 'select * from {} where {}'.format(cls.TABLE, ' and '.join(clauses))
        return sql, params
