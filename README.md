# ANTIANAPY
ANTIANAPY adds small C code snippets to source files to hinder dynamic analysis efforts. These source files are added in a way as to not break existing code and nicely integrate into source files.

## INSTALLATION
ANTIANAPY doesn't require any external libraries. To use it, simply download this repository

## Usage
It's really easy to use ANTIANAPY. Have a look at the help section for precise information on the different flags that are available.
```
usage: ANTIANAPY.py [-h] [--time] [--trace] [--breakpoint] [--non-interactive]
                    input_source [output_source]

ANTIANAPY - Generates code to make a debugger's life harder

positional arguments:
  input_source       Name of the input source file
  output_source      Name of the output source file

optional arguments:
  -h, --help         show this help message and exit
  --time             Implement a time check that stops the program if it runs too long i.e. in
                     a debugging session
  --trace            Implement a check if the program is being traced i.e. debugged
  --breakpoint       Implement a check that looks for breakpoints in the main function
  --non-interactive  Use program in non-interactive mode
```
We will use the following C source file for demonstration purposes:
```C
#include <stdio.h>

int main()
{
	int x = 5;
	x += 3;
	printf("Test\n");
	printf("%d\n",x);
}
```
## Tracing check
The tracing check adds code to your source that checks if a program is being traced i.e. debugged. This code can be either called at the start of main or, if you want to  hide it better, before main in the .init section.
Here's the needed command:
```bash
./ANTIANAPY.py test.c --trace
```
And here's the code snippet that gets integrated:
```C
void check_traced()
{
	if (ptrace(PTRACE_TRACEME, 0) < 0) {
		printf("This process is being debugged!!!\n");
		exit(1);
	}
	return;
}
```
Basically, the check_traced function tries to attach itself as a debugger to the checked program. If any other program is already debugging our application, ptrace(PTRACE_TRACEME, 0) will return -1 because only a single process can attach to another process in Linux.
### strace
When running strace, we can see that the program detects that it's being debugged:
```
...
ptrace(PTRACE_TRACEME)                  = -1 EPERM (Operation not permitted)
fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(0x88, 0), ...}) = 0
brk(NULL)                               = 0x563f5bf67000
brk(0x563f5bf88000)                     = 0x563f5bf88000
write(1, "This process is being debugged!!"..., 34This process is being debugged!!!
) = 34
exit_group(1)                           = ?
...
```
### Bypassing the check
In order to bypass this check, a reverse engineer either has to jump over the call to the tracing check by changing the execution flow or patching the executable so that it jumps over the exit() block.
| complexity score | time score | impact score
|--|--|--|
| ★★★☆☆ | 20 minutes |★★★★☆
## Timing check
The timing check code measures the time of the executable in normal operation. It then adds code to your source that terminates the program after it has run for longer than it should. This check only works for non-interactive programs and programs that always take the same amount of time. Moreover, some debuggers ignore the kill signal sent by the timing thread so this check can be ineffective. The code can be called after main or hidden in the .init section. Here's the command to add this snippet:
```
./ANTIANAPY.py test.c --time
```
And here's the snippet that gets added:
```C
void *timing_check()
{
	sleep(#VALUE);
	kill(getpid(),SIGKILL);
}
...
pthread_t thread_id;
pthread_create(&thread_id, NULL, timing_check, NULL);
```
Basically, the snippet just starts a thread that first sleeps for the amount of time the program is supposed to take and then sends a kill signal to the process. If the process is currently being debugged and the reverse engineer is single stepping through the code, this thread will terminate the binary before the reverse engineer can further analyze what's happening.
### Bypassing the check
Bypassing this check can be hard as you need to probably patch code or stop the thread from starting. However, some debuggers are immune to kill signals sent by other threads and will just continue debugging. radare 2 is one of them.
| complexity score | time score | impact score
|--|--|--|
| ★★★★☆ | 20 minutes |★★☆☆☆
## Breakpoint check
The breakpoint check adds code to the source file that looks for a breakpoint in the main function. It can be called at the start of the main function or hidden in the .init section. This snippet can lead to issues in case some any values used in the main function contain a hex value of 0xcc. Always test your compiled code after adding these snippets
Here's the command to add this snippet:
```
./ANTIANAPY.py test.c --breakpoint
```
And here's the added snippet:
```C
bool check_for_specific_byte(unsigned char byte, void *memory, unsigned int size_of_memory)
{
	unsigned char* bytes = (unsigned char*)memory; 
	for (int i = 0; ; i++)
	{
		if (((size_of_memory > 0) && (i >= size_of_memory)) ||
			((size_of_memory == 0) && (bytes[i] == 0xC3)))
			break;

		if (bytes[i] == byte)
			return true;
	}
	return false;
}

void is_debugged()
{
	
	if (check_for_specific_byte(0xCC, &main,0))
	{
		printf("Stop debugging");
		exit(0);
	}
	return;
}
```
Basically, the call to is_debugged() checks if it can find the value 0xcc which is the hex representation of a breakpoint. If it does, it simply exits.
### radare 2
```shell
r2 -d a.out 
Process with PID 19852 started...
= attach 19852 19852
bin.baddr 0x55f4dd74a000
Using 0x55f4dd74a000
asm.bits 64
 -- This software comes with no brain included. Please use your own.
[0x7f8e55b75100]> aa
[x] Analyze all flags starting with sym. and entry0 (aa)
[0x7f8e55b75100]> db main
[0x7f8e55b75100]> dc
[0x7f8e55a4f2c6]> dc
child exited with status 0

==> Process finished

[0x7f8e55b75100]>
```
radare never stops at our set breakpoint because it doesn't reach it. The breakpoint check hidden in the .init section prematurily terminates the program.
### Bypassing the check
Bypassing this check is not that hard. The program only checks for breakpoints in the main function and only does it once. If you set any breakpoints beyond the main function or just after the breakpoint check function, you'll be able to set breakpoints anywhere you want again.
| complexity score | time score | impact score
|--|--|--|
| ★★★☆☆ | 10 minutes |★★☆☆☆
## Extension
Several code snippets can be added to this project, such as hardware breakpoint checks, memory breakpoint checks and so on. It's also fairly easy to extend this program, because all you need to do is add the C code snippets..
## Sources
The C code snippets have been inspired by the snippets made by Checkpoint Research. You can find their work on Anti-Debug techniques on [https://anti-debug.checkpoint.com/](https://anti-debug.checkpoint.com/).
