import code
import os
from typing import List
import json

import lmdb

class CustomTerminal(code.InteractiveConsole):
    """
    CustomTerminal is an interactive console that connects to an LMDB database and allows users to interact with it using custom commands.
    Attributes:
        database (str): The path to the LMDB database.
        intro (str): The introductory message displayed when the console starts.
        env (lmdb.Environment): The LMDB environment object.
        prompt (str): The prompt string displayed in the console.
    Methods:
        interact():
            Starts the interactive console session with a custom banner and exit message.
        runsource(source, filename="<input>", symbol="single"):
            Parses and executes the given source code. Supports custom commands like show, set, get, del, list, export, and import.
        show_database():
            Prints the path to the connected database.
        set_value(key=None, value=None):
            Sets a key-value pair in the database. Prints an error message if the key or value is not provided.
        get_value(key=None):
            Retrieves and prints the value associated with the given key. Prints an error message if the key is not provided.
        del_value(key=None):
            Deletes the key-value pair associated with the given key. Prints an error message if the key is not provided.
        list_values():
            Lists all key-value pairs in the database. Prints "(Empty)" if the database is empty.
        export_values():
            Exports all key-value pairs in the database to a JSON file named "export.json". Prints "(Empty) Data Export!" if the database is empty.
        import_values(key=None, value=None):
            Imports key-value pairs from a JSON file into the database. The key parameter specifies the key to look for in the JSON objects. Prints an error message if the key or file path is not provided, or if the file is not found.
        get_parts(source: str) -> List[str]:
            Static method that splits the source string into parts using whitespace as the delimiter. Returns a list of parts.
    """
    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self.database = self.locals.get("database")
        self.intro = f"connected {self.database}！Use 'exit()' Or 'Ctl+D' to exit."
        self.env = lmdb.open(self.database)
        self.prompt = ">>> "

    def interact(self):
        super().interact(banner=self.intro, exitmsg="Exit Success!")

    def runsource(self, source, filename="<input>", symbol="single"):
        command, *args = self.get_parts(source)
        commands = {
            "show": self.show_database,
            "set": self.set_value,
            "get": self.get_value,
            "del": self.del_value,
            "list": self.list_values,
            "export":self.export_values,
            "import":self.import_values
        }
        
        if command in commands:
            commands[command](*args)
        else:
            print("(Unknown command)")
        return False

    def show_database(self):
        print(f"Database: {self.database}")

    def set_value(self, key=None, value=None):
        if not key or not value:
            print("Use: set <KEY> <VALUE>")
            return
        with self.env.begin(write=True) as txn:
            txn.put(key.encode(), value.encode())
        print("Ok")

    def get_value(self, key=None):
        if not key:
            print("Use: get <KEY>")
            return
        with self.env.begin() as txn:
            value = txn.get(key.encode())
        print(value.decode() if value else "(Empty)")

    def del_value(self, key=None):
        if not key:
            print("Use: del <KEY>")
            return
        with self.env.begin(write=True) as txn:
            txn.delete(key.encode())
        print("ok")

    def list_values(self):
        with self.env.begin() as txn:
            cursor = txn.cursor()
            if not cursor.first():
                print("(Empty)")
                return
            for key, value in cursor:
                print(f"{{{key.decode()}: {value.decode()}}}")
    def export_values(self):
        with self.env.begin() as txn:
            cursor = txn.cursor()
            if not cursor.first():
                print("(Empty) Data Export!")
                return
            data = [{ key.decode() : value.decode() } for key,value in cursor]
            formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
            with open("export.json","w") as f:
                f.write(formatted_json)
            print("Data Exported to export.json")
            return
    def import_values(self,key=None,value=None):
        if not key or not value:
            print("Use: import <ID> <FILE_PATH>")
            return
        if os.path.exists(value) == False:
            print("File Not Found!")
            return

        with self.env.begin(write=True) as txn:
            with open(file=value,mode="r") as f:
                data=f.read()
                dict_data = json.loads(data)
                for item in dict_data:
                    if item.get(key) == None:
                        print(f"Key {key} not found in {item}")
                        return
                    txn.put(str(item.get(key)).encode(),json.dumps(item).encode())
                print("Data Imported!")
                return
    @staticmethod
    def get_parts(source: str) -> List[str]:
        return source.strip().split(maxsplit=2)
