#!/usr/bin/python3

import code_integration
import argparse

parser = argparse.ArgumentParser(description="ANTIANAPY - Generates code to make a debugger's life harder")
parser.add_argument('inputfile', metavar='input_source', type=str, help='Name of the input source file')
parser.add_argument('outputfile', metavar='output_source', default='default', type=str, nargs='?', help='Name of the output source file')
parser.add_argument('--time', dest='timecheck', action='store_true', help='Implement a time check that stops the program if it runs too long i.e. in a debugging session')
parser.add_argument('--trace', dest='tracecheck', action='store_true', help='Implement a check if the program is being traced i.e. debugged')
parser.add_argument('--breakpoint', dest='breakpointcheck', action='store_true', help='Implement a check that looks for breakpoints in the main function')

args = parser.parse_args()


if not args.timecheck and not args.tracecheck and not args.breakpointcheck:
	print("Please specify something to do, take a look at the help section with -h")
else:
	if args.outputfile == 'default':
		output_file = args.inputfile.split(".c")[0] + "_antianapy.c"
	else:
		output_file = args.outputfile
	with open(args.inputfile,"r") as f:
		data = f.read()
	if args.timecheck:
		data = code_integration.implement_timecheck(data,args.inputfile)
	if args.tracecheck:
		data = code_integration.implement_ptrace(data)
	if args.breakpointcheck:
		data = code_integration.implement_breakpoint(data)
	with open(output_file,"w") as f:
		f.write(data)


