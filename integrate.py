def read_in_snippet(filename):
	with open(filename,"r") as f:
		data = f.read()
	start_include = data.find("includes_start") + len("includes_start") + 1
	end_include = data.find("includes_end") - 1
	include_section = data[start_include:end_include].split("\n")
	
	start_code = data.find("code_main_start") + len("code_main_start") + 1
	end_code = data.find("code_main_end")
	code_section = data[start_code:end_code]
	return (include_section,code_section)
	

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
	

def write_snippet(filename, snippet_name, output_filename):
	snippet = read_in_snippet(snippet_name)
	with open(filename,"r") as f:
		data = f.read()
	include_index = find_last_include(data)
	data = write_include(data,include_index,snippet[0])
	
	main_index = find_main(data)
	data = write_main(data,main_index,snippet[1])
	
	with open(output_filename,"w") as f:
		f.write(data)	
		

write_snippet("test.c","ptrace.c","output_ptrace.c")
write_snippet("test.c","timecheck.c","output_time.c")


