#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// quick thought I had last night if we wanted to make the GUI in C
// we can make a C struct that handles all the logic of piecing together a string
// we can pass to the package manager of choice, then run the command using "system"
typedef struct installer_t {
  const char* package_manager;
  const char* arguments[BUFSIZ];
  const char* packages[BUFSIZ];
  int package_count, argument_count;
} installer_t;

installer_t* installer_t_constructor(const char* pkg_man, int arg_counter, const char* args[], int pkg_counter, const char* pkgs[]){
  installer_t* inst = (installer_t*)malloc(sizeof(installer_t));
  inst->package_manager = strdup(pkg_man);
  for(int i = 0; i < arg_counter; ++i){ inst->arguments[i] = strdup(args[i]); }
  for(int j = 0; j < pkg_counter; ++j){ inst->packages[j] = strdup(pkgs[j]); }
  inst->package_count = pkg_counter;
  inst->argument_count = arg_counter;
  return inst;
}

void installer_t_destructor(installer_t* inst){ free(inst); }
void print_installer_t_command(installer_t* inst){
  /*static char buffer[BUFSIZ];*/
  /*strcat(buffer, inst->package_manager);*/
  printf("%s ", inst->package_manager);
  for(int i = 0; i < inst->argument_count; ++i){
    printf("%s ", inst->arguments[i]);
  }
  for(int i = 0; i < inst->package_count; ++i){
    printf("%s ", inst->packages[i]);
  }
  printf("\n");
}



int main(){

  const char* arguments[] = {
    "install", "-y"
  };

  const char* packages[] = {
    "python", "clang", "spotify"
  };

  installer_t* inst = installer_t_constructor("apt-get", 2, arguments, 3, packages);
  print_installer_t_command(inst);
  installer_t_destructor(inst);
  /*int call = system("uname -a");*/
  /*printf("%d\n", call);*/
  return 0;
}
