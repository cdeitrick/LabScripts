import pandas
from pathlib import Path
from typing import Iterable, Callable, List, Dict
import datetime

def get_sample_id(path: Path):
	sample_id = path.parent.name
	return sample_id


def get_project_name(path: Path):
	try:
		project_name = path.parts[4]
	except IndexError:
		project_name = "Unknown"
	return project_name


def groupby(iterable: Iterable, by: Callable):
	groups = dict()
	for i in iterable:
		key = by(i)
		if key not in groups:
			groups[key] = [i]
		else:
			groups[key].append(i)
	return groups

def extract_date(path:Path)->datetime.date:
	for part in path.parts[::-1]:
		match = part.isdigit()
		if match:
			year = part[-2:]
			month = part[2:-2]
			day = part[:2]
			result = datetime.date(year = int(year), month = int(month), day = int(day))
			return result

def extract_date_from_sample_id(sample_id:str)->datetime.date:
	if not isinstance(sample_id, str): return None
	string = sample_id.split('_')[0]
	month = int(string[:2])
	day = int(string[2:4])
	year = 2000+int(string[4:])
	print((year, month, day))
	return datetime.date(year = year, month = month, day = day)

def search_for_sample_sheets(folder:Path, index = 0)->List[Path]:
	sample_sheets = list()
	if index > 3: return sample_sheets
	for path in folder.iterdir():
		if path.is_dir():
			sample_sheets += search_for_sample_sheets(path, index + 1)
		elif path.suffix == '.csv':
			sample_sheets.append(path)
	return sample_sheets

class SequenceScraper:
	def __init__(self, config_path: Path, dmux_path: Path):
		"""
		Parameters
		----------
		config_path:Path
			The folder containing all SampleSheets.
		dmux_path:Path
			The dmux folder.
		"""
		self.config_path = config_path
		self.dmux_path = dmux_path

		self.sample_sheets = self.generate_combined_sample_sheet()
		sample_map = self.collect_sample_files()
		self.match_files_to_project(self.sample_sheets, sample_map)
		self.to_excel(Path(__file__).with_name('billing.xlsx'))

	def collect_sample_files(self) -> Dict[str, List[Path]]:
		filenames = list()

		for filename in self.dmux_path.glob("**/*"):
			if filename.suffix != '.gz': continue
			if not filename.is_file(): continue
			filenames.append(filename)

		sample_map = groupby(filenames, get_sample_id)
		return sample_map

	def match_files_to_project(self, table: pandas.DataFrame, sample_map: Dict[str, List[Path]]):
		projects = table.groupby(by = 'projectName')

		project_list = list()
		sample_list = list()
		sample_file_list = list()
		for project_name, project_table in projects:
			print("Searching for files associated with {}...".format(project_name))
			project_sample_list = list()
			for index, sample in project_table.iterrows():
				sample_id = sample['sampleId']
				sample_name = sample['sampleName']
				sample_files = sample_map.get(sample_id, [])

				for f in sample_files:

					sample_file_row = {
						'sampleDate':  extract_date(f),
						'sampleId':    sample_id,
						'projectName': project_name,
						'sampleName':  sample_name,
						'filename':    str(f)
					}
					sample_file_list.append(sample_file_row)

				sample_row = {
					'sampleId':    sample_id,
					'sampleName':  sample_name,
					'projectName': project_name,
					'files':       len(sample_files)
				}
				project_sample_list.append(sample_row)

			expected_samples = len(project_table)
			found_samples = len(project_sample_list)
			missing_samples = expected_samples - found_samples

			project_row = {
				'projectName':     project_name,
				'expectedSamples': expected_samples,
				'foundSamples':    found_samples,
				'missingSamples':  missing_samples
			}
			sample_list += project_sample_list
			project_list.append(project_row)

		self.project_df = pandas.DataFrame(project_list)
		self.sample_df = pandas.DataFrame(sample_list)
		self.file_df = pandas.DataFrame(sample_file_list)

	def to_excel(self, filename: Path):

		filename = filename.with_suffix('.xlsx')
		filename = str(filename)
		writer = pandas.ExcelWriter(filename)

		include_index = False
		self.sample_sheets.to_excel(writer, 'fullList', index = include_index)
		self.project_df.to_excel(writer, 'projects', index = include_index)
		self.sample_df.to_excel(writer, 'samples', index = include_index)
		self.file_df.to_excel(writer, 'files', index = include_index)

		writer.close()

	def generate_combined_sample_sheet(self) -> pandas.DataFrame:
		pattern = "**/SampleSheet.csv"
		#pattern = "**/SampleSheet.csv"
		columns = {
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
		print("Searching for all sample sheets...")
		#config_sample_sheets = list(self.config_path.glob(pattern))
		config_sample_sheets = search_for_sample_sheets(self.config_path)
		print("Found {} sample sheets in config_folder.".format(len(config_sample_sheets)))
		#dmux_sample_sheets = list(self.dmux_path.glob(pattern))
		dmux_sample_sheets = search_for_sample_sheets(self.dmux_path)
		print("Found {} sample sheets in dmux folder.".format(len(dmux_sample_sheets)))
		all_sample_sheets = config_sample_sheets + dmux_sample_sheets
		print("Found {} total.".format(len(all_sample_sheets)))
		print("Combining all sample sheets...")
		billing_table = list()
		for i in all_sample_sheets:
			try:
				table = pandas.read_csv(str(i), skiprows = 9, sep = ',')
			except:
				continue
			for key, value in columns.items():
				if key in table.columns:
					table[value] = table[key]
					del table[key]

			billing_table.append(table)

		billing_table = pandas.concat(billing_table)
		billing_table['date'] = billing_table['sampleId'].apply(extract_date_from_sample_id)
		print("Found {} samples".format(len(billing_table)))
		#billing_table = billing_table.drop_duplicates(subset = 'sampleId', keep = 'first')
		billing_table = billing_table.drop_duplicates()
		print("Found {} samples after removing duplicate sampleIds.".format(len(billing_table)))
		output = Path(__file__).with_name("combined_sample_sheet.tsv")
		billing_table.to_csv(str(output), sep = "\t")

		return billing_table


if __name__ == "__main__":
	config_path = Path("/home/data/raw")
	dmux_folder = Path("/home/data/dmux")
	SequenceScraper(config_path, dmux_folder)
