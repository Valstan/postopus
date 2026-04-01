def test_load_table_returns_default_when_no_mongo(monkeypatch):
    from env_loader import session
    import bin.utils.driver_tables as driver_tables

    # Simulate missing Mongo
    session_backup = dict(session)
    try:
        session['MONGO_BASE'] = None
        # calling load_table should return a default table and not raise
        tbl = driver_tables.load_table('kultura')
        assert isinstance(tbl, dict)
        assert 'lip' in tbl and 'hash' in tbl
    finally:
        session.clear()
        session.update(session_backup)
