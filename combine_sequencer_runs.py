from pathlib import Path
import subprocess
import itertools
def concatenate_files(left:Path, right:Path, output:Path):
	command = f"cat {left} {right} > {output}"
	subprocess.call(command)

def combine_sequence_runs(folder_a:Path, folder_b:Path, output_folder:Path):
	files_a = list(folder_a.glob("**/*.gz"))
	print(f"Found {len(files_a)} in {folder_a}")
	files_b = list(folder_b.glob("**/*.gz"))
	print(f"Found {len(files_b)} in {folder_b}")
	files = files_a + files_b

	file_map = dict()
	for filename in files:
		name = filename.name
		if name in file_map:
			file_map[name].append(filename)
		else:
			file_map[name] = [filename]

	assert all(len(v)==2 for v in file_map.values())
	print(f"Found {len(file_map)} files.")
	for name, paths in file_map.items():
		path_a, path_b = paths
		rsubpath = itertools.takewhile(lambda s: s not in [folder_a.name, folder_b.name], path_a.parts[::-1])
		new_path = output_folder.joinpath(*list(rsubpath)[::-1])
		print(new_path)
		print("\t", path_a)
		print("\t", path_b)
		concatenate_files(path_a, path_b, new_path)

if __name__ == "__main__":
	dmux_folder = Path("/home/dmux")
	_folder_a = dmux_folder / "181018"
	_folder_b = dmux_folder / "181020"
	_output_folder = dmux_folder / "181018B"
	if not _output_folder.exists():
		_output_folder.mkdir()
	combine_sequence_runs(_folder_a, _folder_b, _output_folder)