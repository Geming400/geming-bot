from typing import Any


class QueriesHelper:
    @staticmethod
    def insert_json(column: str, value: Any, addStrQuotes: bool = True):
        """Returns a `insert_json` like query.
        Note: the `UPDATE` and `WHERE` statements needs to be manually added
        
        Args:
            column: The column
            value: The value, note: if it's a string, `''` will get added automatically
            addStrQuotes: Adds the sql string quote (`''`) if `value` is of type `str`
        """
        
        _value = f"'{value}'" if addStrQuotes and isinstance(value, str) else addStrQuotes
        
        return f"""
SET {column} = json_insert(
    {column},
    '$[#]', {_value}
)
"""