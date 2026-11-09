import time


def test_addition():
    print("Checking fixture addition...", flush=True)
    time.sleep(0.5)
    assert 1+1==2
    print("Fixture addition passed.", flush=True)
