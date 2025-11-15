# include <stdio.h>
# include <unistd.h>
# include <string.h>

void p(char *user_input_buf, char *dash){
    char *c_ptr;
    char read_buffer [4104];

    puts(dash);
    read(0, read_buffer, 4096);
    c_ptr = strchr(read_buffer, L'\n');
    *c_ptr = '\0';
    strncpy(user_input_buf, read_buffer, 20);
    return;
}

void pp(char *global_buffer){

    char local_buffer_1 [20];
    char local_buffer_2 [20];
    char *dash = " - ";

    p(local_buffer_1, dash);
    p(local_buffer_2, dash);
    strcpy(global_buffer, local_buffer_1);

    size_t len = strlen(global_buffer);
    global_buffer[len] = ' ';
    global_buffer[len + 1] = '\0';
    strcat(global_buffer, local_buffer_2);
    return;
}

int main(void){
    char global_buffer [54];

    pp(global_buffer);
    puts(global_buffer);
    return 0;
}
