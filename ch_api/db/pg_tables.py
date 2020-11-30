

companyprofile_tables = """
CREATE TABLE IF NOT EXISTS companyprofile_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error VARCHAR NOT NULL);

CREATE TABLE IF NOT EXISTS companyprofile (
company_name VARCHAR NOT NULL,
company_number VARCHAR (8) PRIMARY KEY,
can_file BOOLEAN,
company_status VARCHAR,
status VARCHAR, -- This col is not even mentioned in the CH docs.
company_status_detail VARCHAR,
date_of_cessation DATE,
date_of_creation DATE,
etag VARCHAR,
external_registration_number VARCHAR,
has_been_liquidated BOOLEAN,
has_charges BOOLEAN,
has_insolvency_history BOOLEAN,
has_super_secure_pscs BOOLEAN,
is_community_interest_company VARCHAR,
jurisdiction VARCHAR, -- should be not null according to CH docs, but it's not.
last_full_members_list_date VARCHAR,
partial_data_available VARCHAR,
registered_office_is_in_dispute BOOLEAN,
subtype VARCHAR,
type VARCHAR NOT NULL,
undeliverable_registered_office_address BOOLEAN);

-- companyprofile BCNF decompositions ("links", "registered_office_address", "accounts", "annual_return",
--                                     "foreign_company_details", "branch_company_details", "confirmation_statement").

CREATE TABLE IF NOT EXISTS cp_links (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
charges VARCHAR,
overseas VARCHAR, -- this column is not even mentioned in the CH docs.
exemptions VARCHAR,  -- this column is not even mentioned in the CH docs.
filing_history VARCHAR,
insolvency VARCHAR,
officers VARCHAR,
persons_with_significant_control VARCHAR,
persons_with_significant_control_statements VARCHAR,
registers VARCHAR,
self VARCHAR NOT NULL,
uk_establishments VARCHAR); -- this column is not even mentioned in the CH docs

CREATE TABLE IF NOT EXISTS cp_registered_office_address (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
locality VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
address_premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS cp_accounts (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
accounting_reference_date_day INTEGER,
accounting_reference_date_month INTEGER, -- should be not null according to CH docs, but it's not.
last_accounts_made_up_to DATE,
last_accounts_period_end_on DATE,
last_accounts_period_start_on DATE,
last_accounts_type VARCHAR, -- should be not null according to CH docs, but it's not.
next_accounts_due_on DATE,
next_accounts_overdue BOOLEAN,
next_accounts_period_start_on DATE,
next_due DATE,
next_made_up_to DATE, -- should be not null according to CH docs, but it's not.
next_accounts_period_end_on DATE,
overdue BOOLEAN);

CREATE TABLE IF NOT EXISTS cp_annual_return (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
last_made_up_to DATE,
next_due DATE,
next_made_up_to DATE,
overdue BOOLEAN);

CREATE TABLE IF NOT EXISTS cp_foreign_company_details (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
accounting_requirement_foreign_account_type VARCHAR,
accounting_requirement_terms_of_account_publication VARCHAR,
accounts_account_period_from_day INTEGER,
accounts_account_period_from_month INTEGER,
accounts_account_period_to_day INTEGER,
accounts_account_period_to_month INTEGER,
accounts_must_file_within_months INTEGER,
business_activity VARCHAR,
company_type VARCHAR,
governed_by VARCHAR,
is_a_credit_finance_institution BOOLEAN,
is_a_credit_financial_institution BOOLEAN, -- this column is not even mentioned in the CH docs.
legal_form VARCHAR, -- this column is not even mentioned in the CH docs.
originating_registry_country VARCHAR,
originating_registry_name VARCHAR,
registration_number VARCHAR);

CREATE TABLE IF NOT EXISTS cp_branch_company_details(
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
business_activity VARCHAR,
parent_company_name VARCHAR, -- should be not null according to CH docs, but it's not.
parent_company_number VARCHAR); -- should be not null according to CH docs, but it's not.

CREATE TABLE IF NOT EXISTS cp_confirmation_statement(
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
last_made_up_to DATE,
next_due DATE,
next_made_up_to DATE,
overdue BOOLEAN);

-- companyprofile 4NF decompositions ("previous_company_names", "sic_codes").

CREATE TABLE IF NOT EXISTS cp_previous_company_names(
PRIMARY KEY (company_number, name, effective_from, ceased_on),
company_number VARCHAR (8) NOT NULL REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
ceased_on DATE NOT NULL,
effective_from DATE NOT NULL,
name VARCHAR);

CREATE TABLE IF NOT EXISTS cp_sic_codes(
PRIMARY KEY (company_number, sic_codes),
company_number VARCHAR (8) REFERENCES companyprofile(company_number) ON DELETE CASCADE ON UPDATE CASCADE,
sic_codes VARCHAR);"""

