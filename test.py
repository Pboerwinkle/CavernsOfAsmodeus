import math
import numpy

A = numpy.array([[[3, 5], [4, 2]], [[1, 4], [1, 6]]])
B = numpy.zeros(shape=(len(A), 2))
B[:,0] = (A[:,1,1]-A[:,0,1])/(A[:,1,0]-A[:,0,0])
B[:,1] = -B[:,0]*A[:,0,0]+A[:,0,1]
print(B)
print(type(B[1,0]))
print(B[1,0])
if B[1,0] > 10**100:
	print("yes")
