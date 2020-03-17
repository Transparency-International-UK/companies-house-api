#!/usr/bin/python3

from utils.api_functions import get_companyprofile, get_company_resource
from utils.api_functions import get_appointmentlist, get_officersearch

from functools import partial, wraps
from math import ceil


class Getter:
	"""class to extract any type of resource from CH api. Handles pagination and return full paginated object"""

	class _Decorators:
		"""private class for decorators to use in Getter"""

		@classmethod
		def paginate(cls, f):
			"""class method used to decorate Getter.extract method"""

			@wraps(f)
			def wrapper(*args):
				# intercept the Getter instance so we can access its arguments.
				self_ = args[0]
				pagination_cap = self_.pagination_cap

				# extract the resource, if needs pagination this will only be the first page, if it is a resource that
				# does not contain any list needing pagination, start_index will be ignored.
				curried_extractor = f(self_)
				res = curried_extractor(start_index=0)

				# check that resource contains a list AND this list needs pagination.
				if ("total_results" in res
					and "items_per_page" in res
					and (res.get("total_results") > res.get("items_per_page"))):

					total_results = res.get("total_results")
					items_per_page = res.get("items_per_page")
					total_pages = ceil(total_results / items_per_page)
					pages = []

					for start_index in range(0, items_per_page * total_pages, items_per_page):
						# ensure we never exceed the pagination limit imposed by the API for this specific resource.
						if pagination_cap is not None:
							if start_index < pagination_cap:
								page = curried_extractor(start_index=start_index)["items"]

						else:
							page = curried_extractor(start_index=start_index)["items"]

						pages.append(page)

					_ = list(map(res.get("items").extend, pages[1:]))  # we already have the 1st page in json["items"]

					return res, self_.json_params, self_.url_id
				else:
					return res, self_.json_params, self_.url_id

			return wrapper

	def __init__(self, json_params, url_id):
		self.json_params = json_params
		self.url_id = url_id
		self.resource_name = json_params.get("name")
		self.items_per_page = json_params.get("items_per_page", None)
		self.pagination_cap = (json_params.get("list_table_params").get("pagination_cap", None)
		                       if "list_table_param" in json_params else None)

	@_Decorators.paginate
	def extract(self):
		extractor = get_extractor(self.resource_name, self.items_per_page)

		# the last step of the function composition will happen in the decorator.
		return partial(extractor, url_id=self.url_id)


def get_extractor(name, items_per_page):
	if name == "companyprofile":
		return get_companyprofile

	elif name == "officerlist":
		curried_f = partial(get_company_resource, res_type="officers", items_per_page=items_per_page)
		return curried_f

	elif name == "filinghistorylist":
		curried_f = partial(get_company_resource, res_type="filing-history", items_per_page=items_per_page)
		return curried_f

	elif name == "companyinsolvency":
		curried_f = partial(get_company_resource, res_type="insolvency", items_per_page=items_per_page)
		return curried_f

	elif name == "chargeslist":
		curried_f = partial(get_company_resource, res_type="charges", items_per_page=items_per_page)
		return curried_f

	elif name == "psc":
		curried_f = partial(get_company_resource, res_type="persons-with-significant-control", items_per_page=items_per_page)
		return curried_f

	elif name == "appointmentlist":
		curried_f = partial(get_appointmentlist, items_per_page=items_per_page)
		return curried_f

	elif name == "officersearch":
		curried_f = partial(get_officersearch, items_per_page=items_per_page)
		return curried_f


if __name__ == '__main__':
	from pprint import pprint
	from utils.json_params import *

	# extract appointmentList (check pagination decorator triggered pagination for resource that needs it).
	extractor = Getter(appointmentlist_params, "FVzeHfaxEHWP31pW1BIDeqWX8bs")
	appLs = extractor.extract()
	# 288
	res, _, _ = appLs
	print(f"The length of the \"items\" array is {len(res['items'])}")
	# 288
	print(f"\"total_results\" key in extracted JSON is {res.get('total_results')}")
	# 288

	# extract companyprofile (check pagination decorator does not trigger pagination if not needed).

	extractor = Getter(companyprofile_params, "SC596614")
	basicP = extractor.extract()
	pprint(basicP)
