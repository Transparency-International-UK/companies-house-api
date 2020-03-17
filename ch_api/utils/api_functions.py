#!/usr/bin/python3

from utils.utils_constants import API_KEY_ABS_PATH

from backoff import on_exception, expo
import requests
from requests import ConnectionError, Timeout, HTTPError
from ratelimit import limits, sleep_and_retry
from typing import Union


KEY = open(API_KEY_ABS_PATH).read().strip()

FIVE_MINUTES = 300  # Number of seconds in five minutes.

API_BASE_URL = "https://api.companieshouse.gov.uk"


@sleep_and_retry  # if we exceed the rate limit imposed by @limits, it forces sleep until we can start again.
@on_exception(expo, (ConnectionError, Timeout, HTTPError), max_tries=10)
@limits(calls=1000, period=FIVE_MINUTES)  # CH enforces a 600 queries per 5 minutes limit.
def call_api(url: str, api_key: str) -> Union[None, dict]:
	"""
	func to generate a query for an API with auth=(key, ""). Decorators handle rate limit calls and exceptions.
	:param url: string, url of the query.
	:param api_key: string, apy_key.
	:return: if status_code is 200 func returns a JSON object.
			 if status_code is http error func returns {"error":"error_string"}
			 if status_code is not 200/404 func re-runs up to 10 times if exceptions in @on_exception tuple
			 argument are raised. If 11th attempt fails, return None and print 'API response: {}'.format(r.status_code).
	"""
	r = requests.get(url, auth=(api_key, ""))

	if not (r.status_code == 200 or r.status_code == 404 or r.status_code == 401 or r.status_code == 400):
		r.raise_for_status()

	elif r.status_code == 404:
		return dict({"error": "not found"})

	elif r.status_code == 401:
		return dict({"error": "not authorised"})

	elif r.status_code == 400:
		return dict({"error": "bad request"})

	else:
		return r.json()


def get_companyprofile(url_id: str, **kwargs) -> callable:
	"""
	func to extract companyprofile¹ resource from the API given a company number.
	:param url_id: uniquely identified code of the company.
	:param kwargs: it ensures that in the factory function Getter.extract(root_uid, start_index) we are
				   able to call get_companyprofile with the (unnecessary for this func) start_index argument (which is
				   otherwise necessary for all other functions).
	:return: call_api(), with url formatted to search company whose code is "comp_code".
	"""
	url = API_BASE_URL + "/company/" + url_id
	return call_api(url=url, api_key=KEY)


def get_company_resource(url_id: str, res_type: str, items_per_page: int, start_index: int) -> callable:
	"""
	func to customise the API request for a given company, used to create other functions for all possible "res_type".
	:param start_index: index used by the url for the pagination.
	:param url_id: uniquely identified code of the company.
	:param res_type: resource type, can chose from:
					 "officers", will return all officers of the company (no UID attributed by CH)²
					 "filing-history", will return all filings³.
					 "insolvency", will return insolvency information⁴.
					 "charges", will return charges⁵.
					 "persons-with-significant-control", will return all psc (no UID attributed by CH)⁶.
	:param items_per_page: max items per page to be returned (we could set it to any number, but want the max).
	:return: call_api(), with url formatted to search company whose code is root_uid and res_type is chosen from list.
	"""

	url = (API_BASE_URL 
	       + f"/company/{url_id}/{res_type}?items_per_page={items_per_page}&start_index={str(start_index)}")
	return call_api(url=url, api_key=KEY)


def get_appointmentlist(url_id: str, items_per_page: int, start_index: int) -> callable:
	"""
	func to query the API for appointmentList⁸ resource (being all appointments of one officer).
	:param items_per_page: max items per page to be returned (we could set it to any number, but want the max).
	:param start_index: index used by the url for the pagination.
	:param url_id: string, needed to create url to get all appointments from API.
	:return: call_api(), with url formatted to search officers appointments whose link is param appointments_link.
	"""
	# what we are building to:
	# https://api.companieshouse.gov.uk/{root_uid}/?items_per_page=1&start_index=1
	# where a root_uid here is: "/officers/LsKBd0tzif0mocK0gTSiK5WXmuA/appointments"

	url = (API_BASE_URL
	       + f"{url_id}?items_per_page={str(items_per_page)}&start_index={str(start_index)}")
	return call_api(url=url, api_key=KEY)


def get_officersearch(url_id: str, items_per_page: int, start_index: int) -> callable:
	"""
	func to get total results returned in the officerSearch resource⁹.
	:param url_id: string for the officer search query.
	:param items_per_page: max items per page to be returned (we could set it to any number, but want the max).
	:param start_index: index used by the url for the pagination.
						Be aware that if you try to extract more than the first 900 matches, you will get HTTP 416⁷.
	:return: call_api with URL customised to search for a certain officer.
	"""
	url = (API_BASE_URL
	       + f"/search/officers?q={url_id}&items_per_page={str(items_per_page)}&start_index={str(start_index)}")
	return call_api(url=url, api_key=KEY)


# Resources JSON examples and discussion from the CH developer forum


# ¹ https://developer.companieshouse.gov.uk/api/docs/company/company_number/companyProfile-resource.html
# ² https://developer.companieshouse.gov.uk/api/docs/company/company_number/officers/officerList-resource.html
# ³ https://developer.companieshouse.gov.uk/api/docs/company/company_number/filing-history/filingHistoryList-resource.html
# ⁴ https://developer.companieshouse.gov.uk/api/docs/company/company_number/insolvency/companyInsolvency-resource.html
# ⁵ https://developer.companieshouse.gov.uk/api/docs/company/company_number/charges/chargeList-resource.html
# ⁶ https://developer.companieshouse.gov.uk/api/docs/company/company_number/persons-with-significant-control/listPersonsWithSignificantControl.html
# ⁷ https://forum.aws.chdev.org/t/search-company-officers-returns-http-416-when-start-index-over-300/897/4
# ⁸ https://developer.companieshouse.gov.uk/api/docs/officers/officer_id/appointments/appointmentList-resource.html
# ⁹ https://developer.companieshouse.gov.uk/api/docs/search-overview/OfficerSearch-resource.html
