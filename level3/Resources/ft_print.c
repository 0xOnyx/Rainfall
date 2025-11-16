#include <stdio.h>

int main() {
	int a = 0;
	printf("1 %1$n %2$d\n", &a, a);
	printf("%1$d\n", a);
	return (0);
}
