# TODO turn into fully fledged unit test with assertions.

from db.pg_engine import MyDb
from db.pg_constants import DB_CONFIG_ABS_PATH, DB_CONFIG_SECTION, DB_SCHEMA
from utils.json_getter import Getter
from utils.json_inserter import Inserter
from utils.json_params import (companyprofile_params, officerlist_params,
                               psc_params, appointmentlist_params)
from db.pg_tables import (companyprofile_tables, officerlist_tables,
                          psc_tables, appointmentlist_tables)


engine = MyDb(db_config_file=DB_CONFIG_ABS_PATH, db_section_name=DB_CONFIG_SECTION, schema=DB_SCHEMA)
# cpresources = [{'accounts': {'last_accounts': {'type': 'null'}},
#  'can_file': False,
#  'company_name': 'ELEBEX LP',
#  'company_number': 'LP016212',
#  'company_status': 'active',
#  'date_of_creation': '2014-09-16',
#  'etag': '0314941c1bacb1c22c64afb02e6432ac15401b60',
#  'has_been_liquidated': False,
#  'has_charges': False,
#  'has_insolvency_history': False,
#  'jurisdiction': 'england-wales',
#  'links': {'filing_history': '/company/LP016212/filing-history',
#            'self': '/company/LP016212'},
#  'previous_company_names': [{'ceased_on': '2019-09-04',
#                              'effective_from': '2019-08-21',
#                              'name': 'LP016212 LP'},
#                             {'ceased_on': '2019-08-21',
#                              'effective_from': '2014-09-16',
#                              'name': 'ELEBEX LP'}],
#  'registered_office_address': {'address_line_1': 'Suite 6086 128 Aldersgate '
#                                                  'Street',
#                                'address_line_2': 'Barbican',
#                                'country': 'England',
#                                'locality': 'London',
#                                'postal_code': 'EC1A 4AE'},
#  'registered_office_is_in_dispute': False,
#  'sic_codes': ['code1', 'code2'],
#  'type': 'limited-partnership',
#  'undeliverable_registered_office_address': False}, {"error": "Item not found"}, {"total_results": 0}]

# create tables
tables_queries = [appointmentlist_tables, officerlist_tables, psc_tables, companyprofile_tables]
_ = list(map(lambda x: engine.execute(mode="write", query=x), tables_queries))


company_codes = ["OC399321", "AWASDF23", "OC323310", "OC399321"]
for code in company_codes:
    for params in [companyprofile_params, psc_params, officerlist_params]:
        extractor = Getter(params, code)
        json, params, url_id = extractor.extract()
        inserter = Inserter(json=json, params=params)
        inserter.unpack(uid_value=code)

new_ids = ["/officers/somerandomidthatwontbefound/appointments",
           "/officers/sYD9QKtSRdN9TRJ0aukVY3hJHqw/appointments",
           "/officers/sYD9QKtSRdN9TRJ0aukVY3hJHqw/appointments"]

for officer_id in new_ids:
    extractor = Getter(appointmentlist_params, officer_id)
    json, _, _ = extractor.extract()
    inserter = Inserter(json=json, params=appointmentlist_params)
    inserter.unpack(uid_value=officer_id)


