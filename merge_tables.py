import argparse
from pathlib import Path

import pandas


def open_table(filename: Path, sheetname: str) -> pandas.DataFrame:
	if filename.suffix in ['.xlsx', 'xls']:
		table = pandas.read_excel(filename, sheet_name = sheetname)
	else:
		table = pandas.read_csv(filename)
	return table


def merge_tables(left_filename: Path, right_filename: Path, left_sheet: str, right_sheet: str, on: str)->pandas.DataFrame:
	left_table = open_table(left_filename, left_sheet)
	right_table = open_table(right_filename, right_sheet)

	if left_sheet != right_sheet:
		suffixes = ("_" + left_sheet, "_" + right_sheet)
	elif left_filename.name != right_filename.name:
		suffixes = ("_" + left_filename.name, "_" + right_filename.name)
	else:
		suffixes = ("_x", "_y")
	merged_table = left_table.merge(right_table, on = on, suffixes = suffixes)
	return merged_table


def create_parser(parameters = None):
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-l", "--left-filename",
		help = "The first spreadsheet to merge.",
		action = 'store',
		type = Path
	)
	parser.add_argument(
		"-r", "--right-filename",
		help = "The second spreadsheet to merge. Defaults to using the same spreadsheet file.",
		action = 'store',
		type = Path,
		default = None
	)
	parser.add_argument(
		'-1', '--left-sheetname',
		help = 'The name of the sheet in the first spreadsheet to use. Uses the first sheet if no sheet name is given.',
		default = 0,
		dest = "left_sheet"
	)
	parser.add_argument(
		"-2", "--right-sheetname",
		help = 'The name of the sheet in the second spreadsheet to use. Uses the first sheet if no sheet name is given.',
		default = 0,
		dest = 'right_sheet'
	)
	parser.add_argument(
		"-c", "--column",
		help = "The column to merge both tables on.",
		dest = 'column',
	)
	parser.add_argument(
		"-o", "--output",
		help = "The filename of the merged table.",
		dest = "output",
		type = Path
	)
	if parameters:
		parsed_args = parser.parse_args(parameters)
	else:
		parsed_args = parser.parse_args()

	if parsed_args.right_filename is None:
		parsed_args.right_filename = parsed_args.left_filename

	return parsed_args


if __name__ == "__main__":
	debug_args = ["-l", "/home/cld100/Downloads/RNA seq wrt WT(p_0.05).xlsx", "--right-sheetname", "A106P", "--column", "Gene_symbol"]
	args = create_parser(debug_args)

	# file:///home/cld100/Downloads/RNA seq wrt WT(p_0.05).xlsx
	print(args)
	merged_table = merge_tables(args.left_filename, args.right_filename, args.left_sheet, args.right_sheet, args.column)

	if args.output.suffix == '.xlsx':
		merged_table.to_excel(args.output)
	else:
		merged_table.to_csv(args.output)
