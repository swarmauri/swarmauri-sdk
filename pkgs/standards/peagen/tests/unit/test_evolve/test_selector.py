import random

from peagen.evo_db import EvoDB, Program
from peagen.selectors.base import AdaptiveEpsilonSelector


def make_db():
    db = EvoDB()
    p1 = Program("a", 0, 10.0, 32)
    p2 = Program("b", 0, 5.0, 32)
    db.insert(p1)
    db.insert(p2)
    return db, p1, p2


def test_selector_explore(monkeypatch):
    db, p1, p2 = make_db()
    sel = AdaptiveEpsilonSelector(eps_init=1.0)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    assert sel.select(db) == p1


def test_selector_exploit(monkeypatch):
    db, p1, p2 = make_db()
    sel = AdaptiveEpsilonSelector(eps_init=0.0)
    assert sel.select(db) == p2
    sel.feedback(1.0)
    assert sel.eps < 0.1
