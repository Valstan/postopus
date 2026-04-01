import pytest

from importlib import reload


def test_get_session_loads_regional_work(monkeypatch):
    """Ensure get_session records regional base and loads work tables from it.

    We monkeypatch load_table to simulate returns depending on session['name_base'].
    """
    # import modules
    from env_loader import session
    import bin.rw.get_session as get_session_mod
    import bin.utils.driver_tables as driver_tables

    # Prepare a stub for load_table
    def fake_load_table(name_table):
        # Behavior depends on current session['name_base']
        nb = session.get('name_base')
        # Global config
        if nb == 'config' and name_table == 'config':
            return {
                'zagolovki': {'kultura': True},
                'all_my_groups': {'Малмыж - Инфо': 111}
            }
        # Regional config (collection 'mi')
        if nb == 'mi' and name_table == 'config':
            return {
                'title': 'config',
                'kultura': {'grp1': 2001}
            }
        # Work table for kultura in regional collection
        if nb == 'mi' and name_table == 'kultura':
            return {'lip': ['LIP1'], 'hash': [], 'title': 'kultura'}
        # Default fallback
        return {'lip': [], 'hash': [], 'title': name_table}

    # patch both the driver_tables symbol and the copy imported into get_session module
    monkeypatch.setattr(driver_tables, 'load_table', fake_load_table)
    monkeypatch.setattr(get_session_mod, 'load_table', fake_load_table)

    # Make sure session is fresh
    session.clear()

    # Call get_session for Малмыж - Инфо_kultura
    get_session_mod.get_session('Малмыж - Инфо_kultura')

    # Assert that regional name base was stored
    assert session.get('_regional_name_base') == 'mi'

    # Assert regional theme data was copied
    assert 'kultura' in session and isinstance(session['kultura'], dict)

    # Assert work table for kultura was loaded and contains lip
    assert 'work' in session and 'kultura' in session['work']
    assert session['work']['kultura']['title'] == 'kultura'
    assert session['work']['kultura']['lip'] == ['LIP1']


def test_parser_handles_empty_groups(monkeypatch, caplog):
    """Parser should not crash and should return stats when there are no groups."""
    # import parser and set up minimal session
    from env_loader import session
    import bin.control.parser as parser_mod

    # Replace get_del_msg_blacklist and get_msg with no-op to avoid external deps
    monkeypatch.setattr(parser_mod, 'get_del_msg_blacklist', lambda: None)
    monkeypatch.setattr(parser_mod, 'get_msg', lambda *args, **kwargs: [])

    # Prepare session minimal keys
    session.clear()
    session['name_session'] = 'kultura'
    session['region_name'] = 'Малмыж - Инфо'
    session['zagolovki'] = {'kultura': True}
    session['kultura'] = {}  # empty groups
    session['post_group_vk'] = None
    session['work'] = {'kultura': {'lip': [], 'hash': []}}
    session['heshteg'] = {'reklama': '#rekl'}
    session['delete_msg_blacklist'] = []
    session['filter_region'] = 'kirov'
    session['filter_group_by_region_words'] = {}
    session['bad_name_group'] = {}
    session['zagolovok'] = {'kultura': '[Культура]'}

    # Run parser in stat_mode
    res = parser_mod.parser(stat_mode=True)

    # Should be a dict with posts and stats
    assert isinstance(res, dict)
    stats = res.get('stats', {})
    assert stats.get('posts_count', 0) == 0
    # The logger warning should be present
    import logging
    found = any("no groups found for theme 'kultura'" in rec.getMessage() for rec in caplog.records)
    assert found, f"Expected warning not found in logs: {[r.getMessage() for r in caplog.records]}"