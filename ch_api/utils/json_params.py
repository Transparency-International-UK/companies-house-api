#!/usr/bin/python3

companyprofile_params = {
	"is_root": True,
	"name": "companyprofile",
	"abbreviation": "cp",
	"arrays": [
		{"name": "previous_company_names",
		 "uid_key": ["company_number", "name", "effective_from", "ceased_on"]
			},
		{"name": "sic_codes",
		 "uid_key": ["company_number", "sic_codes"]
			}
		],
	"leaves": [
		{"name": "links"},
		{"name": "registered_office_address"},
		{"name": "accounts"},
		{"name": "annual_return"},
		{"name": "foreign_company_details"},
		{"name": "branch_company_details"},
		{"name": "confirmation_statement"}
		],
	"uid_key": ["company_number"]
	}

psc_params = {
	"is_root": True,
	"name": "psc",
	"abbreviation": "psc",
	"items_per_page": 100,
	"arrays": [{
		"name": "items",
		"abbreviation": "items",
		"arrays": [
			{"name": "natures_of_control",
			 "abbreviation": None,  # no further unpacking needed.
			 "uid_key": ["company_number", "psc_serial_id", "natures_of_control"]
				}
			],
		"uid_key": ["company_number", "psc_serial_id"],
		"leaves": [
			{"name": "address"},
			{"name": "identification"},
			{"name": "name_elements"}
			],
		}],
	"uid_key": ["company_number"],
	"drop_if_empty": ["items", "links"],
	}

officerlist_params = {
	"is_root": True,
	"name": "officerlist",
	"abbreviation": "ol",
	"items_per_page": 100,
	"arrays": [{
		"name": "items",
		"abbreviation": "items",
		"uid_key": ["company_number", "officer_serial_id"],
		"arrays": [{
			"name": "former_names",
			"abbreviation": None,  # no further unpacking needed.
			"uid_key": ["company_number", "officer_serial_id", "forenames", "surname"]
			}],
		"leaves": [
			{"name": "address"},
			{"name": "identification"}
			]
		}],
	"uid_key": ["company_number"],
	"drop_if_empty": ["items", "links"],
	}

appointmentlist_params = {
	"is_root": True,
	"name": "appointmentlist",
	"abbreviation": "al",
	"arrays": [{
		"name": "items",
		"abbreviation": "items",
		"uid_key": ["appointmentlist_url_id", "appointment_serial_id"],
		"arrays": [{
			"name": "former_names",
			"abbreviation": None,  # no further unpacking needed.
			"uid_key": ["appointmentlist_url_id", "appointment_serial_id", "forenames", "surname"]
			}],
		"leaves": [
			{"name": "address"},
			{"name": "identification"},
			{"name": "name_elements"}
			]
		}],
	"items_per_page": 50,
	"uid_key": ["appointmentlist_url_id"],
	"drop_if_empty": ["items", "links"],
	"drop_from_root": ["links"]
	}
