import datetime
from flask import jsonify

class Buffer:

    def __init__(self):
        self.messages = []

    def add(self, message):
        #Only store 100 (most recent) messages
        if len(self.messages) == 100:
            self.messages.pop(0)
        self.messages.append(message)

    def remove(self, index, username):
        if self.messages[index].username == username:
            self.messages.pop(index)

    def last_message(self):
        return self.messages[-1]
    
    def to_json(self, start, end):
        result = []
        for index in range(start, end, -1):
            result.append(self.messages[index])
        return jsonify(result)

class ManageBuffer:
    @staticmethod
    def add(buffer, message):
        #Only store 100 (most recent) messages
        if len(buffer) == 100:
            buffer.pop(0)
        buffer.append(message)

    @staticmethod
    def remove(buffer, index, username):
        if buffer[index].username == username:
            buffer.pop(index)

    @staticmethod
    def last_message(buffer):
        return buffer[-1]

class Message:

    def __init__(self, username, message):
        self.username = username
        self.message = message
        # self.date_and_time = datetime.datetime.now().__str__()
    
    def get_date(self):
        return self.date_and_time.strftime("%x at %I:%M %p")

    def to_dict(self):
        result = {
            'username': self.username,
            'message': self.message,
            # 'date_and_time': self.date_and_time
        } 
        return result
