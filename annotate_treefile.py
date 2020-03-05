from typing import List, Dict
from pathlib import Path
import pandas
import pendulum
from pprint import pprint
def load_annotations(filename:Path, key_column:str):
	table = pandas.read_excel(filename)

	data = dict()
	for index, row in table.iterrows():
		key = row[key_column]
		try:
			patientid = int(row['PatientID'])
		except:
			continue
		sample = row['group #']
		date = row["CultureDate"]
		try:
			date: pendulum.DateTime = pendulum.parse(str(date))
			date = date.to_date_string()
		except:
			date = ""
		string = f"{patientid}-{sample}-{date}"

		data[key] = string
		data[row['groupId']] = string
	return data

def apply_annotations(treefile:Path, annotations:Dict[str,str]):
	contents = treefile.read_text()
	for key, value in annotations.items():
		contents = contents.replace(key, value)
	treefile.with_suffix('.annotated.treefile').write_text(contents)

if __name__ == "__main__":
	treefile = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/projects/lipuma/sibling_pair_a/SC1360 phylogeny/K2P+ASC+R2/breseq.snp.fasta.treefile")
	annotation_file = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/projects/lipuma/docs/merged_table.xlsx")

	annotations = load_annotations(annotation_file, 'group #')
	pprint(annotations)
	apply_annotations(treefile, annotations)