all: taskData.o
	g++ -std=c++20 core.cpp taskData.o timespec_functions.o -o core

taskData.o: timespec_functions.o taskData.cpp
	g++ -std=c++20 -c taskData.cpp

timespec_functions.o: timespec_functions.cpp
	g++ -std=c++20 -c timespec_functions.cpp

clean:
	rm *.o core