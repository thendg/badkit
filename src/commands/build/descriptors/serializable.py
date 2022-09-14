import yaml


class Serializable(yaml.YAMLObject):
    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        pass

    @classmethod
    def from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Serializable":
        # Set attributes to None if not in file
        values = loader.construct_mapping(node, deep=True)
        attr = cls.get_attrs()
        result = {}
        for val in attr:
            try:
                result[val] = values[val]
            except KeyError:
                result[val] = None
        return cls(**result)
