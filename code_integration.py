import subprocess
import os

def read_in_snippet(filename):  #reads in C source snippet
	result = []
	with open(filename,"r") as f:
		data = f.read()
	if data.find("includes_start") == -1:
		result.append(-1)
	else:	#gets every custom include and puts them in a list
		start_include = data.find("includes_start") + len("includes_start") + 1
		end_include = data.find("includes_end") - 1
		include_section = data[start_include:end_include].split("\n")
		result.append(include_section)
	
	if data.find("code_main_start") == -1:
		result.append(-1)
	else:	#gets custom code that has to be in the main function
		start_main = data.find("code_main_start") + len("code_main_start") + 1
		end_main = data.find("code_main_end")
		main_section = data[start_main:end_main]
		result.append(main_section)
		
	if data.find("code_function_start") == -1:
		result.append(-1)
	else:	#gets custom code that is outside the main function
		start_function = data.find("code_function_start") + len("code_function_start") + 1
		end_function = data.find("code_function_end")
		function_section = data[start_function:end_function]
		result.append(function_section)
	
	return result
	

def find_last_include(data):	#find first index after last include in source file to append includes there
	current_index = 0
	if data.find("//end custom includes") != -1:
		return data.find("//end custom includes") + len("//end custom includes") + 1
	else:
		while(True):
			if data.find("#include") == -1:
				return current_index
			else:
				include_index = data.find("#include")
				current_index += include_index + data[include_index:].find("\n") + 1
				data = data[current_index:]
				
	
def write_include(data,include_index,includes):	#checks if an include is already in the source file, if not writes it to the calculated index
	for include in includes:
		if data.find(include) == -1 or include == "//end custom includes" or include == "//custom includes by ANTIANAPY":
			data = data[0:include_index] + include + "\n" + data[include_index:]
			include_index += len(include) + 1
	return data
	

def find_main(data):	#returns first line inside the main function
	main_index = data.find("main")
	if main_index == -1:
		print("main function not found, are you applying this on your main file?")
		return -1
	else:
		return main_index + data[main_index:].find("{\n") + 2	


def write_main(data,main_index,code):	#writes code inside main function
	data = data[0:main_index] + code + data[main_index:]
	return data
	

def find_function(data):	#find first line above main function
	main_index = data.find("main")
	section = data[:main_index:]
	negative_offset = section[::-1].find("\n")
	return main_index - negative_offset


def write_function(data,function_index,code):	#writes code outside of main function
	data = data[0:function_index] + code + data[function_index:]	
	return data
	
	
def replace_value(data,value):	#replace #VALUE with a calculated value, this is needed for timing check
	data = data.replace("#VALUE",value)
	return data
	
def measure_time(filename):	#measures execution time of compiled program, time has to be below 1 minute and program can't be interactive
	compile_command = "gcc -o antianapy_tmp " + filename
	os.system(compile_command)
	
	time_output = subprocess.check_output(["/usr/bin/time","./antianapy_tmp"],stderr=subprocess.STDOUT).decode()	#calls time to measure execution time of executable
	elapsed_index = time_output.find("elapsed")	#parse output to get minutes and seconds
	section = time_output[:elapsed_index]
	negative_offset = section[::-1].find(" ")
	time = time_output[elapsed_index-negative_offset:elapsed_index]
	
	minutes = int(time.split(":")[0])
	if minutes > 0 :
		print("Program takes too long, time cannot be measured precisely enough")
		seconds = -1
	else:
		seconds = int(time.split(":")[1].split(".")[0]) + 2
	os.system("rm antianapy_tmp")
	return seconds

def write_snippet(data, snippet_name,value=""):	#write selected code snippet (includes, main section, function section) to C source file
	snippet = read_in_snippet(snippet_name)
		
	if snippet[0] != -1:	#if snippet has includes
		include_index = find_last_include(data)
		data = write_include(data,include_index,snippet[0])
	
	if snippet[1] != -1:	#if snippet has main section
		main_index = find_main(data)
		data = write_main(data,main_index,snippet[1])
	
	if snippet[2] != -1:	#if snippet has function section
		function_index = find_function(data)
		data = write_function(data,function_index, snippet[2])
	if value != "":	#if there's a value to replace
		data = replace_value(data,value)
	
	return data
		

def implement_timecheck(data,input_file,interactive=True):	#implements time check snippet
	print("---------Implementing time check---------")
	print("The timecheck functionality doesn't protect against every debugger. Some might ignore the kill signal sent by the timechecking thread")
	print("You can only use this functionality if your program is non-interactive and has a constant runtime")
	if (not interactive or input("Do you want to continue? (y or n) ").lower() == "y"):
		if(not interactive or input("Do you want ANTIANAPY to determine the runtime of your program automatically? (y or n) ").lower() == "y"):
			seconds = measure_time(input_file)
			if seconds != -1:
				if(not interactive or input("Do you want to hide the code in the .init section? (y or n) ").lower() == "y"):
					return write_snippet(data, "snippets/init_timecheck.c", str(seconds))
				else:
					return write_snippet(data, "snippets/timecheck.c", str(seconds))
			else:
				return data
		else:
			print("Please replace #VALUE in the generated code with the number of seconds you want the code to be able to run")
			
			if(input("Do you want to hide the code in the .init section? (y or n) ").lower() == "y"):
				return write_snippet(data, "snippets/init_timecheck.c")
			else:
				return write_snippet(data, "snippets/timecheck.c")
	else:
		return data
		
def implement_ptrace(data, interactive=True):	#implements trace check snippet
	print("--------Implenting tracing check--------")
	if(not interactive or input("Do you want to hide the code in the .init section? (y or n) ").lower() == "y"):
		return write_snippet(data ,"snippets/init_ptrace.c")
	else:
		return write_snippet(data, "snippets/ptrace.c")
		
def implement_breakpoint(data, interactive=True): #implements breakpoint check
	print("------Implementing breakpoint check------")
	print("The breakpoint check only checks if a breakpoint has been set in the main function")
	print("This code can still produce false postives if you use some values whose hexadecimal representation contains 0xcc")
	print("Always test your compiled code and check if it runs correctly")
	if (not interactive or input("Do you want to continue? (y or n) ").lower() == "y"):
		if(not interactive or input("Do you want to hide the code in the .init section? (y or n) ").lower() == "y"):
			return write_snippet(data, "snippets/init_breakpointcheck.c")
		else:
			return write_snippet(data, "snippets/breakpointcheck.c")
	else:
		return data
