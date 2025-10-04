def test_imports():
    import tigrbl_spiffe as mod
    assert hasattr(mod, "TigrblSpiffePlugin")
    assert hasattr(mod, "Svid")
    assert hasattr(mod, "register")
