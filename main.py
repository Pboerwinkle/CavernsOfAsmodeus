import math
import random
import numpy

import pygame
import pygame.gfxdraw
pygame.init()

import circleLineCollision
import voronoiMapGen

screenSize = (800, 800)
halfScreen = (screenSize[0]/2, screenSize[1]/2)
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("Caverns of Asmodeus","Caverns of Asmodeus")
clock = pygame.time.Clock()
framerate = 60

mapSize = (800, 800)
mapData = voronoiMapGen.genMap(0.1, 500, mapSize)

allPoints = numpy.array(mapData["all points"])
mapData["slpIntrcptWalls"] = numpy.zeros(shape=(len(mapData["edges"]), 2))
walls = allPoints[mapData["edges"]]
mapData["slpIntrcptWalls"][:,0] = (walls[:,1,1]-walls[:,0,1])/(walls[:,1,0]-walls[:,0,0])
mapData["slpIntrcptWalls"][:,1] = -mapData["slpIntrcptWalls"][:,0]*walls[:,0,0]+walls[:,0,1]

newPoints = allPoints
def translate(d, points):
	transPoints = numpy.zeros(shape=(len(points), 2))
	transPoints[:,0] = points[:,0]+d[0]
	transPoints[:,1] = points[:,1]+d[1]
	return transPoints

def rotate(a, points):
	rotPoints = numpy.zeros(shape=(len(points), 2))
	rotPoints[:,0] = points[:,0]*math.cos(a) - points[:,1]*math.sin(a)
	rotPoints[:,1] = points[:,1]*math.cos(a) + points[:,0]*math.sin(a)
	return rotPoints

def dilate(m, points):
	dilPoints = numpy.zeros(shape=(len(points), 2))
	dilPoints = points*m
	return dilPoints

def magnify(e, points):
	magPoints = numpy.zeros(shape=(len(points), 2))
	magPoints[:,0] = points[:,0]*e
	magPoints[:,1] = points[:,1]*e
	return magPoints

def getEndPoint(angle, speed):
	x = speed*math.cos(angle)
	y = speed*math.sin(angle)
	return [x, y]

spriteSheet = pygame.image.load("assets/Sprites.png")
miniSheets = {
	"chassis": spriteSheet.subsurface([0, 0, 26, 28]),
	"sideTreads": spriteSheet.subsurface([0, 28, 36, 32])}
animStates = {"leftTread": [0, 3], "rightTread": [0, 3]}
playerConst = {"turnSpeed": 0.03, "speed": 1.5, "radius": 10, "camElev": 1.5, "zoomFactor": 2}
playerVars = {
	"chassisAngle": 0,
	"pos": list(halfScreen),
	"gunAngle": 0}

playerTracks = numpy.zeros((1000, 2, 2))

trackLeft = getEndPoint(playerVars["chassisAngle"]+math.pi/2, 8)
playerTracks[:, 0] = [playerVars["pos"][0]+trackLeft[0], playerVars["pos"][1]+trackLeft[1]]
trackRight = getEndPoint(playerVars["chassisAngle"]-math.pi/2, 8)
playerTracks[:, 1] = [playerVars["pos"][0]+trackRight[0], playerVars["pos"][1]+trackRight[1]]

controls = {"advance":
				{"keys": [119, 1073741906],
				"state": False
				},
			"reverse":
				{"keys": [115, 1073741905],
				"state": False
				},
			"left":
				{"keys": [97, 1073741904],
				"state": False
				},
			"right":
				{"keys": [100, 1073741903],
				"state": False
				}
			}

