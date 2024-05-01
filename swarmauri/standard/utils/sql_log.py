import sqlite3
from datetime import datetime
import asyncio


def sql_log(self, db_path: str, conversation_id, model_name, prompt, response, start_datetime, end_datetime):
    try:
        duration = (end_datetime - start_datetime).total_seconds()
        start_datetime = start_datetime.isoformat()
        end_datetime = end_datetime.isoformat()
        conversation_id = conversation_id
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        conversation_id TEXT, 
                        model_name TEXT, 
                        prompt TEXT, 
                        response TEXT, 
                        start_datetime TEXT, 
                        end_datetime TEXT,
                        duration NUMERIC)''')
        cursor.execute('''INSERT INTO conversations (
                        conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime,
                        duration) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime, 
                        duration))
        conn.commit()
        conn.close()
    except:
        raise



def sql_log_decorator(func):
    async def wrapper(self, *args, **kwargs):
        start_datetime = datetime.now()
        try:
            # Execute the function
            result = await func(self, *args, **kwargs)
        except Exception as e:
            # Handle errors within the decorated function
            self.agent.conversation._history.pop(0)
            print(f"chatbot_function error: {e}")
            return "", [], kwargs['history']  

        end_datetime = datetime.now()
        
        # SQL logging
        # Unpacking the history and other required parameters from kwargs if they were used
        history = kwargs.get('history', [])
        message = kwargs.get('message', '')
        response = result[1]  # Assuming the response is the second item in the returned tuple
        model_name = kwargs.get('model_name', '')
        conversation_id = str(self.agent.conversation.id)
        sql_log(conversation_id, model_name, message, response, start_datetime, end_datetime)
        return result
    return wrapper


class SqlLogMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = sql_log(value)
        return super().__new__(cls, name, bases, dct)