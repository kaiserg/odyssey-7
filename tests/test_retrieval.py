from app.main import chunks

def test_manuals_loaded():
    assert len(chunks)>=6
    assert any('Oxygen Emergency' in c['section'] for c in chunks)
