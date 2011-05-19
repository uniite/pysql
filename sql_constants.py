"""
Source: http://dev.mysql.com/doc/refman/5.5/en/operator-precedence.html
"""

# A list of all the MySQL operators
SQL_OPERATORS = set([
    "INTERVAL",
    "BINARY", "COLLATE",
    "!",
    "-", "~",
    "^",
    "*", "/", "DIV", "%", "MOD",
    "-", "+",
    "<<", ">>",
    "&",
    "|",
    "=", "<=>", ">=", ">", "<=", "<", "<>", "!=", "IS", "LIKE", "REGEXP", "IN",
    "BETWEEN", "CASE", "WHEN", "THEN", "ELSE",
    "NOT",
    "&&", "AND",
    "XOR",
    "||", "OR",
    "=", ":=",
    "(", ")",
    ".",
    ",", ";"
])


# SQL Operators grouped by meaning
# TODO: Add more
SQL_OPERATOR_TYPES = {
    "AND": "logical_and",
    "&&": "logical_and",
    "OR": "logical_or",
    "||": "logical_or",
    "=": "equality",
    "NOT": "logical_not",
    "!": "logical_not",
    ">=": "greater_than_or_equal",
    ">": "greater_than",
    "<=": "less_than_or_equal",
    "<": "less_than",
    "!=": "not_equal",
}

# All the operators which are symbols rather than words
# (used for regex/scanning)
SQL_ESCAPED_OPERATORS = set([
    "INTERVAL",
    "BINARY", "COLLATE",
    "!=",  # Needs to be up here, or the scanner will match != as !, =
    "\\!",
    "\\-", "~",
    "\\^",
    "\\*", "/", "DIV", "%", "MOD",
    "\\-", "\\+",
    "<<", ">>",
    "&",
    "\\|",
    "=", "<=>", ">=", ">", "<=", "<", "<>", "IS", "LIKE", "REGEXP", "IN",
    "BETWEEN", "CASE", "WHEN", "THEN", "ELSE",
    "NOT",
    "&&", "AND",
    "\\|\\|", "OR",
    "=", ":=",
    "\\(", "\\)",
    "\\.",
    ",", ";"
])

# All the MySQL operators by name,
# and their query/code equivalents, by language.
SQL_OPERATOR_TRANSLATION = {
    "interval": {
        "sql": "INTERVAL {0} {1}",
        "js": None,
        "python": None
    },
    "binary": None,
    "collate": None,
    "logical_not": {
        "sql": "NOT {0}",
        "js": "!{0}",
        "python": "not {0}"
    },
    "unary_minus": {
        "sql": "-{0}",
        "js": "-{0}",
        "python": "-{0}"
    },
    "bitwise_inversion": "~{0}",
    "exponential": {
        "sql": "%s ^ %s",
        "js": "Math.pow({0}, {1})",
        "python": "{0} ** {1}"
    },
    "multiplication": "{0} * {1}",
    "division": "{0} / {1}",
    "modulo": "{0} % {1}",
    "subtraction": "{0} - {1}",
    "addition": "{0} + {1}",
    "bitwise_left_shift": "{0} << {1}",
    "bitwise_right_shift": "{0} >> {1}",
    "bitwise_and": "{0} & {1}",
    "bitwise_or": "{0} | {1}",
    "equality": {
        "sql": "{0} = {1}",
        "mongodb": "{0}: {1}",
        "js": "{0} == {1}",
        "python": "{0} == {1}"
    },
    # TODO: Check null equality in JS
    "null_safe_equality": {
        "sql": "{0} <=> {1}",
        "js": "{0} == {1}",
        "python": "{0} == {1}"
    },
    "greater_than_or_equal": "{0} >= {1}",
    "greater_than": "{0} > {1}",
    "less_than_or_equal": "{0} <= {1}",
    "less_than": "{0} < {1}",
    "not_equal": "{0} != {1}",
    # TODO: Verify thsi for JS
    "is": {
        "sql": "{0} is {1}",
        "js": "{0} == {1}",
        "python": "{0} is {1}"
    },
    "like": {
        "sql": "{0} LIKE {1}",
        "js": None,
        "python": None
    },
    # expression REGEXP pattern
    # TODO: Look into compatbility
    "regular_expression": {
        "sql": "{0} REGEXP {1}",
        "js": None,
        "python": None
    },
    "in": {
        "sql": "{0} IN {1}",
        "js": "{1}.indexOf({0}) != -1",
        "python": "{0} in {1}"
    },
    # TODO: Figure out to do with these code flow operators
    "between": None,
    "case": None,
    "when": None,
    "then": None,
    "else": None,
    "logical_and": {
        "sql": "{0} AND {1}",
        "mongodb": "{0}, {1}",
        "js": "{0} && {1}",
        "python": "{0} and {1}"
    },
    "xor": {
        "sql": "{0} XOR {1}",
        "js": "{0} ? !{1} : {1}",
        "python": "bool({1}) ^ bool({1})"
    },
    # TODO: Figure out how to make the translation optimized
    # eg. {$or: {[a, b, c]}} rather than {$or: [{$or: {[a, b]}}, c]}
    "logical_or": {
        "sql": "{0} OR {1}",
        "mongodb": "$or: [{0}, {1}]",
        "js": "{0} || {1}",
        "python": "{0} or {1}"
    },
    # Note how we use := for SQL, since "="
    # can be mis-interpreted as the equality operator.
    "assignment": {
        "sql": "{0} := {1}",
        "js": "{0} = {1}",
        "python": "{0} = {1}"
    },
    # TODO: These aren't really operators
    "parenthesis": "({0})",
    "parenthesis_open": "(",
    "parenthesis_close": ")",
    "member_accessor": "{0}.{1}",
    "double_quote": "\"{0}\"",
    "single_quote": "'{0}'",
    "identifier_quote": {
        "sql": "`{0}`",
        "js": None,
        "python": None
    },
    "end_statement": ";"
}


