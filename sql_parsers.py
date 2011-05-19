from sql_constants import SQL_OPERATOR_TYPES



class UnsupportedSQLExpression (Exception): pass


def SELECT (args):
    # Select all columns
    if args[0][1] == "*" and len(args) == 1:
        return {}
    else:
        raise UnsupportedSQLExpression("Unsupported expression for SELECT")


def FROM (args):
    if len(args) == 1:
        return {"table": args[0][1]}
    else:
        raise UnsupportedSQLExpression("Unsupported expression for FROM")


def WHERE (args):
    # Values for each side of the operation
    # eg. a + b
    a = []
    b = []
    conditions = []
    # TODO: Figure out how to do unary operators
    for token_type, token_value in args:
        if token_type == "operator":
            # See if we need to evaluate a previous operation
            if b:
                # TODO: Make this smarter
                template = SQL_OPERATOR_TRANSLATION[op]["mongodb"]
                conditions.append(template.format(a[0], b[0]))
                a = []
                b = []
            op = SQL_OPERATOR_TYPES[token_value]


        elif token_type == "value":
            if op:
                a.append(token_value)
            else:
                b.append(token_value)
        else:
            raise UnsupportedSQLExpression("Unsupported expression for WHERE")
