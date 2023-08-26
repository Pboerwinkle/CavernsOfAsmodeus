def toSI(line):
	xDiff = line[2]-line[0]
	if xDiff == 0:
		xDiff = 0.000001

	slope = (line[3]-line[1])/xDiff
	yIntrcpt = slope*(line[0]*-1) + line[1]
	return slope, yIntrcpt

def intersect(line1, line2):
	x = (line2[1]-line1[1]) / (line1[0]-line2[0])
	y = line1[0]*x + line1[1]
	return x, y

def bisect(line):
	x = (line[0]+line[2])/2
	y = (line[1]+line[3])/2
	point = [x, y]

	slope = toSI(line)[0]

	if(slope == 0):
		slope -= 0.000001
	slope = (1/slope)*-1
	yIntercept = (slope*x*-1)+y
	return slope, yIntercept

def generate(width, height, S):
	# https://courses.cs.washington.edu/courses/cse326/00wi/projects/voronoi.html

	C = [
		((-width, -height), [
			[width/2, height/2, width/2, -10*height],
			[width/2, -10*height, -10*width, height/2],
			[-10*width, height/2, width/2, height/2]
		]),
		((2*width, -height), [
			[width/2, height/2, width/2, -10*height],
			[width/2, -10*height, 10*width, height/2],
			[10*width, height/2, width/2, height/2]
		]),
		((2*width, 2*height), [
			[width/2, height/2, 10*width, height/2],
			[10*width, height/2, width/2, 10*height],
			[width/2, 10*height, width/2, height/2]
		]),
		((-width, 2*height), [
			[width/2, height/2, width/2, 10*height],
			[width/2, 10*height, -10*width, height/2],
			[-10*width, height/2, width/2, height/2]
		]),
	]

	for site in S:
		cell = (site, [])
		for c in C:
			pb = bisect((site[0], site[1], c[0][0], c[0][1]))
			pbFunc = lambda x : pb[0]*x + pb[1]
			X = []
			sign = site[1] < pbFunc(site[0])
			toDelete = []
			for e in c[1]:
				first = e[1] < pbFunc(e[0])
				second = e[3] < pbFunc(e[2])
				if sign == first == second:
					toDelete.append(e)
				if first != second:
					inter = intersect(pb, toSI(e))
					if first == sign:
						e[0] = inter[0]
						e[1] = inter[1]
					else:
						e[2] = inter[0]
						e[3] = inter[1]
					X.append(inter)
			if X:
				newE = X[0] + X[1]
				c[1].append(list(newE))
				cell[1].append(list(newE))
			for e in toDelete:
				c[1].remove(e)
		C.append(cell)
	return C

import random
import math

#DENSITY = 0.1 # doesn't do anything if MAP is False
#COUNT =  500
#SCREEN_SIZE = (800, 800)

def getPair(match):
	if match % 2 == 0:
		matchPair = match+1
	else:
		matchPair = match-1
	return matchPair

def compPnts(pnt1, pnt2):
	if abs(pnt1[0] - pnt2[0])<1 and abs(pnt1[1] - pnt2[1])<1:
		return True
	else:
		return False

def genMap(DENSITY, COUNT, SCREEN_SIZE):
	sites = []
	for i in range(COUNT):
		sites.append((random.randint(0,SCREEN_SIZE[0]), (random.randint(0,SCREEN_SIZE[1]))))

	cells = generate(SCREEN_SIZE[0], SCREEN_SIZE[1], sites)

	inBounds = lambda x,y : x > 0 and y > 0 and x < SCREEN_SIZE[0] and y < SCREEN_SIZE[1]
	edges = []
	indexEdges = []
	usedCells = []
	allPoints = []
	currentIndex = 0
	for cell in cells:
		wall = random.random() < DENSITY
		if not wall:
			for edge in cell[1]:
				if not (inBounds(edge[0], edge[1]) and inBounds(edge[2], edge[3])):
					wall = True
					break
		if wall:
			cellPoints = []
			indexCellPoints = []
			for i, edge in enumerate(cell[1]):
				edge = list(round(x, 4) for x in edge)
				if edge[0]-edge[2] == 0:
					edge[0] -= 0.001
				indexedEdge = [currentIndex, currentIndex+1]
				if edge in edges:
					iToRemove = edges.index(edge)
					edges.remove(edge)
					indexEdges.pop(iToRemove)
				else:
					edges.append(edge)
					indexEdges.append(indexedEdge)
				cellPoints.extend((edge[:2], edge[2:]))
				indexCellPoints.extend((currentIndex, currentIndex+1))
				currentIndex += 2

			indexedCell = []
			indexedCell.extend((indexCellPoints[0], indexCellPoints[1]))
			arrangedCell = []
			arrangedCell.extend((cellPoints[0], cellPoints[1]))
			currentPnt = 1
			while len(cell[1])>len(arrangedCell):
				gotMatch = False
				for i in range(len(cellPoints)):
					if compPnts(cellPoints[i], arrangedCell[-1]) and i != currentPnt:
						repeat = False
						for point in arrangedCell:
							if compPnts(cellPoints[getPair(i)], point):
								repeat = True
						if repeat:
							continue
						match = i
						gotMatch = True
				if gotMatch:
					matchPair = getPair(match)
					arrangedCell.append(cellPoints[matchPair])
					indexedCell.append(indexCellPoints[matchPair])
					currentPnt = matchPair
				else:
					break

			usedCells.append(indexedCell)
			#usedCells.append(arrangedCell)
			allPoints.extend(cellPoints)

	return {"all points": allPoints, "edges": indexEdges, "cells": usedCells}
