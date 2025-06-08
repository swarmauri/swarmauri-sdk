from peagen.evo_db import EvoDB, Program


def test_insert_and_sample(tmp_path):
    db = EvoDB(speed_bin_ms=5, mem_bin_kb=32, size_bin_ch=10)
    p = Program("print(1)", 0, 4.0, 16)
    db.insert(p)
    assert p.bucket in db.grid
    island = db.sample()
    assert island.champ == p
    ck = tmp_path / "ck.msgpack"
    db.save_checkpoint(ck)
    assert ck.exists()
