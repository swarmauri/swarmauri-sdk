from swarmauri_base import BaseModel, TomlMixin, YamlMixin


class ExamplePlugin(YamlMixin, TomlMixin, BaseModel):
    name: str
    value: int
