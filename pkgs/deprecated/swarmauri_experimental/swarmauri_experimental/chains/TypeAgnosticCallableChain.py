from typing import Any, Callable, List, Dict, Optional, Tuple, Union

CallableDefinition = Tuple[Callable, List[Any], Dict[str, Any], Union[str, Callable, None]]

class TypeAgnosticCallableChain:
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        self.callables = callables if callables is not None else []

    @staticmethod
    def _ignore_previous(_previous_result, *args, **kwargs):
        return args, kwargs

    @staticmethod
    def _use_first_arg(previous_result, *args, **kwargs):
        return [previous_result] + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_first(previous_result, *args, **kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result) + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_only(previous_result, *_args, **_kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result), {}

    @staticmethod
    def _add_previous_kwargs_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**kwargs, **previous_result}

    @staticmethod
    def _add_previous_kwargs_no_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**previous_result, **kwargs}

    @staticmethod
    def _use_all_args_all_kwargs_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {}
        combined_kwargs.update(kwargs)
        return combined_args, combined_kwargs

    @staticmethod
    def _use_all_args_all_kwargs_no_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = kwargs if isinstance(kwargs, dict) else {}
        combined_kwargs = {**combined_kwargs, **(previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {})}
        return combined_args, combined_kwargs

    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, input_handler: Union[str, Callable, None] = None) -> None:
        if isinstance(input_handler, str):
            # Map the string to the corresponding static method
            input_handler_method = getattr(self, f"_{input_handler}", None)
            if input_handler_method is None:
                raise ValueError(f"Unknown input handler name: {input_handler}")
            input_handler = input_handler_method
        elif input_handler is None:
            input_handler = self._ignore_previous
        self.callables.append((func, args or [], kwargs or {}, input_handler))

    def __call__(self, *initial_args, **initial_kwargs) -> Any:
        result = None
        for func, args, kwargs, input_handler in self.callables:
            if isinstance(input_handler, str):
                # Map the string to the corresponding static method
                input_handler_method = getattr(self, f"_{input_handler}", None)
                if input_handler_method is None:
                    raise ValueError(f"Unknown input handler name: {input_handler}")
                input_handler = input_handler_method
            elif input_handler is None:
                input_handler = self._ignore_previous
                
            args, kwargs = input_handler(result, *args, **kwargs) if result is not None else (args, kwargs)
            result = func(*args, **kwargs)
        return result

    def __or__(self, other: "TypeAgnosticCallableChain") -> "TypeAgnosticCallableChain":
        if not isinstance(other, TypeAgnosticCallableChain):
            raise TypeError("Operand must be an instance of TypeAgnosticCallableChain")
        
        new_chain = TypeAgnosticCallableChain(self.callables + other.callables)
        return new_chain