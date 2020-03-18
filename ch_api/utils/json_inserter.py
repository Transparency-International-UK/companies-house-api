#!/usr/bin/python3

from typing import Union

from db.pg_constants import DB_SCHEMA, DB_CONFIG_ABS_PATH, DB_CONFIG_SECTION
from db.pg_engine import MyDb
from utils.helpers import flatten_nested_dicts_only as flatten
from utils.helpers import nullify_empty_str_in_dict_vals as nullify_str
from utils.helpers import is_str_and_empty

# define types ensembles for type checking
Number = (int, float)
Atom = (str, Number)
Collection = (list, tuple, set)

# how to use
"""
from utils.json_params import officerlist_params, psc_params, companyprofile_params
from utils.json_getter import Getter
from utils.json_inserter import Inserter

company_numbers = ["OC418979", "SO302993", "OC303424", "OC350154", "OC424474"]  # or read from file        
params = [officerlist_params, psc_params, companyprofile_params]
for company_number in company_numbers:
    for params_dict in params:
        extractor = Getter(json_params=params_dict, url_id=company_number)
        json, _, _ = extractor.extract()
        inserter = Inserter(json=json, params=params_dict)
        inserter.unpack(uid_value=company_number)
"""

# start engine
engine = MyDb(db_config_file=DB_CONFIG_ABS_PATH, db_section_name=DB_CONFIG_SECTION, schema=DB_SCHEMA)