psc_tables = """
CREATE TABLE IF NOT EXISTS psc_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error VARCHAR NOT NULL);

CREATE TABLE IF NOT EXISTS psc_empty(
id_item_queried VARCHAR (8) PRIMARY KEY,
active_count INTEGER,
ceased_count INTEGER,
etag VARCHAR,
items_per_page INTEGER,
kind VARCHAR,
start_index INTEGER,
total_results INTEGER);

CREATE TABLE IF NOT EXISTS psc(
company_number VARCHAR (8) PRIMARY KEY,
active_count INTEGER,
ceased_count INTEGER,
etag VARCHAR,
items_per_page INTEGER,
kind VARCHAR,
links_persons_with_significant_control_statements_list VARCHAR,
links_persons_with_significant_control_statements VARCHAR, -- this column is not even mentioned in the CH docs.
links_self VARCHAR,
links_exemptions VARCHAR, -- this column is not even mentioned in the CH docs.
start_index INTEGER,
total_results INTEGER);

-- psc 4NF decomposition ("items").

CREATE TABLE IF NOT EXISTS psc_items(
company_number VARCHAR (8) NOT NULL REFERENCES psc(company_number) ON DELETE CASCADE ON UPDATE CASCADE, 
psc_serial_id SERIAL,
PRIMARY KEY (company_number, psc_serial_id),
ceased_on DATE,
country_of_residence VARCHAR,
date_of_birth_day INTEGER,
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
etag VARCHAR,
kind VARCHAR, -- this column is not even mentioned in the CH docs.
links_self VARCHAR,
description VARCHAR,
links_statement VARCHAR,
name VARCHAR,
nationality VARCHAR,
notified_on DATE);

-- psc[items] BCNF decompositions ("address",  "identification", "name_elements").

CREATE TABLE IF NOT EXISTS psc_items_address(
company_number VARCHAR (8), -- *
psc_serial_id INT, -- *
PRIMARY KEY (company_number, psc_serial_id),
FOREIGN KEY (company_number, psc_serial_id) REFERENCES psc_items(company_number, psc_serial_id) 
                                            ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
locality VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS psc_items_identification(
company_number VARCHAR (8), -- *
psc_serial_id INT, -- *
PRIMARY KEY (company_number, psc_serial_id),
FOREIGN KEY (company_number, psc_serial_id) REFERENCES psc_items(company_number, psc_serial_id) 
                                            ON DELETE CASCADE ON UPDATE CASCADE,
legal_authority VARCHAR, -- this column is not even mentioned in the CH docs.
registration_number VARCHAR, -- this column is not even mentioned in the CH docs.
legal_form VARCHAR, -- this column is not even mentioned in the CH docs.
place_registered VARCHAR, -- this column is not even mentioned in the CH docs.
country_registered VARCHAR -- this column is not even mentioned in the CH docs.
);

CREATE TABLE IF NOT EXISTS psc_items_name_elements(
company_number VARCHAR (8), -- *
psc_serial_id INT, -- *
PRIMARY KEY (company_number, psc_serial_id),
FOREIGN KEY (company_number, psc_serial_id) REFERENCES psc_items(company_number, psc_serial_id) 
                                            ON DELETE CASCADE ON UPDATE CASCADE,
forename VARCHAR,
middle_name VARCHAR,
other_forenames VARCHAR,
surname VARCHAR,
title VARCHAR);

-- psc[items] 4NF decompositions ("natures_of_control").

CREATE TABLE IF NOT EXISTS psc_items_natures_of_control(
company_number VARCHAR (8), -- *
psc_serial_id INT, -- *
PRIMARY KEY (company_number, psc_serial_id, natures_of_control),
FOREIGN KEY (company_number, psc_serial_id) REFERENCES psc_items(company_number, psc_serial_id) 
                                            ON DELETE CASCADE ON UPDATE CASCADE,
natures_of_control VARCHAR);"""

