import inspect

def child_function(arg):
    # Get the stack frame of the caller
    caller_frame = inspect.currentframe().f_back
    # Get the name of the caller function
    caller_name = caller_frame.f_code.co_name
    # Inspect the arguments of the caller function
    args, _, _, values = inspect.getargvalues(caller_frame)
    # Assuming the caller has only one argument for simplicity
    arg_name = args[0]
    arg_value = values[arg_name]
    print(f"Caller Name: {caller_name}, Argument Name: {arg_name}, Argument Value: {arg_value}")

def caller_function(l):
    child_function(l)

# Example usage
caller_function("Hello")

