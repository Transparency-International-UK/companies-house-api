#!/usr/bin/python3

import pandas as pd

from db.pg_constants import DB_CONFIG_SECTION, DB_CONFIG_ABS_PATH, DB_SCHEMA
from db.pg_engine import MyDb
from db.pg_tables import companyprofile_tables, psc_tables
from db.pg_tables import officerlist_tables, appointmentlist_tables
from utils.json_getter import Getter
from utils.json_inserter import Inserter
from utils.json_params import psc_params, companyprofile_params
from utils.json_params import officerlist_params, appointmentlist_params
from utils.cli import parser
from utils.cli import file_is_csv_or_txt, optional_flags_collide, data_wont_fit_excel
from utils.cli import file_contains_company_codes, url_ids_examples
from utils.helpers import read_file_with_url_ids


# cli arguments constants
ARGS = parser.parse_args()

ARGS_PARAMS = {'al' : {"params"      : appointmentlist_params,
                       "create_stmts": appointmentlist_tables,
                       "all_tables"  : ["appointmentlist",
                                        "al_items",
                                        "al_items_address",
                                        "al_items_identification",
                                        "al_items_name_elements",
                                        "al_items_former_names"]},
               'ol' : {"params"      : officerlist_params,
                       "create_stmts": officerlist_tables,
                       "all_tables"  : ["officerlist_http_errors",
                                        "officerlist_empty",
                                        "ol_items",
                                        "ol_items_address",
                                        "ol_items_identification",
                                        "ol_items_former_names"]},
               'psc': {"params"      : psc_params,
                       "create_stmts": psc_tables,
                       "all_tables"  : ["psc_items",
                                        "psc_items_name_elements",
                                        "psc_items_identification",
                                        "psc_items_address",
                                        "psc_http_errors",
                                        "psc_items_natures_of_control"]},
               'cp' : {"params"      : companyprofile_params,
                       "create_stmts": companyprofile_tables,
                       "all_tables"  : ["companyprofile",
                                        "cp_registered_office_address",
                                        "companyprofile_http_errors",
                                        "cp_sic_codes",
                                        "cp_previous_company_names"]}}

SELECT_ALL = "select * from {};"


# supporting functions for main()
def make_url_list(args):
    """
    given a file url runs checks for illegal cases and extracts the serializes content of the file to an iterable.
    """

    if not file_is_csv_or_txt(args):
        raise ValueError("The file where you store the url_ids has to be in csv format.")

    else:
        url_ids = read_file_with_url_ids(path=args.file)

    if data_wont_fit_excel(args, url_ids):
        raise ValueError("You won't be able to dump more than 1,048,576 rows in an excel file. \n"
                         "Please reduce the number of url_ids to be queried in the csv file containing them.")

    return url_ids


def run_flags_check(args, url_ids):
    """
    runs checks for all illegal cases when using the flags with prog.py
    """

    if optional_flags_collide(args):
        raise ValueError("When passing the --al flag, other flags are automatically deactivated.\n"
                         "The url for the appointmentslist resource is different from the url required by"
                         " psc, cp and ol.\n\n" + url_ids_examples)

    if args.al is True and file_contains_company_codes(url_ids):

        raise ValueError("It looks lik you have provided a file containing company codes with the --al flag.\n"
                         "Company codes can only be used for --psc --ol and --cp flags.\n\n"
                         + url_ids_examples
                         + "Here's the list of url that were read (and cleaned) from the file.\n"
                         + " \n".join(url_ids[:5] if len(url_ids) > 5 else url_ids))

    if (args.psc is True or args.cp is True or args.ol is True) and not file_contains_company_codes(url_ids):

        raise ValueError("It looks lik you have provided a file which does not contain company codes.\n"
                         "Company codes are required for the --psc --ol and --cp flags.\n\n"
                         + url_ids_examples
                         + "Here's the list of url that were read (and cleaned) from the file.\n\n"
                         + " \n".join(url_ids[:5] if len(url_ids) > 5 else url_ids))
    return None


def dump_to_excel(args, args_params, query, conn):
    """
    iteratively apply SELECT * FROM {table} and creates Excel files, one table per Excel sheet.
    """

    if args.excel is True:

        # build list of dictionaries {json flag: list of table names}.
        # all_tables_dicts = [{"cp" : ["companyprofile", "cp_sic_codes", ...]},
        #                     {"ol" : ["ol_items", "ol_items_address", ...]}, ...]
        all_tables_dicts = [{key: dict_["all_tables"]} for key, dict_ in args_params.items() if vars(args)[key]]

        # What we are building to do with comprehension => df_name.to_excel(writer, sheet_name='some_table_name')
        for table_dict in all_tables_dicts:

            # build dictionary of dataframes read from pg.
            # {"cp" : [{"companyprofile": df}, {"cp_sic_codes": df},...]}
            df_hash = {k: [{table: pd.read_sql_query(query.format(table), conn) for table in v}]
                       for k, v in table_dict.items()}

            # create list of writer instances.
            writers = [pd.ExcelWriter(DB_SCHEMA + '_' + k + '.xlsx', engine='xlsxwriter')
                       for k, _ in df_hash.items()]

            # write to excel file.
            for writer, (k, v) in zip(writers, df_hash.items()):
                for dic in v:
                    for tab, df in dic.items():
                        df.to_excel(writer, sheet_name=tab)

                # Close the Pandas Excel writer and output the Excel file.
                writer.save()
        return


def main(args, args_params):

    # get url_ids from file and check flags passed by user.
    url_ids = make_url_list(args)
    run_flags_check(args, url_ids=url_ids)

    # create engine instance
    engine = MyDb(db_config_file=DB_CONFIG_ABS_PATH, db_section_name=DB_CONFIG_SECTION, schema=DB_SCHEMA)
    connection = engine.connect()

    # create list of create statements
    create_stmts = [dict_["create_stmts"] for key, dict_ in args_params.items() if vars(args)[key]]

    # execute create statement
    _ = list(map(lambda x: engine.execute(mode="write", query=x), create_stmts))

    # create list of params dictionaries.
    params = [dict_["params"] for key, dict_ in args_params.items() if vars(args)[key]]

    # for al flag.
    if args.al:

        for appointmentlist_id in url_ids:
            extractor = Getter(appointmentlist_params, appointmentlist_id)
            json, _, _ = extractor.extract()
            inserter = Inserter(json=json, params=appointmentlist_params)
            inserter.unpack(uid_value=appointmentlist_id)

    # for all other flags (psc, ol, cp).
    if args.ol or args.psc or args.cp:

        for company_number in url_ids:
            for params_dict in params:
                extractor = Getter(json_params=params_dict, url_id=company_number)
                json, _, _ = extractor.extract()
                inserter = Inserter(json=json, params=params_dict)
                inserter.unpack(uid_value=company_number)

    if args.excel is True:
        dump_to_excel(args=ARGS, args_params=ARGS_PARAMS, query=SELECT_ALL, conn=connection)

if __name__ == '__main__':

    main(args=ARGS, args_params=ARGS_PARAMS)
