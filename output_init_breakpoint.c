#include <stdio.h>
//custom includes by ANTIANAPY
#include <stdlib.h>
#include <stdbool.h>
//end custom includes


//custom code generated by ANTIANAPY	
static void is_debugged() __attribute((constructor));

int main();


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

static void is_debugged()
{
	
	if (check_for_specific_byte(0xCC, &main,0))
	{
		printf("Stop debugging");
		exit(0);
	}
	return;
	
}
//end custom code

int main()
{
	int x = 5;
	x += 3;
	printf("Test\n");
	printf("%d\n",x);
}