officerlist_tables = """
CREATE TABLE IF NOT EXISTS officerlist_http_errors (
id_item_queried VARCHAR PRIMARY KEY,
error VARCHAR NOT NULL);

CREATE TABLE IF NOT EXISTS officerlist_empty (
id_item_queried VARCHAR PRIMARY KEY,
etag VARCHAR DEFAULT NULL,
-- DROPPED: links VARCHAR DEFAULT NULL,
active_count INTEGER,
inactive_count INTEGER,
items_per_page INTEGER,
kind VARCHAR,
resigned_count INTEGER ,
start_index VARCHAR,
total_results INTEGER);

CREATE TABLE IF NOT EXISTS officerlist (
company_number VARCHAR PRIMARY KEY, 
etag VARCHAR UNIQUE,
links_self VARCHAR UNIQUE,
active_count INTEGER NOT NULL,
inactive_count INTEGER, -- should be NOT NULL as for CH docs, but it's not.
items_per_page INTEGER NOT NULL,
kind VARCHAR NOT NULL,
resigned_count INTEGER  NOT NULL,
start_index VARCHAR NOT NULL,
total_results INTEGER NOT NULL);

-- officerlist 4NF decompositions ("items").

CREATE TABLE IF NOT EXISTS ol_items (
company_number VARCHAR REFERENCES  officerlist(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
officer_serial_id SERIAL, -- officers don't have a UID in CH db.
PRIMARY KEY (company_number, officer_serial_id), -- 1 company_number : 1+ officer
appointed_on DATE,
country_of_residence VARCHAR,
date_of_birth_day INTEGER,
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
links_officer_appointments VARCHAR,
links_self VARCHAR,
name VARCHAR,
nationality VARCHAR,
occupation VARCHAR,
officer_role VARCHAR,
resigned_on DATE);

-- officerlist["items"] BCNF decompositions ("address", "identification")

CREATE TABLE IF NOT EXISTS ol_items_address (
company_number VARCHAR, -- *
officer_serial_id INTEGER,
PRIMARY KEY (company_number, officer_serial_id), -- 1 company_number : 1+ officer
FOREIGN KEY (company_number, officer_serial_id)
REFERENCES ol_items (company_number, officer_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR, -- should be NOT NULL as for CH docs, but it's not.
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR, -- should be NOT NULL as for CH docs, but it's not.
locality VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS ol_items_identification (
company_number VARCHAR,
officer_serial_id INTEGER,
PRIMARY KEY (company_number, officer_serial_id), -- 1 company_number : 1+ officer
FOREIGN KEY (company_number, officer_serial_id)
REFERENCES ol_items (company_number, officer_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
identification_type VARCHAR,
legal_authority VARCHAR,
legal_form VARCHAR,
place_registered VARCHAR,
registration_number VARCHAR);

-- officerlist["items"] 4NF decompositions ("former_names").

CREATE TABLE IF NOT EXISTS ol_items_former_names(
PRIMARY KEY (company_number, officer_serial_id, forenames, surname),
company_number VARCHAR NOT NULL,
officer_serial_id INTEGER NOT NULL,
FOREIGN KEY (company_number, officer_serial_id)
REFERENCES ol_items(company_number, officer_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
forenames VARCHAR DEFAULT 'not provided',  -- need DEFAULT as col used in composite pkey, cannot be NULL.
surname VARCHAR DEFAULT 'not provided'); -- need DEFAULT as col used in composite pkey, cannot be NULL."""

