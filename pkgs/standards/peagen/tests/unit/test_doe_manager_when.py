import yaml
from peagen.doe import DOEManager


def test_patch_when(tmp_path):
    spec_yaml = tmp_path / "spec.yml"
    template_yaml = tmp_path / "template.yaml"

    spec_yaml.write_text(
        yaml.safe_dump(
            {
                "schemaVersion": "1.0.1",
                "FACTORS": {
                    "C3": {
                        "description": "third component",
                        "code": "C3",
                        "levels": ["none", "ConcreteC"],
                        "patches": [
                            {
                                "op": "remove",
                                "path": "/PROJECTS/0/PACKAGES/0/MODULES/2",
                                "value": None,
                                "when": "{{ C3 == 'none' }}",
                            }
                        ],
                    }
                },
            }
        )
    )

    template_yaml.write_text(
        yaml.safe_dump(
            {
                "PROJECTS": [
                    {
                        "NAME": "Base",
                        "PACKAGES": [
                            {
                                "NAME": "pkg",
                                "MODULES": [
                                    {"NAME": "A"},
                                    {"NAME": "B"},
                                    {"NAME": "C"},
                                ],
                            }
                        ],
                    }
                ]
            }
        )
    )

    mgr = DOEManager(str(spec_yaml), str(template_yaml))
    payloads = mgr.generate()
    assert len(payloads) == 2
    assert len(payloads[0]["PACKAGES"][0]["MODULES"]) == 2
    assert len(payloads[1]["PACKAGES"][0]["MODULES"]) == 3
