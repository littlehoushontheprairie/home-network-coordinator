from dataclasses import fields, is_dataclass
from typing import get_type_hints, get_origin, get_args, Union

class DataclassHelper:
    @staticmethod
    def from_dict(cls, data: dict):
        allowed_fields = {f.name: f for f in fields(cls)}
        hints = get_type_hints(cls)
        kwargs = {}

        for key, value in data.items():

            if key not in allowed_fields:
                continue  # ignore unknown fields

            expected_type = hints[key]
            origin = get_origin(expected_type)  # e.g. list, dict, Union
            args = get_args(expected_type)      # e.g. (str,) for list[str]

            # Unwrap Optional[X] / Union[X, None] → X
            if origin is Union:
                non_none = [a for a in args if a is not type(None)]
                if value is None or not non_none:
                    kwargs[key] = None
                    continue
                expected_type = non_none[0]
                origin = get_origin(expected_type)
                args = get_args(expected_type)

                # Nested dataclass
            if is_dataclass(expected_type) and isinstance(value, dict):
                kwargs[key] = DataclassHelper.from_dict(expected_type, value)

            # list[SomeDataclass]
            elif origin is list and args and is_dataclass(args[0]) and isinstance(value, list):
                kwargs[key] = [DataclassHelper.from_dict(args[0], item) for item in value]

            # dict[str, SomeDataclass]
            elif origin is dict and args and len(args) == 2 and is_dataclass(args[1]) and isinstance(value, dict):
                kwargs[key] = {k: DataclassHelper.from_dict(args[1], v) for k, v in value.items()}

            else:
                kwargs[key] = value  # primitive or unrecognized type, assign as-is

        return cls(**kwargs)