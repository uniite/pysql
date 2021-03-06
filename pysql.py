"""
PySQL

An abstraction layer for databases, accessible via a MySQL connection.
"""
__author__ = "Jon Botelho"


import SocketServer
import struct
import os
from types import StringType
import pymongo
import re



class MySQLPacket (object):

    def __init__ (self, data=None, length=0, number=0):
        """ For creating outgoing packets. """

        # Auto-fill the length if data is provided
        if data:
            self.data = data
            self.length = len(data)
        else:
            self.length = length
        self.number = number

    
    @classmethod
    def fromSocket (cls, sock, get_data=False):
        """ For reading incoming packets. """
        
        # Make a new instance of this class
        packet = cls()
        # Get the packet length (3 bytes), and the packet number (1 byte)
        packet.length, length_byte3, packet.packet_number \
            = struct.unpack("< HB B", sock.recv(4))
        packet.length += length_byte3 << 16
        if get_data:
            # Read the packet's data, now that we have the length
            packet.data = sock.recv(packet.length)

        # We're done; return the complete packet
        return packet


    def __str__ (self):
        """ Encode the packet for sending. """
        
        self.length = len(self.data)
        return struct.pack(
            "< H B B",
            self.length & 0xFFFF,
            self.length >> 16,
            self.number
        ) + self.data



class GreetingPacket (MySQLPacket):
    """
    Sent to the client as soon as they connect.
    
    Also known as the Handshake Initialization Packet.
    """

    def __init__ (self, protocol_version=10, server_version="5.1.53 - log",
                  thread_id=11578506, salt=None, server_capabilities=0xF7FF,
                  charset=8, server_status=0x0002):
        """
        Make a new greeting packet.

        The defaults are:
            protocol_version/server_version: MySQL 5.1
            salt: Auto-generated, 20 bits
            sever_capabilities: Everything supported except SSL
            charset: latin1 COLLATE latin1_swedish_ci (8)
        """

        # Generate a random salt if a valid one was not given
        try:
            salt = str(salt)
            assert(len(salt) == 20)
        except:
            salt = os.urandom(20)
            assert(len(salt) == 20)
        self.salt = salt

        # Fill in all the other values
        self.number = 0
        self.protocol_version = protocol_version
        self.server_version = server_version
        self.thread_id = thread_id
        self.server_capabilities = server_capabilities
        self.charset = charset
        self.server_status = server_status
    

    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        self.data = struct.pack(
            "< B %ssB I 8sB H B H 13s 8sB" % len(self.server_version),
            self.protocol_version,
            self.server_version, 0,
            self.thread_id,
            self.salt[:8], 0,
            self.server_capabilities,
            self.charset,
            self.server_status,
            "\0" * 13,
            self.salt[8:20], 0
        )
        # Return the encoded packet
        return super(GreetingPacket, self).__str__()


class LoginRequestPacket (MySQLPacket):
    """
    Sent by the client for authentication.

    Tends to be the first packet sent by the client,
    right after the Greeting Packet.
    """

    @classmethod
    def fromSocket (cls, sock):
        """ For reading incoming packets. """

        # Get some basic information from our parent class,
        # and use the resulting object here-on
        packet = super(LoginRequestPacket, cls).fromSocket(sock)
        # Decode the first part of the packet
        packet.client_capabilities, packet.extended_client_capabilities,\
        packet.max_packet_size, packet.charset \
            = struct.unpack("< H H I B", sock.recv(9))
        # The second part is tricky because it contains null-terminated strings
        rest = sock.recv(packet.length - 9)
        # Get the null-terminated username string
        packet.username, rest = rest.split("\0", 1)[0]
        # The password is an SHA-1 hash (20-bytes/160-bits)
        packet.password = rest[:20]
        # The last thing is the schema name (null-terminated)
        packet.schema = rest[20:-1]

        # We're done; return the filled-in packet object
        return packet



class OKPacket (MySQLPacket):
    """
    Sent as a response to packets sent from the client.
    """

    def __init__ (self, number=1, field_count=0, affected_rows=0,
                  insert_id=0, server_status=0, warnings=0):
        # TODO: Change numeric fields to use length coded binary
        self.number = number
        self.field_count = field_count
        self.affected_rows = affected_rows
        self.insert_id = insert_id
        self.server_status = server_status
        self.warnings = warnings
       

    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        self.data = struct.pack(
            "< B B B H H",
            self.field_count,
            self.affected_rows,
            self.insert_id,
            self.server_status,
            self.warnings
        )
        # Return the encoded packet
        return super(OKPacket, self).__str__()




