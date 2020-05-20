SHELL = bash

TARGET = example
CXXFILES = Main.cpp GroceryCheckout.cpp
HEADERS = GroceryCheckout.h
CXX = clang++
CFLAGS += -std=c++17

OBJS = $(CXXFILES:.cpp=.o)

default all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CFLAGS) -o $(TARGET) $(OBJS)

clean:
	rm *.o
scrubbed: clean
	rm $(TARGET)
