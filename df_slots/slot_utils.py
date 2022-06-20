from .root import root, freeze_root, flatten_slot_tree


class AutoRegisterMixin:
    def __init__(self, *, name: str, **data) -> None:
        super().__init__(name=name, **data)
        if freeze_root:
            return
        add_nodes, remove_nodes = flatten_slot_tree(self)
        for key in remove_nodes.keys():
            if key in root:
                root.pop(key)
        root.update(add_nodes)
