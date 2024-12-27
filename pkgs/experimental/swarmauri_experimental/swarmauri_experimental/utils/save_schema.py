import inspect
import random

class Storage:
    def __init__(self):
        self.logs = []

    def log(self, log_data):
        self.logs.append(log_data)

    def print_logs(self):
        for log in self.logs:
            print(log)

class Loggable:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage

    def log_call(self, *args, **kwargs):
        # Inspect the call stack to get the caller's details
        caller_frame = inspect.stack()[2]
        caller_name = inspect.currentframe().f_back.f_code.co_name
        #caller_name = caller_frame.function
        module = inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if module else 'N/A'

        # Log all relevant details
        log_data = {
            'caller_name': caller_name,
            'module_name': module_name,
            'called_name': self.name,
            'called_function': caller_frame[3], # The function in which log_call was invoked
            'args': args,
            'kwargs': kwargs
        }
        self.storage.log(log_data)

class Caller(Loggable):
    def __init__(self, name, storage, others):
        super().__init__(name, storage)
        self.others = others

    def __call__(self, *args, **kwargs):
        if len(self.storage.logs)<10:
            self.log_call(*args, **kwargs)
            # Randomly call another without causing recursive calls
            if args:  # Ensures it's not the first call without actual target
                next_caller_name = random.choice([name for name in self.others if name != self.name])
                self.others[next_caller_name](self.name)

# Initialize storage and callers
storage = Storage()
others = {}

# Creating callers
alice = Caller('Alice', storage, others)
bob = Caller('Bob', storage, others)
charlie = Caller('Charlie', storage, others)
dan = Caller('Dan', storage, others)

others['Alice'] = alice
others['Bob'] = bob
others['Charlie'] = charlie
others['Dan'] = dan

# Simulate the calls
dan(1, taco=23)

# Print the logs
storage.print_logs()