while True:
	clock.tick(framerate)
	events = pygame.event.get()
	for event in events:
		if event.type==pygame.QUIT:
			pygame.quit()
			quit()
		if event.type==pygame.KEYDOWN:
			for cont in controls:
				thisCont = controls[cont]
				for key in thisCont["keys"]:
					if event.key == key:
						thisCont["state"] = True
		if event.type==pygame.KEYUP:
			for cont in controls:
				thisCont = controls[cont]
				for key in thisCont["keys"]:
					if event.key == key:
						thisCont["state"] = False

	if controls["left"]["state"]:
		animStates["leftTread"][0]-=0.2
		animStates["rightTread"][0]+=0.2
		playerVars["chassisAngle"] -= playerConst["turnSpeed"]
	if controls["right"]["state"]:
		animStates["leftTread"][0]+=0.2
		animStates["rightTread"][0]-=0.2
		playerVars["chassisAngle"] += playerConst["turnSpeed"]

	if playerVars["chassisAngle"] > math.pi*2:
		playerVars["chassisAngle"] = playerVars["chassisAngle"] - math.pi*2
	elif playerVars["chassisAngle"] < 0:
		playerVars["chassisAngle"] = math.pi*2 + playerVars["chassisAngle"]
	if playerVars["chassisAngle"] == math.pi/2:
		playerVars["chassisAngle"] = math.pi/2 - 0.001
	elif playerVars["chassisAngle"] == 3*math.pi/2:
		playerVars["chassisAngle"] = 3*math.pi/2 + 0.001

	newPos = playerVars["pos"].copy()
	changedPos = False
	if controls["advance"]["state"]:
		animStates["leftTread"][0]+=0.2
		animStates["rightTread"][0]+=0.2
		difference = getEndPoint(playerVars["chassisAngle"], playerConst["speed"])
		newPos[0] += difference[0]
		newPos[1] += difference[1]
		changedPos = True
	if controls["reverse"]["state"]:
		animStates["leftTread"][0]-=0.2
		animStates["rightTread"][0]-=0.2
		difference = getEndPoint(playerVars["chassisAngle"]+math.pi, playerConst["speed"])
		newPos[0] += difference[0]
		newPos[1] += difference[1]
		changedPos = True

	if changedPos and newPos != playerVars["pos"]:
		interceptions = []
		trajPP = [playerVars["pos"], newPos]
		trajSI = []
		trajSI.append((trajPP[1][1]-trajPP[0][1]) / (trajPP[1][0]-trajPP[0][0]))
		trajSI.append(-trajSI[0]*trajPP[0][0]+trajPP[0][1])
		for i in range(len(mapData["edges"])):
			indexEdge = mapData["edges"][i]
			edge = [mapData["all points"][indexEdge[0]], mapData["all points"][indexEdge[1]]]
			collision = circleLineCollision.detectCollision(trajPP, trajSI, edge, mapData["slpIntrcptWalls"][i], playerConst["radius"])
			interceptions.append(collision)
		closestPoint = newPos
		closestDist = circleLineCollision.getSqrDist(playerVars["pos"], closestPoint)
		for inter in interceptions:
			if inter == None:
				continue
			thisDist = circleLineCollision.getSqrDist(playerVars["pos"], inter)
			if thisDist < closestDist:
				closestDist = thisDist
				closestPoint = inter.copy()
		oldPos = playerVars["pos"].copy()
		playerVars["pos"] = closestPoint

	for anim in animStates:
		thisAnim = animStates[anim]
		if thisAnim[0] > thisAnim[1]:
			thisAnim[0] -= thisAnim[1]
		if thisAnim[0] < 0:
			thisAnim[0] += thisAnim[1]

	transDiff = [-playerVars["pos"][0], -playerVars["pos"][1]]
	newPoints = translate(transDiff, allPoints)
	rotAngle = -playerVars["chassisAngle"]-math.pi/2
	newPoints = rotate(rotAngle, newPoints)
	newPoints = dilate(playerConst["zoomFactor"], newPoints)
	highPoints = numpy.copy(newPoints)
	highPoints = magnify(playerConst["camElev"], highPoints)
	newPoints = translate(halfScreen, newPoints)
	highPoints = translate([halfScreen[0], halfScreen[1]], highPoints)

	###

	playerTracks = numpy.roll(playerTracks, 1, axis = 0)

	trackLeft = getEndPoint(playerVars["chassisAngle"]+math.pi/2, 7)
	playerTracks[0, 0] = [playerVars["pos"][0]+trackLeft[0], playerVars["pos"][1]+trackLeft[1]]
	trackRight = getEndPoint(playerVars["chassisAngle"]-math.pi/2, 7)
	playerTracks[0, 1] = [playerVars["pos"][0]+trackRight[0], playerVars["pos"][1]+trackRight[1]]

	newTracks1 = translate(transDiff, playerTracks[:, 0])
	newTracks1 = rotate(rotAngle, newTracks1)
	newTracks1 = dilate(playerConst["zoomFactor"], newTracks1)
	newTracks1 = translate(halfScreen, newTracks1)

	newTracks2 = translate(transDiff, playerTracks[:, 1])
	newTracks2 = rotate(rotAngle, newTracks2)
	newTracks2 = dilate(playerConst["zoomFactor"], newTracks2)
	newTracks2 = translate(halfScreen, newTracks2)

	screen.fill((83, 63, 52))

	pygame.draw.lines(screen, (63, 43, 32), False, newTracks1, width=3)
	pygame.draw.lines(screen, (63, 43, 32), False, newTracks2, width=3)

	for edge in mapData["edges"]:
		thisEdge = [newPoints[edge[0]], newPoints[edge[1]]]
		if ((thisEdge[0][0] < screenSize[0]+600 and thisEdge[0][0] > -600 and thisEdge[0][1] < screenSize[1]+600 and thisEdge[0][1] > -600)
		or (thisEdge[1][0] < screenSize[0]+600 and thisEdge[1][0] > -600 and thisEdge[1][1] < screenSize[1]+600 and thisEdge[1][1] > -600)):
			pygame.gfxdraw.filled_polygon(screen, (newPoints[edge[0]], newPoints[edge[1]], highPoints[edge[1]], highPoints[edge[0]]), (71, 35, 15))
			#pygame.gfxdraw.line(screen, round(newPoints[edge[0]][0]), round(newPoints[edge[0]][1]), round(highPoints[edge[0]][0]), round(highPoints[edge[0]][1]), (61, 21, 5))
			#pygame.gfxdraw.line(screen, round(newPoints[edge[1]][0]), round(newPoints[edge[1]][1]), round(highPoints[edge[1]][0]), round(highPoints[edge[1]][1]), (61, 21, 5))
	for cell in mapData["cells"]:
		inScreen = False
		for point in cell:
			thisPoint = highPoints[point]
			if thisPoint[0] < screenSize[0]+600 and thisPoint[0] > -600 and thisPoint[1] < screenSize[1]+600 and thisPoint[1] > -600:
				inScreen = True
				break
		if not inScreen:
			continue
		pygame.gfxdraw.filled_polygon(screen, highPoints[cell], (30, 16, 8))

	leftTread = miniSheets["sideTreads"].subsurface([round(animStates["leftTread"][0])*9, 0, 9, 32])
	rightTread = miniSheets["sideTreads"].subsurface([round(animStates["rightTread"][0])*9, 0, 9, 32])

	screen.blit(leftTread, (round(halfScreen[0])-18, round(halfScreen[1])-16))
	screen.blit(rightTread, (round(halfScreen[0])+9, round(halfScreen[1])-16))
	screen.blit(miniSheets["chassis"], (round(halfScreen[0])-13, round(halfScreen[1])-13))

	pygame.display.flip()
