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
        search_values(value=None):
            Searches for values in the database that match the given search criteria.
        get_parts(source: str,maxsplit:int=1) -> List[str]:
            Static method that splits the source string into parts using whitespace as the delimiter. Returns a list of parts.
        
    """

    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self.database = self.locals.get("database")
        self.intro = f"connected {self.database}！Use 'Ctl+D' to exit."
        self.env = lmdb.open(self.database)
        self.prompt = ">>> "
        self.coding='unicode_escape'
        self.commands = {
            "show": (self.show_database,0),
            "set": (self.set_value,2),
            "get": (self.get_value,1),
            "del": (self.del_value,1),
            "list": (self.list_values,0),
            "export":(self.export_values,0),
            "import":(self.import_values,2),
            "search":(self.search_values,1)
        }

    def interact(self):
        super().interact(banner=self.intro, exitmsg="Exit Success!")

    def runsource(self, source, filename="<input>", symbol="single"):
        """
        Execute a command parsed from the given source string.
        This method takes a source string, parses it to extract the command and its arguments,
        and then executes the corresponding function if the command is recognized.
        Parameters:
        source (str): The input string containing the command and its arguments.
        filename (str, optional): The name of the file from which the source was read. Defaults to "<input>".
        symbol (str, optional): The symbol indicating the type of input. Defaults to "single".
        Returns:
        bool: Always returns False.
        Commands:
        - "show": Calls self.show_database() with no arguments.
        - "set": Calls self.set_value() with 2 arguments.
        - "get": Calls self.get_value() with 1 argument.
        - "del": Calls self.del_value() with 1 argument.
        - "list": Calls self.list_values() with no arguments.
        - "export": Calls self.export_values() with no arguments.
        - "import": Calls self.import_values() with 2 arguments.
        - "search": Calls self.search_values() with 1 argument.
        If the command is not recognized, prints "(Unknown command)".
        """
        command,*args = self.get_parts(source)
        if command not in self.commands:
            print("(Unknown command)")
            return False
        fuc,expected_args=self.commands[command]
        command,*args=self.get_parts(source,expected_args)
        fuc(*args)
        return False

    def show_database(self):
        """
        Displays the current database name.

        This method prints the name of the database stored in the `self.database` attribute.
        """
        print(f"Database: {self.database}")

    def set_value(self, key=None, value=None):
        """
        Sets a key-value pair in the environment.

        Args:
            key (str, optional): The key to set. Defaults to None.
            value (str, optional): The value to set. Defaults to None.

        Returns:
            None

        Prints:
            "Use: set <KEY> <VALUE>" if key or value is not provided.
            "Ok" if the key-value pair is successfully set.
        """
        if not key or not value:
            print("Use: set <KEY> <VALUE>")
            return
        with self.env.begin(write=True) as txn:
            txn.put(key.encode(self.coding), value.encode(self.coding))
        print("Ok")

    def get_value(self, key=None):
        """
        Retrieve and print the value associated with the given key from the environment.

        Args:
            key (str, optional): The key for which the value needs to be retrieved. If not provided, 
                                 a usage message will be printed.

        Returns:
            None: This function prints the retrieved value or a message if the key is not found or not provided.
        """
        if not key:
            print("Use: get <KEY>")
            return
        with self.env.begin() as txn:
            value = txn.get(key.encode(self.coding))
        print(value.decode(self.coding) if value else "(Empty)")

    def del_value(self, key=None):
        """
        Deletes a value from the environment database using the provided key.

        Args:
            key (str, optional): The key of the value to be deleted. If no key is provided, 
                                 a usage message will be printed.

        Returns:
            None
        """
        if not key:
            print("Use: del <KEY>")
            return
        with self.env.begin(write=True) as txn:
            txn.delete(key.encode(self.coding))
        print("ok")

    def list_values(self):
        """
        Lists all key-value pairs in the current environment's database.

        This method opens a read-only transaction and iterates through all key-value pairs
        in the database. If the database is empty, it prints "(Empty)". Otherwise, it prints
        each key-value pair in the format {key: value}.

        Returns:
            None
        """
        with self.env.begin() as txn:
            cursor = txn.cursor()
            if not cursor.first():
                print("(Empty)")
                return
            for key, value in cursor:
                print(f"{{{key.decode(self.coding)}: {value.decode(self.coding)}}}")
    def export_values(self):
        """
        Exports the values from the database to a JSON file.

        This method begins a transaction with the database environment and 
        iterates over the key-value pairs using a cursor. If the database is 
        empty, it prints a message indicating that there is no data to export. 
        Otherwise, it decodes the key-value pairs, formats them as a JSON 
        string with indentation, and writes the JSON string to a file named 
        'export.json'. Finally, it prints a message indicating that the data 
        has been exported.

        Raises:
            Exception: If there is an error during the transaction or file 
            writing process.
        """
        with self.env.begin() as txn:
            cursor = txn.cursor()
            if not cursor.first():
                print("(Empty) Data Export!")
                return
            data = [{ key.decode(self.coding) : value.decode(self.coding) } for key,value in cursor]
            formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
            with open("export.json","w") as f:
                f.write(formatted_json)
            print("Data Exported to export.json")
            return
    def import_values(self,key=None,value=None):
        """
        Imports values from a JSON file into the environment.

        Args:
            key (str): The key to look for in each item of the JSON data.
            value (str): The file path to the JSON file to be imported.

        Returns:
            None

        Prints:
            - "Use: import <ID> <FILE_PATH>" if key or value is not provided.
            - "File Not Found!" if the specified file does not exist.
            - "Key {key} not found in {item}" if the key is not found in an item.
            - "Data Imported!" if the data is successfully imported.

        Raises:
            json.JSONDecodeError: If the file content is not valid JSON.
        """
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
    def search_values(self,search=None):
        """
        Searches for values in the database that match the given search criteria.

        Args:
            search (str, optional): The search term to look for in the database. If not provided, a usage message is printed.

        Returns:
            None

        Prints:
            - A usage message if no search term is provided.
            - "(Empty)" if the database is empty or no matching values are found.
            - Matching key-value pairs in the format "{key: value}" if any matches are found.
        """
        if not search:
            print("Use: search <VALUE>")
            return
        with self.env.begin() as txn:
            cursor = txn.cursor()
            if not cursor.first():
                print("(Empty)")
                return
            seach_stats=0
            for key, val in cursor:
                if self.search_check(key,val,search) :
                    print(f"{{{key.decode(self.coding)}: {val.decode(self.coding)}}}")
                    seach_stats+=1
            if seach_stats==0:
                print("(Empty)")
        return
    def search_check(self,key:bytes,val:bytes,search:str):
        """
        Checks if a search string is present in either the key or value.

        Args:
            key (bytes): The key to be searched, in bytes.
            val (bytes): The value to be searched, in bytes.
            search (str): The search string to look for in the key or value.

        Returns:
            bool: True if the search string is found in either the key or value, False otherwise.
        """
        if search in key.decode(self.coding) or search in val.decode(self.coding):
            return True
        return False

    @staticmethod
    def get_parts(source: str,maxsplit:int=1) -> List[str]:
        """
        Splits the input string into a list of substrings.

        Args:
            source (str): The input string to be split.
            maxsplit (int, optional): Maximum number of splits to do. Default is 1.

        Returns:
            List[str]: A list of substrings obtained by splitting the input string.
        """
        return source.strip().split(maxsplit=maxsplit)
    