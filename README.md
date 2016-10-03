#AFMtoSTL
=========

##OVERVIEW:
This program takes data from Bruker AFM scans exported as an ASCII file and produces an ASCII STL file suitable for 3d printing. Certainly programs exist that can create STL formatted files from this type of data, but I have not found them to be able to produce files that are suitable for 3D printing. 

The main criterion from my view is that the slicing software doesn't complain, which seems to mean that you need not just some surface, but a model that has an inside and an outside, as in, it could hold water in it without leaking if it existed IRL.

The program reads the header of the ASCII file to determine X & Y dimensions of the file, but relies on user input to determine nm-per-sampling. The nm-per-sampling is determined based on the *original scan size* (in nm) and the *number of samplings-per-line*. This can't be retrieved reliably from the header. The number then can be acheived by dividing scan-size (in nm) by samples/line.


##UNDER DEVELOPMENT:

###Plan to add
Currently, the program does not compute the normal vectors and instead outputs 0 0 0. However, these can often be safely omitted. It has not, in my usage of the STL's, resulted in any problems with 3D printing.

###Problems
The program can only output ASCII STL files, which results in rather large files. I would like to add support for binary STL output, that is under development.