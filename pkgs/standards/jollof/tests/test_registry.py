from jollof.registry import PluginDomainRegistry


def test_registry_methods():
    PluginDomainRegistry._registry.clear()
    PluginDomainRegistry.add("dom", "grp", "plug", "m:Cls")
    assert PluginDomainRegistry.get("dom", "grp", "plug") == "m:Cls"

    PluginDomainRegistry.update("dom", "grp", "plug", "m:NewCls")
    assert PluginDomainRegistry.get("dom", "grp", "plug") == "m:NewCls"

    assert "dom" in PluginDomainRegistry.known_domains()
    assert "grp" in PluginDomainRegistry.known_groups("dom")

    PluginDomainRegistry.remove("dom", "grp", "plug")
    assert PluginDomainRegistry.get("dom", "grp", "plug") is None

    PluginDomainRegistry.add("dom", "grp", "plug2", "m:C2")
    PluginDomainRegistry.delete_group("dom", "grp")
    assert "grp" not in PluginDomainRegistry.known_groups("dom")

    assert isinstance(PluginDomainRegistry.total_registry(), dict)
