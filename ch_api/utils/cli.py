import argparse

parser = argparse.ArgumentParser(prog='prog.py')

parser.add_argument('file', help='path to csv file containing the url ids to be queried.')
parser.add_argument('--psc', help='add --psc flag to get companyprofile', action="store_true")
parser.add_argument('--ol', help='add --ol flag to get companyprofile', action="store_true")
parser.add_argument('--cp', help='add --cp flag to get companyprofile', action="store_true")
parser.add_argument('--al', help='add --al flag to get appointmentslist', action="store_true")
parser.add_argument('--excel', help='add --excel flag to dump data automatically to excel files.', action="store_true")


def file_is_csv_or_txt(args):
    if args.file.endswith(("csv", "txt")):
        return True


def optional_flags_collide(args):

    # bool(file) + bool(al) = 2
    if (args.al is True and args.excel is not True) and (sum([bool(value) for value in vars(args).values()]) > 2):
        return True
    # bool(file) + bool(al) + bool(excel) = 3
    elif (args.al is True and args.excel is True) and (sum([bool(value) for value in vars(args).values()]) > 3):
        return True


def data_wont_fit_excel(args, url_ids):
    if (args.excel is True) and len(url_ids) > 1048576:
        return True


def file_contains_company_codes(url_ids):
    if len(list(url_ids)[0]) == 8:
        return True
    return False

url_ids_examples = ("Example of root_uid for appointmentlist resource: /officers/RY_RJjPR0uGi0pOJuJi7dyCCTzo/appointments\n"
                    "Example of root_uid for psc, companyprofile and officerlist resources: OC399321\n\n")
