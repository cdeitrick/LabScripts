""" Removes fasta sequences that fall under a defined threshold."""
import argparse
from pathlib import Path

from Bio import SeqIO


def remove_contigs(input_filename: Path, output_filename: Path, cutoff: int = 1000):
	contigs = SeqIO.parse(input_filename, "fasta")
	approved_contigs = [i for i in contigs if len(i.seq) > cutoff]
	SeqIO.write(approved_contigs, output_filename, "fasta")


def create_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-i", "--input",
		help = "Input Filename",
		type = Path,
		dest = "input_filename"
	)
	parser.add_argument(
		"-o", "--output",
		help = "Output Filename",
		type = Path,
		dest = "output_filename"
	)
	parser.add_argument(
		"--cutoff",
		help = "The minimum length of each output contig.",
		type = int,
		default = 1000,
		dest = "cutoff"
	)
	return parser


if __name__ == "__main__":
	parser = create_parser()
	args = parser.parse_args()
	remove_contigs(args.input_filename, args.output_filename, args.cutoff)