appointmentlist_tables = """
CREATE TABLE IF NOT EXISTS appointmentlist_http_errors (
id_item_queried VARCHAR PRIMARY KEY,
error VARCHAR NOT NULL);

CREATE TABLE IF NOT EXISTS appointmentlist(
appointmentlist_url_id VARCHAR UNIQUE NOT NULL,  -- same as links_self, renamed for clarity. 
-- DROPPED links_self VARCHAR,
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
etag VARCHAR,
is_corporate_officer BOOLEAN,
items_per_page INTEGER NOT NULL,
kind VARCHAR,
name VARCHAR,
start_index INTEGER NOT NULL,
total_results INTEGER NOT NULL);

-- appointmentlist 4NF decompositions ("items").

CREATE TABLE IF NOT EXISTS al_items(
appointmentlist_url_id VARCHAR NOT NULL,
appointment_serial_id SERIAL, -- appointments don't have a UID in CH db.
FOREIGN KEY (appointmentlist_url_id) REFERENCES appointmentlist(appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointmentlist_url_id, appointment_serial_id), -- 1 officer appointment JSON : 1+ appointments
appointed_before DATE,
appointed_on DATE,
appointed_to_company_name VARCHAR,
appointed_to_company_number VARCHAR,
appointed_to_company_status VARCHAR,
country_of_residence VARCHAR,
is_pre_1992_appointment BOOLEAN,
links_company VARCHAR,
name VARCHAR,
nationality VARCHAR,
occupation VARCHAR,
officer_role VARCHAR,
resigned_on DATE);

-- appointmentlist["items"] BCNF decompositions ("address", "identification", "name_elements")

CREATE TABLE IF NOT EXISTS al_items_address(
appointmentlist_url_id VARCHAR NOT NULL,
appointment_serial_id INTEGER,
FOREIGN KEY (appointmentlist_url_id, appointment_serial_id) 
REFERENCES al_items(appointmentlist_url_id, appointment_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointmentlist_url_id, appointment_serial_id),
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
locality VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS al_items_identification(
appointmentlist_url_id VARCHAR NOT NULL,
appointment_serial_id INTEGER,
FOREIGN KEY (appointmentlist_url_id, appointment_serial_id) 
REFERENCES al_items(appointmentlist_url_id, appointment_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointmentlist_url_id, appointment_serial_id),
identification_type VARCHAR,
legal_authority VARCHAR,
legal_form VARCHAR,
place_registered VARCHAR,
registration_number VARCHAR);

CREATE TABLE IF NOT EXISTS al_items_name_elements(
appointmentlist_url_id VARCHAR NOT NULL,
appointment_serial_id INTEGER,
FOREIGN KEY (appointmentlist_url_id, appointment_serial_id) 
REFERENCES al_items(appointmentlist_url_id, appointment_serial_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointmentlist_url_id, appointment_serial_id),
forename VARCHAR,
honours VARCHAR,
other_forenames VARCHAR,
surname VARCHAR,
title VARCHAR);

-- appointmentlist["items"] 4NF decompositions ("former_names").

CREATE TABLE IF NOT EXISTS al_items_former_names(
PRIMARY KEY (appointmentlist_url_id, appointment_serial_id, forenames, surname),
appointmentlist_url_id VARCHAR NOT NULL,
appointment_serial_id INTEGER,
FOREIGN KEY (appointmentlist_url_id, appointment_serial_id) 
REFERENCES al_items(appointmentlist_url_id, appointment_serial_id) ON DELETE CASCADE ON UPDATE CASCADE,
forenames VARCHAR DEFAULT 'not provided',  -- need DEFAULT as col used in composite pkey, cannot be NULL.
surname VARCHAR DEFAULT 'not provided'); -- need DEFAULT as col used in composite pkey, cannot be NULL."""
