CC=gcc

.DEFAULT_GOAL := all
.PHONY: all clean

all: libloop.so loop

clean:
	rm *.o libloop.so loop

libloop.so: loop.o
	$(CC) -shared -o $@ $^

loop: loop.o
	$(CC) -o $@ $^

%.o: %.c
	$(CC) -fPIC -c -o $@ $<

