import sys

# For printing to stderr. Use to print anything you don't want in output.
def eprint(string):
	sys.stderr.write(string+'\n')
	sys.stderr.flush()