class Inserter:

    """
    class that recursively walk nested data objects and insert data in postgres tables.
    table names are created step by step during the walk down the the nested data.
    the word "key" is used in JSON semantics (key: value pair). Not in the SQL context.
    the word "uid_key" hence signifies the columns of a primary key of a table, whose values are "uid_values".
    """

    def __init__(self, json, params):
        self.reset(json, params)

    # defining a reset method is preferred over manually calling __init__().
    def reset(self, json, params, **kwargs):
        # initialise the resource, the param dictionary.
        self.json = json
        self.params = params

        # initialise the list of param dictionaries of all the arrays and leaves in the resource.
        self.arrays_params = params.get("arrays", [])
        self.leaves_params = params.get("leaves", [])

        # initialise all the information on the root and branches keys (columns of the tables used to pkey).
        self.uid_key = params.get("uid_key", None)
        self.arrays_keys = [dict_.get("name") for dict_ in self.arrays_params] if self.arrays_params else []
        self.leaves_keys = [dict_.get("name") for dict_ in self.leaves_params] if self.leaves_params else []
        self.json_root_uid_pair = kwargs.get("json_root_uid_pair", None)

        # initialise information regarding the keys to drop from the resource.
        self.drop_from_root = self.params.get("drop_from_root", [])
        self.drop_if_empty = self.params.get("drop_if_empty", [])
        self.total_results = self.json.get("total_results", None)
        self.leaves_drop_keys = [dict_.get("drop", []) for dict_ in self.leaves_params] if self.leaves_params else []

        # initialise boolean expressions used to check the resource content.
        self.json_is_error = "error" in self.json
        self.json_is_empty = (self.total_results is not None and self.total_results == 0)

    def unpack(self, uid_value=None, branch_table_name=None):

        # check illegal cases (no uid_key present, uid_key not passed as a Collection)
        if self.uid_key is None:
            raise TypeError("Every table needs a primary key. Please add it to the configuration dictionary.")

        if self.uid_key is not None and not isinstance(self.uid_key, Collection):
            raise TypeError("\"uid_key\" should be passed as a list or a set")

        # the uid_pair is created (1) to create a unique k:v pair to add to the root json data if it has none and
        # (2) in recursive calls of unpack() to add the unique k:v pairs to the branches of the json to fkey with root.
        uid_pair = self.create_uid_pair(uid_key=self.uid_key,
                                        uid_value=uid_value)

        # the root data uid_value needs to be added to all branches => json_root_uid_pair - see (2) above.
        if self.params.get("is_root", None) is not None:
            # upon initialisation json_root_uid_pair is None. First time unpack() executes (root level) uid_pair created
            # is the root of the json tree. In recursive calls of unpack() (branch levels) instance is reset passing
            # the uid_pair of root level as optional kwarg to json_root_uid_pair parameter.
            self.json_root_uid_pair = uid_pair

        # handle cases in which API returned an error object or
        # an object containing an empty array => {"name": "bar", "array_key": [], "total_results": 0}
        if self.json_is_error or self.json_is_empty:

            engine.execute(
                mode="write",
                query="INSERT INTO {table} ({fields}) VALUES ({placeholders}) "
                      "ON CONFLICT ({p_key}) DO UPDATE "  # upsert
                      "SET ({fields}) = ({placeholders})",
                table=self.params.get("name") + "_" + "http_errors"
                      if self.json_is_error
                      else self.params.get("name") + "_" + "empty",
                p_key=["id_item_queried"],
                data=self.make_data_from_dict(source=self.json,
                                              add={"id_item_queried": uid_value},
                                              drop=None if self.json_is_error else self.drop_if_empty))
            return

        # preprocess the data before upsertion.
        data = self.make_data_from_dict(source=self.json,
                                        add=uid_pair,  # if uid_pair is empty {}, nothing is added to data dictionary.
                                        drop=self.arrays_keys
                                           + self.leaves_keys
                                           + self.drop_from_root)

        # first time unpack() executes branch_table_name is None.
        # in recursive calls branch_table_name will be name the branch table passed from the previous stack frame.
        root_table_name, branch_table_draft_name = self.create_table_variables(branch_table_name)

        # perform upsert of root level data: if the record is already present in the table, it'll be overwritten
        # returning the values of the primary key so it can be added to the branches dictionaries as foreign key.

        # delete old records in root table, it will cascade to branch tables.
        # IMPORTANT: for this to work always add ON DELETE CASCADE ON UPDATE CASCADE to all FOREIGN KEY.
        if self.params.get("is_root", None):

            fields_root_id = list(self.json_root_uid_pair.keys())
            data_root_value = list(self.json_root_uid_pair.values())

            engine.execute(mode="write",
                           query="DELETE FROM {table} WHERE {fields} = %s",
                           fields=fields_root_id,
                           table=root_table_name,
                           data=data_root_value)

        # insert new records.
        branch_uid_value_tup = engine.execute(mode="write + read",
                                              query=("INSERT INTO {table} ({fields}) VALUES ({placeholders}) "
                                                     "RETURNING {p_key}"),
                                              p_key=self.uid_key,
                                              table=root_table_name,
                                              data=data)

        # connection.fetchall() returns tuple => single key: (["bar"],) // composite key: ([("bar", "foo"),],)
        branch_uid_value = branch_uid_value_tup[0]

        # ensure we capture any SERIAL type added by INSERT to create composite keys.
        updated_uid_pair = (isinstance(branch_uid_value[0], Atom)  # the returned pkey is non composite.
                            and dict(zip(self.uid_key, branch_uid_value))
                            or isinstance(branch_uid_value[0], Collection)  # the returned pkey is composite.
                            and dict(zip(self.uid_key, branch_uid_value[0])))

        # BCNF decompositions: prune leaves from the root json object.
        if self.leaves_keys:

            for leaf_key, leaf_keys_to_drop in zip(self.leaves_keys, self.leaves_drop_keys):
                leaf_data = self.json.get(leaf_key, None)
                branch_table_name = branch_table_draft_name + leaf_key

                if leaf_data is not None:
                    # root -> leaf is a 1:1 dependency.
                    # in case of uid conflict, replace using upsert.
                    # leaves are outright flattened.
                    engine.execute(mode="write",
                                   query=("INSERT INTO {table} ({fields}) VALUES ({placeholders}) "
                                          "ON CONFLICT ({p_key}) DO UPDATE "
                                          "SET ({fields}) = ({placeholders})"),
                                   table=branch_table_name,
                                   p_key=self.uid_key,
                                   data=self.make_data_from_dict(source=leaf_data,
                                                                 add=updated_uid_pair,
                                                                 drop=leaf_keys_to_drop))

        # 4NF decompositions: recursively unpack() branches of the root json which contains k:v where v is an array.
        if self.arrays_keys:
            for array_key, array_params in zip(self.arrays_keys, self.arrays_params):
                array_data = self.json.get(array_key, None)

                if array_data is not None:
                    branch_table_name = branch_table_draft_name + array_key

                    if isinstance(array_data[0], dict):

                        for element in array_data:

                            # create new instance with the dictionary element in the array.
                            # reset the instance with new root data (root of the array branch)
                            # and the array_params taken from the configuration dictionary.
                            array_instance = Inserter(json={}, params={})
                            array_instance.reset(json=element,
                                                 params=array_params,
                                                 json_root_uid_pair=self.json_root_uid_pair)

                            # recursively unpack until array_params is None.
                            if array_params is not None:
                                array_instance.unpack(branch_table_name=branch_table_name,
                                                      # uid_value of the original root level data allows to fkey
                                                      # on root table. SERIAL type is added for each array element.
                                                      uid_value=branch_uid_value)

                    elif isinstance(array_data[0], Atom):

                        # we cannot perform upsert with ON CONFLICT (p_key) DO UPDATE...
                        # simply delete records with root json key and bulk insert.
                        engine.execute(mode="write",
                                       query="DELETE FROM {table} WHERE {fields} = %s",
                                       fields=list(self.json_root_uid_pair.keys()),
                                       table=branch_table_name,
                                       data=list(self.json_root_uid_pair.values()))

                        if array_key in array_params.get("uid_key"):
                            fields = array_params.get("uid_key")
                        else:
                            fields = array_params.get("uid_key") + [array_key]

                        # prepare data and query for bulk insertion.
                        data_tuples = list(map(self.make_data_from_atom,
                                               array_data,
                                               # create list with all uid_values (in case composite key).
                                               # As many as len(array_data) so map has the the same num of arguments.
                                               [[element for element in list(branch_uid_value)] for _ in array_data]))

                        # [('bar', 1), ('foo', 2)] -> ('bar', 1, 'foo', 2)
                        data = list(sum(data_tuples, ()))

                        bulk_insert = self.prepare_bulk_insert_query(array=array_data)

                        engine.execute(mode="write",
                                       query=bulk_insert,
                                       table=branch_table_name,
                                       data=data,
                                       fields=fields)
                    else:
                        # lists of lists are not dealt with.
                        raise TypeError(
                            "You reached an array of iterables in the JSON. You need to create a conditional"
                            " branch to handle this edge case.")
                else:
                    # makes sure that if first array key checked is not present, program continues.
                    continue

    def create_table_variables(self, branch_table_name: str) -> [str, str]:
        """
        generates root level data table names and branch level data draft table names.
        branches table names final composition will happen at insertion time by adding the name of the branch.
        """
        if branch_table_name is None:   # root level data.

            # table of root-level data has name of json. ex. "companyprofile".
            # table names for the branches of root level data starts with root table abbreviation + "_". ex. "cp_"
            return self.params.get("name"), self.params.get("abbreviation") + "_"

        elif branch_table_name is not None:  # branch level data.

            # branch of branch table names starts with the parent table name + "_". ex. "cp_items_"
            if self.arrays_params or self.leaves_keys:  # ensure branches of branches are indeed present.
                return branch_table_name, branch_table_name + "_"

            else:  # otherwise (no further unpacking needed) simply return table to insert to and an empty string.
                return branch_table_name, ""

    def create_uid_pair(self, uid_key: Collection, uid_value: Union[None, list]) -> dict:
        """
        generates the uid_pair of the object. If json does not have unique k: v pair uid_value can be passed.
        otherwise it's extracted from the data itself.
        """
        uid_pair = {}

        if uid_value is not None and isinstance(uid_value, Atom):
            uid_pair = dict(zip(uid_key, [uid_value]))

        elif uid_value is not None and isinstance(uid_value, Collection):
            uid_pair = dict(zip(uid_key, uid_value))

        # the uid_value is already present in the root level data. Simply extract it.
        elif uid_value is None:
            uid_pair = {k: v for k, v in self.json.items() if k in uid_key}

        return uid_pair

    @staticmethod
    def make_data_from_dict(source: dict, add: dict, drop: (list, None)) -> dict:
        """preprocess dictionary data by:
             * flattening the dictionary;
             * adding and dropping necessary k:v pairs;
             * nullifying all empty string replacing them with None.
        """
        data = flatten(source, drop)
        return nullify_str(dict(data, **add))

    @staticmethod
    def make_data_from_atom(source: Atom, add: list, prepend=True) -> tuple:
        if is_str_and_empty(val=source):
            data = [None]
        else:
            data = [source]

        if prepend:
            data = add + data
        else:
            data.extend(add)

        return tuple(data)

    @staticmethod
    def prepare_bulk_insert_query(array: Collection, draft_stmt="INSERT INTO {table} ({fields}) VALUES {to_do};") -> str:
        append = (" ({placeholders})," * len(array)).rstrip(",")
        query = draft_stmt.format(table="{table}", fields="{fields}", to_do=append)
        return query