class CommandPacket(MySQLPacket):
    """
    A packet containing a command from the client.
    """

    commands = {
        1: "Quit",
        3: "Query"
    }

    @classmethod
    def fromSocket (cls, sock):
        """ For reading incoming packets. """
        
        # Get some basic information from our parent class,
        # and use the resulting object here-on
        packet = super(CommandPacket, cls).fromSocket(sock)
        # Decode the command type
        packet.command = struct.unpack("< B", sock.recv(1))[0]
        # Fill in a command description (for convenience)
        if packet.command in cls.commands:
            packet.description = cls.commands[packet.command]
        else:
            packet.description = "Unknown"
        # Decode the actual command/statement
        # (Usually SQL)
        packet.statement = sock.recv(packet.length - 1)

        # We're done; return the completed command object
        return packet





class ResultSetHeaderPacket(MySQLPacket):
    """
    Describes a result set.
    """

    def __init__ (self, number=1, field_count=0):
        # TODO: Change field count to use coded binary
        self.number = number
        self.field_count = field_count


    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        self.data = struct.pack(
            "B",
            self.field_count
        )
        # Return the encoded packet
        return super(ResultSetHeaderPacket, self).__str__()





class FieldPacket(MySQLPacket):
    """
    Describes a field/column in a result set.
    """

    def __init__ (self, number=1, catalog="def", database="",
                  table="", original_table="",
                  name="", original_name="",
                  charset=8, length=255, type=254,  # Type 254 is String/VARCHAR
                  flags=0, decimals=0, default=0):
        # TODO: Change numeric values to use length coded binary
        # TODO: Change the text values to be length coded strings
        self.number = number
        self.catalog = catalog
        self.database = database
        self.table = table
        self.original_table = original_table or self.table
        self.name = name
        self.original_name = original_name or self.name
        self.charset = charset
        self.length = length
        self.type = type
        self.flags = flags
        self.decimals = decimals
        self.default = default


    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        # First do the strings
        # TODO: Do real length coding on these
        string_fields = ("catalog", "database", "table", "original_table",
                         "name", "original_name")
        self.data = ""
        for name in string_fields:
            s = getattr(self, name)
            self.data += struct.pack("B", len(s))
            # Make sure there's no unicode
            self.data += str(s)
        # Then do the numeric packet fields
        self.data += struct.pack(
            "< B H I B H B H B B",
            0,
            self.charset,
            self.length,
            self.type,
            self.flags,
            self.decimals,
            0,
            self.default,
            0
        )
        # Return the encoded packet
        return super(FieldPacket, self).__str__()




class EOFPacket(MySQLPacket):
    """
    Signals the end of a series of field packets.
    """

    def __init__ (self, number=1, warnings=0, server_status=0):
        self.number = number
        self.warnings = warnings
        self.server_status = server_status


    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        self.data = struct.pack(
            "< B H H",
            0xFE,
            self.warnings,
            self.server_status
        )
        # Return the encoded packet
        return super(EOFPacket, self).__str__()


class RowDataPacket(MySQLPacket):
    """
    Signals the end of a series of field packets.
    """

    def __init__ (self, number=1, values=[]):
        self.number = number
        self.values = values


    def __str__ (self):
        """ Encode the packet for sending. """

        # Encode the packet's payload
        # TODO: Do length encoded strings for real
        # TODO: Figure out how to encode numbers, NULLs, etc.
        self.data = ""
        for value in self.values:
            self.data += struct.pack("B", len(value))
            self.data += value
        # Return the encoded packet
        return super(RowDataPacket, self).__str__()


class ResultSet(object):
    """ Used to send a set of results back to the client. """

    def __init__ (self, columns=[], rows=[], table="", database=""):
        self.columns = columns
        self.rows = rows
        self.table = table
        self.database = database

    def toPackets (self):
        """
        Gets a list of MySQL packets used to send this
        result set to the client.
        """

        # First make a header packet
        i = 1
        field_count = len(self.columns)
        packets = [ResultSetHeaderPacket(i, field_count)]

        # Then the field packets for each column
        for col in self.columns:
            i += 1
            packets += [
                FieldPacket(
                    i,
                    database=self.database,
                    table=self.table,
                    name=col
                )
            ]

        # Then an EOF
        i += 1
        packets += [EOFPacket(i)]

        # Then the row data
        for row in self.rows:
            i += 1
            packets += [RowDataPacket(i, row)]

        # Then another EOF to finish it off
        i += 1
        packets += [EOFPacket(i)]
        
        return packets


    def __str__ (self):
        return "".join([str(p) for p in self.toPackets()])



class Query(object):
    pass

        





SQL_IDENTIFIER_REGEX = "(?:`[^`]+`|[$\w]+)"
# TODO: Add support for quote escapes
# TODO: Add support for floats and hex numbers
SQL_VALUE_REGEX = "(?:[0-9]+|'[^']+'|\"[^\"]+\")"
SQL_CONDITION_REGEX = ""
SQL_REGEX_DICT = {
    "ident": SQL_IDENTIFIER_REGEX,
    "value": SQL_VALUE_REGEX
}


from sql_constants import *
SQL_OPERATORS_REGEX = "|".join(SQL_ESCAPED_OPERATORS)

