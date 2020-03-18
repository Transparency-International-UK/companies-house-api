# TODO turn into fully fledged unit test with assertions.

from pprint import pprint

from utils.json_getter import Getter
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