# MySQL keywords form:
# http://dev.mysql.com/doc/mysqld-version-reference/en/mysqld-version-reference-reservedwords-5-5.html
# TODO: Add time units, or build them into the INTERVAL sub-parser
keywords = """
ACCESSIBLE
ADD
ALL
ALTER
ANALYZE
AND
AS
ASC
ASENSITIVE
BEFORE
BETWEEN
BIGINT
BINARY
BLOB
BOTH
BY
CALL
CASCADE
CASE
CHANGE
CHAR
CHARACTER
CHECK
COLLATE
COLUMN
CONDITION
CONSTRAINT
CONTINUE
CONVERT
CREATE
CROSS
CURRENT_DATE
CURRENT_TIME
CURRENT_TIMESTAMP
CURRENT_USER
CURSOR
DATABASE
DATABASES
DAY_HOUR
DAY_MICROSECOND
DAY_MINUTE
DAY_SECOND
DEC
DECIMAL
DECLARE
DEFAULT
DELAYED
DELETE
DESC
DESCRIBE
DETERMINISTIC
DISTINCT
DISTINCTROW
DIV
DOUBLE
DROP
DUAL
EACH
ELSE
ELSEIF
ENCLOSED
ESCAPED
EXISTS
EXIT
EXPLAIN
FALSE
FETCH
FLOAT
FLOAT4
FLOAT8
FOR
FORCE
FOREIGN
FROM
FULLTEXT
GENERAL[a]
GRANT
GROUP
HAVING
HIGH_PRIORITY
HOUR_MICROSECOND
HOUR_MINUTE
HOUR_SECOND
IF
IGNORE
IGNORE_SERVER_IDS[b]
IN
INDEX
INFILE
INNER
INOUT
INSENSITIVE
INSERT
INT
INT1
INT2
INT3
INT4
INT8
INTEGER
INTERVAL
INTO
IS
ITERATE
JOIN
KEY
KEYS
KILL
LEADING
LEAVE
LEFT
LIKE
LIMIT
LINEAR
LINES
LOAD
LOCALTIME
LOCALTIMESTAMP
LOCK
LONG
LONGBLOB
LONGTEXT
LOOP
LOW_PRIORITY
MASTER_HEARTBEAT_PERIOD[c]
MASTER_SSL_VERIFY_SERVER_CERT
MATCH
MAXVALUE
MEDIUMBLOB
MEDIUMINT
MEDIUMTEXT
MIDDLEINT
MINUTE_MICROSECOND
MINUTE_SECOND
MOD
MODIFIES
NATURAL
NOT
NO_WRITE_TO_BINLOG
NULL
NUMERIC
ON
OPTIMIZE
OPTION
OPTIONALLY
OR
ORDER
OUT
OUTER
OUTFILE
PRECISION
PRIMARY
PROCEDURE
PURGE
RANGE
READ
READS
READ_WRITE
REAL
REFERENCES
REGEXP
RELEASE
RENAME
REPEAT
REPLACE
REQUIRE
RESIGNAL
RESTRICT
RETURN
REVOKE
RIGHT
RLIKE
SCHEMA
SCHEMAS
SECOND_MICROSECOND
SELECT
SENSITIVE
SEPARATOR
SET
SHOW
SIGNAL
SLOW[d]
SMALLINT
SPATIAL
SPECIFIC
SQL
SQLEXCEPTION
SQLSTATE
SQLWARNING
SQL_BIG_RESULT
SQL_CALC_FOUND_ROWS
SQL_SMALL_RESULT
SSL
STARTING
STRAIGHT_JOIN
TABLE
TERMINATED
THEN
TINYBLOB
TINYINT
TINYTEXT
TO
TRAILING
TRIGGER
TRUE
UNDO
UNION
UNIQUE
UNLOCK
UNSIGNED
UPDATE
USAGE
USE
USING
UTC_DATE
UTC_TIME
UTC_TIMESTAMP
VALUES
VARBINARY
VARCHAR
VARCHARACTER
VARYING
WHEN
WHERE
WHILE
WITH
WRITE
XOR
YEAR_MONTH
ZEROFILL
"""

SQL_KEYWORDS = [x.strip() for x in keywords.splitlines() if x.strip()]
SQL_KEYWORDS_REGEX = "|".join(SQL_KEYWORDS)