#CC = clang
CC = gcc
CFLAGS = -Wall -std=c99 -pedantic

all:  phylib

clean:  
	rm *.svg *.db

libphylib.so: phylib.o
	$(CC) -shared -o libphylib.so phylib.o -lm

phylib.o:  phylib.c phylib.h
	$(CC) $(CFLAGS) -fPIC -c phylib.c -o phylib.o

A1test1.o: A1test1.c phylib.h
	$(CC) $(CFLAGS) -fPIC -c A1test1.c -o A1test1.o

phylib_wrap.c phylib.py: phylib.i
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -c phylib_wrap.c -I/usr/include/python3.9/ -fPIC -o phylib_wrap.o

_phylib.so: phylib_wrap.o phylib.o A1test1.o
	$(CC) $(CFLAGS) -shared phylib_wrap.o phylib.o A1test1.o -o _phylib.so -L/usr/lib/python3.9 -L. -lpython3.9 -lphylib

phylib: A1test1.o libphylib.so _phylib.so
	$(CC) A1test1.o -L. -lphylib -o phylib -lm