class SQLStatement(object):
    def __init__ (self, statement):
        self.statement = statement

    def scan (self):
        """
        Scans through the SQL statement, and splits it up
        into tokens like "FROM", "=", "(", etc.
        """

        def parse_op (scanner, token): return "operator", token
        def parse_ident (scanner, token): return "identifier", token
        def parse_value (scanner, token): return "value", token
        def parse_kw (scanner, token): return "keyword", token

        scanner = re.Scanner([
            (SQL_OPERATORS_REGEX, parse_op),
            (SQL_KEYWORDS_REGEX, parse_kw),
            (SQL_VALUE_REGEX, parse_value),
            (SQL_IDENTIFIER_REGEX, parse_ident),
            ("\s*", None)
        ])

        return scanner.scan(self.statement)


class SelectQuery(Query):
    """ Respresents an SQL SELECT query. """

    statement_regex = re.compile((
        "^\s*SELECT\s+" +
            "\*\s+" +
        "(FROM)\s+" +
            "(?P<table>{ident})" +
        "(?:\s+(WHERE)" +
            "\s+({ident})\s*(=)\s*({value})" +
        ")?\s*;?\s*"
    ).format(**SQL_REGEX_DICT), re.I | re.S | re.M)
    
    def __init__ (self, statement):
        # Make sure we have a SELECT query
        if not statement.lower().startswith("select"):
            raise ValueError("The given statement a SELECT query.")
        self.statement = statement

    def execute (self):
        # Figure out what the query actually means
        tokens = SQLStatement(self.statement).scan()
        if tokens[1]:
            print "Could not parse statement. Error around: %s" % tokens[1]
            return
        tokens = tokens[0]
        print "Tokens: %s" % (tokens,)
        keyword = ""
        arguments = []
        parsed = []
        i = 0
        for token_type, token_value in tokens:
            # TODO: Rework this to loop through without the i += 1 nonsense
            # Should scan through, keep adding on to keyword args array
            # until another keyword is encountered. Then, parse the args.
            # Check if we have a keyword
            if token_value.upper() in SQL_KEYWORDS or token_value == ";":
                # The there was a previous keyword,
                # We need to parse its arguments now before moving on.
                if keyword:
                    if hasattr(sql_parsers, keyword):
                        result = getattr(sql_parsers, keyword)(arguments)
                        parsed.append((keyword, result))
                    else:
                        raise Exception("No parser found for %s" % keyword)
            else:
                arguments += (token_type, token_value)
                keyword = token_value.upper()

        # TODO: Get a table back out here
        # TODO: Get the conditions
        return table, conditions





class MySQLServerSession(object):
    def __init__ (self, sock, client):
        self.socket = sock
        
        self.socket.send(str(GreetingPacket()))
        # Auth isn't working for now
        #packet = LoginRequestPacket.fromSocket(self.socket)
        packet = MySQLPacket.fromSocket(self.socket, get_data=True)
        self.socket.send(str(OKPacket(number=2)))
        
        print "Connected to %s" % (client[0])

        mongo = pymongo.Connection()
        mongo_coll = mongo["pysql_test"]
        print "Brought up MongoDB Connection"

        # Now just sit here relieving commands all day
        while True:
            command = CommandPacket.fromSocket(self.socket)
            print "%s: %s" % (command.description, command.statement)
            if command.statement.lower().find("select") != -1:
                """cols = ["Name", "City"]
                rows = [["Jon", "NYC"], ["GMP", "Worc"]]
                rs = ResultSet(cols, rows, "test_table", "test")
                self.socket.send(str(rs))"""
                query_info = SelectQuery(command.statement).execute()
                if not query_info:
                    print "Unsupported SELECT query."
                    self.socket.send(str(OKPacket()))
                    return
                table, cond = query_info
                if len(cond):
                    cond = cond[0]
                    print "Running db.%s.find(%s)" % (table, cond)
                    results = mongo_coll[table].find(cond)
                else:
                    print "Running db.%s.find()" % table
                    results = mongo_coll[table].find()

                # If we got any results, send them back
                if results.count():
                    # Convert everything to MySQL format
                    # Start by getting a list of all the columns
                    cols = results[0].keys()
                    # Delete the _id key to avoid issues for now
                    cols = [x for x in cols if x != "_id"]
                    # Put togeher all the dictionaries into flat rows
                    rows = []
                    for res in results:
                        data = []
                        for c in cols:
                            data.append(res[c])
                        rows.append(data)
                    print "Rows: %s" % rows
                    print "Cols: %s" % cols
                    # Turn it into actual packets and sent it out
                    rs = ResultSet(cols, rows, table, "pysql_test")
                    self.socket.send(str(rs))
                else:
                    self.socket.send(str(OKPacket()))


                        

            else:
                self.socket.send(str(OKPacket()))
            

    

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        MySQLServerSession(self.request, self.client_address)
        print "Done."



if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 3306

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


  