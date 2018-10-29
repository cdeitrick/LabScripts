
from pathlib import Path
import re
import pandas
from io import StringIO
from skbio import read
from skbio.tree import TreeNode
from random import randint
def generate_random_color()->str:
	r = randint(100, 255)
	g = randint(100, 255)
	b = randint(100, 255)

	color = f"#{r:>02X}{g:>02X}{b:>02X}"
	return color

def import_table(path: Path, sheetname = 0) -> pandas.DataFrame:
	if path.suffix in ['.xlsx', '.xls']:
		table = pandas.read_excel(path, sheet_name = sheetname)
	else:
		sep = '\t' if path.suffix in ['.tab', '.tsv'] else ","
		table = pandas.read_csv(path, sep = sep)
	return table

def annotate(tree_contents:str, table: pandas.DataFrame):
	colorby = 'Category'
	id_colormap = {
		273: "#1d91c0",
		653: "#225ea8",
		353: "#8c510a",
		326: "#bf812d",
		888: "#9970ab",
		1581: "#c2a5cf",
		62: "#f03b20",
		214: "#fd8d3c"
	}
	city_colormap = {
		'Philadelphia': "#fd8d3c",
		'Los Angeles': "#1d91c0",
		'Long Beach': "#225ea8",
		'Washington': "#8c510a"
	}
	from pprint import pprint

	itor_colors = list()
	for index, row in table.iterrows():
		sample_id = row['RepositoryNumber']
		category = row['Category']
		group = row['group #']
		source = row['BugSource:']
		city = row['City']

		pattern = f"{sample_id}_S[\d]+"

		if isinstance(category, str):
			color = None
			label = f"{sample_id}|{category}"
		else:
			color_id = row['PatientID']


			color = id_colormap.get(color_id)

			label = f"{sample_id}|{group}|{source}|{city}"
			color_range = f"{label}\trange\t{color}\t{color_id}"

		#color_line = f"{label}\tbranch\t{color}\tnormal\t1"

		tree_contents = re.sub(pattern, label, tree_contents)
		if color is not None:
			itor_colors.append(color_range)

	return tree_contents, itor_colors



if __name__ == "__main__":
	annotated_tree_filename = Path("/home/cld100/Documents/projects/lipuma/tree.annotated.nwk")
	tree_filename = Path("/home/cld100/Documents/projects/lipuma/tree.newick")
	table_filename = Path("/home/cld100/Documents/projects/lipuma/LiPuma-PHDC/merged_table.xlsx")
	table = pandas.read_excel(table_filename)

	contents = tree_filename.read_text()

	new_tree, itol = annotate(contents, table)

	tree_filename.with_suffix(".annotated.nwk").write_text(new_tree)

	itol_contents = "TREE_COLORS\nSEPARATOR TAB\nDATA\n"

	itol_filename = tree_filename.with_suffix(".colors.txt")
	itol_filename.write_text(itol_contents + "\n".join(itol))