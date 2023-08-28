import math

def lineLineIntrsct(line1, line2):
	slpDiff = line1[0]-line2[0]
	if slpDiff == 0:
		return None

	x = (line2[1]-line1[1])/(line1[0]-line2[0])
	y = line1[0]*x+line1[1]
	return [x, y]

def getClosestPoint(line, point):
	if line[0] == 0:
		return [point[0], line[1]]
	else:
		slp = -1/line[0]
	yIntrcpt = slp * (-1*point[0]) + point[1]
	perpLine = [slp, yIntrcpt]

	intrsct = lineLineIntrsct(perpLine, line)
	return intrsct

def isOnLine(line, point):
	if point == None:
		return False
	if line[0][0] < line[1][0]:
		minX = line[0][0]
		maxX = line[1][0]
	else:
		minX = line[1][0]
		maxX = line[0][0]

	if point[0] >= minX and point[0] <= maxX:
		return True
	else:
		return False

def getSqrDist(pnt1, pnt2):
	return (pnt2[0]-pnt1[0])**2 + (pnt2[1]-pnt1[1])**2

def detectCollision(trjctryPP, trjctrySI, staticPP, staticSI, radius):
	CPTrjctry1 = getClosestPoint(staticSI, trjctryPP[0])
	TSintrsct = lineLineIntrsct(trjctrySI, staticSI)
	CPTrjctry2 = getClosestPoint(staticSI, trjctryPP[1])
	CPStatic1 = getClosestPoint(trjctrySI, staticPP[0])
	CPStatic2 = getClosestPoint(trjctrySI, staticPP[1])

	if ((isOnLine(trjctryPP, TSintrsct) and isOnLine(staticPP, TSintrsct))
	or (getSqrDist(CPTrjctry2, trjctryPP[1]) < radius**2 and isOnLine(staticPP, CPTrjctry2))
	or (getSqrDist(CPStatic1, staticPP[0]) < radius**2 and isOnLine(trjctryPP, CPStatic1))
	or (getSqrDist(CPStatic2, staticPP[1]) < radius**2 and isOnLine(trjctryPP, CPStatic2))
	or (getSqrDist(trjctryPP[1], staticPP[0]) < radius**2)
	or (getSqrDist(trjctryPP[1], staticPP[1]) < radius**2)):
		#print("intersection")
		distTrjctry1 = math.sqrt(getSqrDist(trjctryPP[0], CPTrjctry1))
		distConstant = radius/distTrjctry1
		x = (trjctryPP[0][0]-TSintrsct[0])*distConstant+TSintrsct[0]
		y = (trjctryPP[0][1]-TSintrsct[1])*distConstant+TSintrsct[1]
		intrsctCenter = [x, y]
		CPintrsctCent = getClosestPoint(staticSI, intrsctCenter)
		if isOnLine(staticPP, CPintrsctCent):
			return [x, y]
		else:
			if (getSqrDist(staticPP[1], trjctryPP[0]) < getSqrDist(staticPP[0], trjctryPP[0])):
				CPStatic1,CPStatic2 = CPStatic2,CPStatic1
				staticPP[0],staticPP[1] = staticPP[1],staticPP[0]
			dist1 = getSqrDist(CPStatic1, staticPP[0])
			dist2 = getSqrDist(CPStatic2, staticPP[1])
			if dist1 > radius**2:
				usedDist = dist2
				usedPnt = CPStatic2
			else:
				usedDist = dist1
				usedPnt = CPStatic1
			if usedDist > radius**2:
				print("distance from static end to trajectory too great!")
				return None
			distBack = math.sqrt(radius**2 - usedDist)
			strtToCP = math.sqrt(getSqrDist(trjctryPP[0], usedPnt))
			distConstant = distBack/strtToCP
			x = (trjctryPP[0][0]-usedPnt[0])*distConstant+usedPnt[0]
			y = (trjctryPP[0][1]-usedPnt[1])*distConstant+usedPnt[1]
			return [x, y]
	else:
		return None
