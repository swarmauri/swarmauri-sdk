import sqlite3
from functools import wraps

def log_prompt_response(db_path):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extracting the 'message' parameter from args which is assumed to be the first argument
            message = args[0]  
            response = await func(*args, **kwargs)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS prompts_responses
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             prompt TEXT, 
                             response TEXT)''')
            
            # Insert a new record
            cursor.execute('''INSERT INTO prompts_responses (prompt, response) 
                            VALUES (?, ?)''', (message, response))
            conn.commit()
            conn.close()
            return response
        
        return wrapper
    return decorator