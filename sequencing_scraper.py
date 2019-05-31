import csv
import datetime
from pathlib import Path
from typing import List
import pandas
from loguru import logger
import datetime

COLUMNMAP = {
	'I5_Index_ID': 'i5IndexId',
	'I7_Index_ID': 'i7IndexId',
	'Index_ID':    'indexId',
	'Name':        'sampleName',
	'NucleicAcid': 'nucleicAcid',
	'Pop':         'pop',
	'Project':     'projectName',
	'SampleID':    'sampleId',
	'Sample_ID':   'sampleId',
	'Sample_Name': 'sampleName',
	'Sample_Well': 'sampleWell',
	'Species':     'species',
	'Well':        'sampleWell',
	'index':       'index',
	'index2':      'index2'
}


def extract_date_from_sample_id(sample_id: str) -> datetime.date:
	if not isinstance(sample_id, str): return None
	string = sample_id.split('_')[0]

	try:
		month = int(string[:2])
		day = int(string[2:4])
		year = 2000 + int(string[4:])
		result = datetime.date(year = year, month = month, day = day)
	except ValueError:
		result = None
	return result


def search_for_sample_sheets(folder: Path, index = 0) -> List[Path]:
	sample_sheets = list()
	if index > 3: return sample_sheets
	for path in folder.iterdir():
		if path.is_dir():
			sample_sheets += search_for_sample_sheets(path, index + 1)
		elif path.name == 'SampleSheet.csv':
			sample_sheets.append(path)
	return sample_sheets


def find_all_sample_sheets(*paths) -> List[Path]:
	""" Finds all sample sheets within the given folders. """
	sample_sheets = list()
	for path in paths:
		files = list(path.glob('**/*SampleSheet.csv'))
		logger.info(f"Found {len(files)} samplesheets in folder {path}")
		sample_sheets += files
	return sample_sheets


def combine_sample_sheets(filenames: List[Path]) -> pandas.DataFrame:
	""" Combines the individual samplesheets into a single DataFrame."""
	fieldnames = ['Sample_ID', 'Sample_Name', 'Species', 'Project', 'NucleicAcid', 'Sample_Well', 'I7_Index_ID', 'index', 'I5_Index_ID', 'index2']
	sample_sheets = list()
	for filename in filenames:
		with filename.open() as file1:
			reader = csv.DictReader(file1, fieldnames = fieldnames)
			for line in reader:
				# Find the header line, then break. The rest of the `reader` object should be the samples.
				if line['Sample_ID'] == 'Sample_ID':
					break
			# Consume the rest of the `reader` object.
			sample_sheets += list(reader)

	df = pandas.DataFrame(sample_sheets)
	if None in df.columns:
		# This happens when there are extra columns in the samplesheet.
		df.pop(None)
	logger.debug(f"{df.columns}")
	if len(df.columns) > len(fieldnames):
		df.to_csv('test.csv')
	df.columns = [COLUMNMAP[i] for i in df.columns]
	return df


def generate_combined_sample_sheet(path:Path=None, *paths) -> pandas.DataFrame:
	""" Generates a single samplesheet from all of the individual sample sheets.
		Parameters
		----------
		path: Path
			If a folder, the filename will be generated based on the date.
	"""

	logger.info("Searching for all sample sheets...")
	sample_sheets = find_all_sample_sheets(*paths)

	logger.info("Combining all sample sheets...")
	sample_sheet = combine_sample_sheets(sample_sheets)

	billing_table = sample_sheet
	logger.info(f"Found {len(billing_table)} samples")

	if billing_table.empty:
		logger.warning("The scraper did not find any samplesheets.")
	else:
		billing_table['date'] = billing_table['sampleId'].apply(extract_date_from_sample_id)
		billing_table = billing_table.drop_duplicates()
		logger.info(f"Found {len(billing_table)} samples after removing duplicate sampleIds.")
		current_date = datetime.datetime.now().date().isoformat()
		basename = f"combined_sample_sheet.{current_date}.tsv"
		if path:
			if path.is_dir():
				filename = path / basename
			else:
				filename = path
		else:
			filename = basename
		billing_table.to_csv(str(filename))

	return billing_table

def schedule_scraping():
	""" Runs the scraper every week to find new SampleSheets."""
	# Need to keep track of which samplesheets have already been processed.
	folder = Path(__file__).parent
	index_filename = folder / "samplesheet.index.txt"
	log_filename = folder / "log.txt"
	logger.add(log_filename)

	for i in range(10): # for debugging. replace with while loop in future.
		current_date = datetime.datetime.now()
		year, week, day = current_date.isocalendar()
		# Generate the name of the samplesheet based on which week it is.
		filename = folder / f"{year}-{week}.SampleSheet.csv"



if __name__ == "__main__":
	# config_path = Path("/home/data/raw")
	# dmux_folder = Path("/home/data/dmux")
	# table = generate_combined_sample_sheet(dmux_folder, config_path)
	generate_combined_sample_sheet(Path(__file__).parent / "ss")
