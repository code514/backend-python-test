from alayatodo import connect_db


class DataAccessObject(object):
    # Data access

    @classmethod
    def execute(cls, sql, params=None):
        db = connect_db()
        return db.execute(sql, params)

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
        db = connect_db()
        cursor = cls.execute(sql, params)
        db.commit()
        return cursor

    @classmethod
    def count(cls, **kwargs):
        return cls.one(*cls.by(_columns='count(*)', **kwargs))[0]

    # Query builder

    @classmethod
    def by(cls, _columns='*', **kwargs):
        columns = _columns if isinstance(_columns, list) else [_columns]

        if not kwargs:
            return 'select {} from {}'.format(', '.join(columns), cls.TABLE), []

        clauses = []
        params = []

        for k, v in kwargs.items():
            clauses.append('{} = ?'.format(k))
            params.append(v)

        sql = 'select {} from {} where {}'.format(
            ', '.join(columns),
            cls.TABLE,
            ' and '.join(clauses)
        )
        return sql, params

    @classmethod
    def insert(cls, **kwargs):
        sql = 'insert into {} ({}) values ({})'.format(
            cls.TABLE,
            ', '.join(kwargs.keys()),
            ', '.join(['?'] * len(kwargs.keys())))
        return sql, kwargs.values()


class User(DataAccessObject):
    TABLE = 'users'

    @classmethod
    def authenticate(cls, username, password):
        user = cls.one(*cls.by(username=username, password=password))
        return dict(user) if user else None


class Todo(DataAccessObject):
    TABLE = 'todos'

    @classmethod
    def get(cls, id):
        return cls.one(*cls.by(id=id))

    @classmethod
    def for_user(cls, user_id, limit=None, offset=None):
        sql, params = cls.by(user_id=user_id)

        if limit is not None:
            sql += ' limit {}'.format(limit)
            if offset is not None:
                sql += ' offset {}'.format(offset)

        return cls.many(sql, params)

    @classmethod
    def complete(cls, id, completed=True):
        cls.do('update todos set completed = ? where id = ?', ((1 if completed else 0), id))

    @classmethod
    def delete(cls, id):
        cls.do('delete from todos where id = ?', (id, ))

    @classmethod
    def new(cls, user_id, description):
        clean_description = description.strip()
        if not clean_description:
            raise TodoDescriptionError()

        cursor = cls.do(*cls.insert(user_id=user_id, description=clean_description))
        return cls.get(cursor.lastrowid)


class TodoDescriptionError(RuntimeError):
    pass
