objects = printer.o main.o
COMPILER=clang

edit: $(objects)
	$(COMPILER) -o main $(objects)
main.o: main.c
	$(COMPILER) -c main.c
printer.o: src/printer.c includes/printer.h
	$(COMPILER) -c src/printer.c
clean:
	rm main $(objects)
