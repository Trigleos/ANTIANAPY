import subprocess
import os

def read_in_snippet(filename):
	result = []
	with open(filename,"r") as f:
		data = f.read()
	if data.find("includes_start") == -1:
		result.append(-1)
	else:
		start_include = data.find("includes_start") + len("includes_start") + 1
		end_include = data.find("includes_end") - 1
		include_section = data[start_include:end_include].split("\n")
		result.append(include_section)
	
	if data.find("code_main_start") == -1:
		result.append(-1)
	else:
		start_main = data.find("code_main_start") + len("code_main_start") + 1
		end_main = data.find("code_main_end")
		main_section = data[start_main:end_main]
		result.append(main_section)
		
	if data.find("code_function_start") == -1:
		result.append(-1)
	else:
		start_function = data.find("code_function_start") + len("code_function_start") + 1
		end_function = data.find("code_function_end")
		function_section = data[start_function:end_function]
		result.append(function_section)
	
	return result
	

def find_last_include(data):
	current_index = 0
	while(True):
		if data.find("#include") == -1:
			return current_index
		else:
			include_index = data.find("#include")
			current_index += include_index + data[include_index:].find("\n") + 1
			data = data[current_index:]
				
	
def write_include(data,include_index,includes):
	for include in includes:
		if data.find(include) == -1:
			data = data[0:include_index] + include + "\n" + data[include_index:]
			include_index += len(include) + 1
	return data
	

def find_main(data):
	main_index = data.find("main")
	if main_index == -1:
		print("main function not found, are you applying this on your main file?")
		return -1
	else:
		return main_index + data[main_index:].find("{\n") + 2	


def write_main(data,main_index,code):
	data = data[0:main_index] + code + data[main_index:]
	return data
	

def find_function(data):
	main_index = data.find("main")
	section = data[:main_index:]
	negative_offset = section[::-1].find("\n")
	return main_index - negative_offset


def write_function(data,function_index,code):
	data = data[0:function_index] + code + data[function_index:]	
	return data
	
	
def replace_value(data,value):
	data = data.replace("#VALUE",value)
	return data
	
def measure_time(filename):
	compile_command = "gcc -o antianapy_tmp " + filename
	os.system(compile_command)
	
	time_output = subprocess.check_output(["/usr/bin/time","./antianapy_tmp"],stderr=subprocess.STDOUT).decode()
	elapsed_index = time_output.find("elapsed")
	section = time_output[:elapsed_index]
	negative_offset = section[::-1].find(" ")
	time = time_output[elapsed_index-negative_offset:elapsed_index]
	
	minutes = int(time.split(":")[0])
	if minutes > 0 :
		print("Program takes too long, time cannot be measured reasonably")
		seconds = -1
	else:
		seconds = int(time.split(":")[1].split(".")[0])+1
	os.system("rm antianapy_tmp")
	return seconds

def write_snippet(filename, snippet_name, output_filename,value=""):
	snippet = read_in_snippet(snippet_name)
	with open(filename,"r") as f:
		data = f.read()
		
	if snippet[0] != -1:
		include_index = find_last_include(data)
		data = write_include(data,include_index,snippet[0])
	
	if snippet[1] != -1:
		main_index = find_main(data)
		data = write_main(data,main_index,snippet[1])
	
	if snippet[2] != -1:
		function_index = find_function(data)
		data = write_function(data,function_index, snippet[2])
		
	data = replace_value(data,value)
	
	with open(output_filename,"w") as f:
		f.write(data)	
		

write_snippet("test.c","ptrace.c","output_ptrace.c")
seconds = measure_time("test.c")
write_snippet("test.c","timecheck.c","output_time.c",str(seconds))
write_snippet("test.c","breakpointcheck.c","output_breakpoint.c")
write_snippet("test.c","init_breakpointcheck.c","output_init_breakpoint.c")
write_snippet("test.c","init_ptrace.c","output_init_ptrace.c")


