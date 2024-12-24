import inspect

class IndexErrorWithContext(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
        self.stack_info = inspect.stack()
        self.handle_error()

    def handle_error(self):
        # You might want to log this information or handle it differently depending on your application's needs
        frame = self.stack_info[1]  # Assuming the IndexError occurs one level up from where it's caught
        error_details = {
            "message": str(self.original_exception),
            "function": frame.function,
            "file": frame.filename,
            "line": frame.lineno,
            "code_context": ''.join(frame.code_context).strip() if frame.code_context else "No context available"
        }
        print("IndexError occurred with detailed context:")
        for key, value in error_details.items():
            print(f"{key.capitalize()}: {value}")