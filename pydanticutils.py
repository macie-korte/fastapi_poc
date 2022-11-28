import pydantic
from typing import Optional

# From https://stackoverflow.com/questions/67699451/make-every-fields-as-optional-with-pydantic
class AllOptional(pydantic.main.ModelMetaclass):
    """
    A metaclass which will make all fields optional when used.
    Use it as:

    class PatchableItem(Item, metaclass=AllOptional):
        pass
    """
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)

