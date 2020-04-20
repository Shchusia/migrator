class DBConformity(object):
    # SQL Numeric Data Types        | from | to |
    BIT_TYPE = 'BIT'  #             | 0 | 1 |
    TINYINT_TYPE = 'TINYINT'  #     | 0 | 255 |
    SMALLINT_TYPE = 'SMALLINT'  #   | -32,768 | 32,768 |
    INT_TYPE = 'INT'  #             | -2,147,483,648 | 2,147,483,648 |
    BIGINT_TYPE = 'BIGINT'  #       | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,808 |
    DECIMAL_TYPE = 'DECIMAL'  #     | -10^38 +1 | 10^38 -1 |
    NUMERIC_TYPE = 'NUMERIC'  #     | -10^38 +1 | 10^38 -1 |
    FLOAT_TYPE = 'FLOAT'  #         | -1.79E + 308 | 1.79E + 308 |
    REAL_TYPE = 'REAL'  #           | -3.40E + 38 | 3.40E + 38 |

    # SQL Date and Time Data Types  | Description
    DATE_TYPE = 'DATE'  # Stores date in the format YYYY-MM-DD
    TIME_TYPE = 'TIME'  # Stores time in the format HH:MI:SS
    DATETIME_TYPE = 'DATETIME'  # Stores date and time information in the format YYYY-MM-DD HH:MI:SS
    TIMESTAMP_TYPE = 'TIMESTAMP'  # Stores number of seconds passed since the Unix epoch (‘1970-01-01 00:00:00’ UTC)
    YEAR_TYPE = 'YEAR'  # Stores year in 2 digit or 4 digit format. Range 1901 to 2155 in 4-digit format. Range 70 to 69, representing 1970 to 2069.

    # SQL Character and String Data Types | Description
    CHAR_TYPE = 'CHAR({})'  # Fixed length with maximum length of 8,000 characters
    VARCHAR_TYPE = 'VARCHAR({})'  # Variable length storage with maximum length of 8,000 characters
    TEXT_TYPE = 'TEXT'  # Variable length storage with maximum size of 2GB data'


class DbUtil(object):
    conformity = DBConformity()
    def _connect(self):
        raise NotImplementedError

    def _disconnect(self):
        raise NotImplementedError

    def __del__(self):
        self._disconnect()

