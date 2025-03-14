# LMCMD

## Introduction

`lmcmd` is an interactive console based on Python's `code.InteractiveConsole`, supporting key-value database operations using `LMDB`.

## Installation

You can install it using `pip`:

```bash
pip install lmcmd
```

## Features

- **show**: Display the current database name.
- **set `<KEY>` `<VALUE>`**: Store key-value data.
- **get `<KEY>`**: Retrieve the value of a specified key.
- **del `<KEY>`**: Delete a specified key.
- **list**: List all key-value pairs in the database.
- **export**: Export database data to `export.json`.
- **import `<ID>` `<FILE_PATH>`**: Import data from a JSON file.
- **search `<VALUE>`**: List value in the database key or value.

## Usage

### 1. Start the Terminal

After installation, you can run it directly from the command line:

```bash
lmcmd my_database
```

### 2. Interactive Commands Example

```shell
>>> set name Alice
Ok
>>> get name
Alice
>>> list
{name: Alice}
>>> export
Data Exported to export.json
>>> import id data.json
Data Imported!
>>> show
Database: my_database
>>> del name
Ok
>>> list
(Empty)
>>> search Alice
{name: Alice}
```

## Explanation

### **Data Storage**

All data is stored in the `LMDB` database. A `KEY` must be provided for `set/get/del` operations.

### **Data Export**

Use the `export` command to save database data to `export.json`.

### **Data Import**

`import <ID> <FILE_PATH>`

- `<ID>`: The unique identifier field for the imported data.
- `<FILE_PATH>`: The path to the JSON data file.

If the JSON data is formatted as follows:

```json
[
  { "id": 1, "name": "Alice" },
  { "id": 2, "name": "Bob" }
]
```

Executing `import id data.json` will store the data using `id` as the key.

## Dependencies

- Python 3.8+
- `lmdb`

## License

This project is released under the MIT License.
