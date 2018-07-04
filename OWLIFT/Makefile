CC = g++ -std=c++11
LIBS = `pkg-config --libs opencv`  -lowlift -lpthread
FLAGS = `pkg-config --cflags opencv`

all: saveTemp2

clean:

saveTemp2: OWLIFT_SaveTemp_ver2.o
	$(CC) -o $@  OWLIFT_SaveTemp_ver2.o $(LIBS)

%.o: %.cpp
	$(CC) $(FLAGS) -c -o $@ $<
