includes_start
//custom includes by ANTIANAPY
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
//When compiling with gcc, use the -pthread flag if on Ubuntu
//end custom includes
includes_end

code_function_start

//custom code generated by ANTIANAPY	
void *timing_check()
{
	sleep(#VALUE);
	kill(getpid(),SIGKILL);
}
//end custom code

code_function_end
	
code_main_start

	//custom code generated by ANTIANAPY	
	pthread_t thread_id;
	pthread_create(&thread_id, NULL, timing_check, NULL);
	//end custom code
	
code_main_end
