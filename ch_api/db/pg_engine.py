#!/usr/bin/python3

from configparser import ConfigParser
import psycopg2
from psycopg2 import sql
from functools import (partial, reduce,)


# supporting stuff

def read_config(filename, section):
    """func to extract the parameters of db configuration form a config file."""

    parser = ConfigParser()

    if not parser.read(filename):
        raise Exception(f"Reading from File: {filename} seems to return and empty object.")
    else:
        parser.read(filename)

    dict_ = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            dict_[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file.")

    return dict_


def data_has_been_wrongly_passed(args):
    data = args["data"]
    if not isinstance(data, dict):
        if not isinstance(data, (list, tuple)):
            return True
    else:
        return False


def fields_has_been_wrongly_passed(args):
    data = args["data"]
    if isinstance(data, dict):
        if args["fields"] is not None:   # if data is a dictionary, "fields" should be None by default.
            return True
    elif isinstance(data, (list, set)):
        if args["fields"] is None:  # if data is a iterable, "fields" should should be passed explicitly by user.
            return True


class MyDb:
    """database object to connect and execute row sql queries."""

    def __init__(self, db_config_file, db_section_name, schema=None):
        self.db_config_file = db_config_file
        self.db_section_name = db_section_name
        self.params = read_config(filename=db_config_file, section=db_section_name)
        self.schema = schema  # default execution will be on public schema when schema is None.

    def connect(self):

        try:
            connection = psycopg2.connect(**self.params)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        if self.schema is not None:
            cur = connection.cursor()
            schema = sql.Identifier(self.schema)

            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema}").format(schema=schema))

            # ensures all transactions executed with this connection will be done in the schema chosen.
            cur.execute(sql.SQL("SET search_path TO {schema}, public;").format(schema=schema))

            connection.commit()

        if connection is not None:
            return connection

    def execute(self,
                mode,
                query,
                schema=None,
                table=None,
                fields=None,
                data=None,
                drop_keys=None,
                **kw_options):

        # check kw arguments are ok.

        kwargs = locals()

        if mode not in ["read", "write", "write + read"]:
            raise SyntaxError("\"mode\" must be: \"read\", \"write\" or \"write + read\".")

        if "placeholders" in kwargs:
            raise ValueError("\"placeholders\" will be compiled at runtime from the \"data\" parameter. \n"
                             "Do not pass explicitly.")

        if data is not None:
            if data_has_been_wrongly_passed(kwargs):
                raise TypeError("\"data\" should be passed as a dictionary or an iterable, "
                                "even if is has one only element.\n If you are passing a query without inserting data, "
                                "\"data\" is defaulted to None.")

            if fields_has_been_wrongly_passed(kwargs):
                raise ValueError("\"fields\" argument should be passed IF the \"data\" argument is an iterable.\n"
                                 "If not, the \"data\" argument can only be a dictionary, in which case the \n"
                                 "\"fields\" parameter will be created automatically from the dictionary keys.\n"
                                 "If you want to drop some k:v pairs from the insertion, use the \"drop_keys\" "
                                 "kw argument")

        try:
            conn = self.connect()

            with conn:  # context manager will commit() automatically or rollback() if error.

                with conn.cursor() as curs:

                    # create sql identifier map from the NON optional keyword arguments.
                    locals_ = {k: v for k, v in kwargs.items() if k in ["schema",
                                                                        "table",
                                                                        "fields",
                                                                        "data",
                                                                        "drop_keys", ]}

                    # locals_ also contains the "data":v pair, which won't be touched.
                    # pipeline declaratively composing the functions to be reduced on locals_.
                    locals_with_sql_ids = self.reduce_fns_on_dict(fns=[partial(self.create_sql_id, on_param="schema"),
                                                                       partial(self.create_sql_id, on_param="table"),
                                                                       self.add_fields_and_placeholders],
                                                                  dic=locals_)

                    if kw_options:
                        # kw_options being optional, we need to compose the functions iteratively not declaratively.
                        fns_to_reduce = [partial(self.create_sql_id, on_param=k) if isinstance(v, str)
                                         else partial(self.create_sql_ids_from_list, on_list_param=k)
                                         if isinstance(v, (list, tuple))
                                         else []
                                         for k, v in kw_options.items()]

                        kwargs_with_sql_id = self.reduce_fns_on_dict(fns=fns_to_reduce, dic=kw_options)

                        # execute query unpacking both locals_with_sql_ids and kwargs_with_sql_id.
                        curs.execute(sql.SQL(query).format(**locals_with_sql_ids, **kwargs_with_sql_id),
                                     data)  # if data is None, execute() will work just fine.
                    else:
                        curs.execute(sql.SQL(query).format(**locals_with_sql_ids),
                                     data)  # if data is None, execute() will work just fine.

                    if mode == "read" or mode == "write + read":
                        # fetch object of select stmt.
                        return curs.fetchall()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            # in case something when wrong in closing the connection in the try block.
            if conn is not None:
                conn.close()

    @staticmethod
    def reduce_fns_on_dict(fns, dic):
        return reduce(lambda d, f: f(d), fns, dic)

    @staticmethod
    def create_sql_id(dic, on_param):
        param = dic.get(on_param)    # all kw arguments are defaulted to None in function definition.
        if param is not None:
            dic[on_param] = sql.Identifier(param)  # overwrite with sql id
            return dic
        else:
            # if the value of on_param is None, we drop it from the dictionary.
            dic.pop(on_param) if dic[on_param] is None else dic
            return dic

    @staticmethod
    def create_sql_ids_from_list(dic, on_list_param):
        list_param = dic.get(on_list_param)  # (, None) unnecessary, kw args are defaulted to None in func definition.
        if list_param is not None:
            dic[on_list_param] = sql.SQL(', ').join(map(sql.Identifier, list_param))  # overwrite with sql id
            return dic
        else:
            # if the value of on_list_param is None, we drop it from the dictionary.
            dic.pop(on_list_param) if dic[on_list_param] is None else dic
            return dic

    @staticmethod
    def add_fields_and_placeholders(dic):
        data = dic.get("data")  # all kw arguments are defaulted to None in function definition.
        if data is not None and isinstance(data, dict):
            drop = list() if dic.get("drop_keys", None) is None \
                else dic["drop_keys"]
            fields = [k for k in data if k not in drop]
            dic["fields"] = sql.SQL(', ').join(map(sql.Identifier, fields))  # overwrite with sql id
            dic["placeholders"] = sql.SQL(', ').join(map(sql.Placeholder, fields))  # add new k:v pair with sql id

        if data is not None and isinstance(data, (list, tuple)):
            fields_num = len(dic["fields"])  # needed to know how many placeholders we need to create.
            dic["fields"] = sql.SQL(', ').join(map(sql.Identifier, dic["fields"]))  # overwrite with sql id
            dic["placeholders"] = sql.SQL(', ').join(sql.Placeholder() * fields_num)  # add new k:v pair with sql id

        return dic

