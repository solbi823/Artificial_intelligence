import sys
import os
import string
import ctypes

# double ended queue 를 import 한다: BFS와 IDS에 사용
from collections import deque 
# prioirity queue 를 import 한다. a star algorithm에 사용
import heapq


# 각각의 node 를 나타내는 자료구조입니다. 미로의 node들은 이중 배열로 저장합니다. 
class Node():

	def __init__(self, x, y, value):

		self.xpos = x
		self.ypos = y
		self.state = value

		self.parentNode = None
		self.childNodes =[]

		#key를 찾고 난 다음에 아래의 값들은 초기화 되어야합니다. 
		self.heuristicValue = 1000
		self.movedDistance = 0


	def __lt__(self, other):
		return (self.heuristicValue + self.movedDistance < other.heuristicValue + other.movedDistance)

	def printit(self):
		print("x: "+str(self.xpos)+"  y: "+str(self.ypos) + " state: "+ str(self.state) + "  hValue: "+str(self.heuristicValue))


	# 현재 거리로부터 목표 지점까지의 거리를 manhattan distance 로 구합니다.
	def heuristic(self, goal): 
		self.heuristicValue = abs(self.xpos - goal.xpos) + abs(self.ypos - goal.ypos)

	# 출발 지점에서 얼마나 이동했는지 계산합니다. 
	def setMovedDistance(self):	

		if self.parentNode != None:
			self.movedDistance = self.parentNode.movedDistance + 1


	# 현재 노드에서 갈수 있는 node를 찾아서 parent - child 관계를 등록합니다. 
	def seekChildNodes(self, arrValue):

		# key를 찾은 이후에 다시 child node를 찾을 때에는 빈 리스트에서 시작해야합니다. 
		self.childNodes = []	

		# 출발지점이라면 아래 한칸이 유일한 child node.
		if self.state == 3:			
			self.childNodes.append(arrValue[self.xpos+1][self.ypos])
			arrValue[self.xpos+1][self.ypos].parentNode = self
			return

		# 도착지점이라면 child node 는 없습니다. 
		# 키보다 목적지에 먼저 도달하였을 경우를 위한 예외처리
		if self.state == 4:
			return

		# 상하좌우 중 벽이 아니고 parent node 가 아닌 것이 child node.

		if arrValue[self.xpos-1][self.ypos].state != 1 and arrValue[self.xpos-1][self.ypos] != self.parentNode:
			self.childNodes.append(arrValue[self.xpos-1][self.ypos])
			arrValue[self.xpos-1][self.ypos].parentNode = self

		if arrValue[self.xpos+1][self.ypos].state != 1 and arrValue[self.xpos+1][self.ypos]!= self.parentNode:
			self.childNodes.append(arrValue[self.xpos+1][self.ypos])
			arrValue[self.xpos+1][self.ypos].parentNode = self

		if arrValue[self.xpos][self.ypos-1].state != 1 and arrValue[self.xpos][self.ypos-1] != self.parentNode:
			self.childNodes.append(arrValue[self.xpos][self.ypos-1])
			arrValue[self.xpos][self.ypos-1].parentNode = self

		if arrValue[self.xpos][self.ypos+1].state != 1 and arrValue[self.xpos][self.ypos+1] != self.parentNode:
			self.childNodes.append(arrValue[self.xpos][self.ypos+1])
			arrValue[self.xpos][self.ypos+1].parentNode = self


	# 탐색을 종료하였을 때 백트래킹하여 경로를 파악합니다. 움직인 거리를 리턴합니다. 
	def backtrackPath(self):
		path = self
		length = self.movedDistance
		self.movedDistance = 0

		# 지나온 경로를 5로 바꿉니다. 
		while path.parentNode != None :
			path.state = 5
			path = path.parentNode

		return length



# 여기서부터 미로를 찾는 알고리즘입니다. 
# BFS 와 Iterative deepening search 는 uninformed search 입니다. 
# 키와 목적지의 위치를 알지 못하고 해당 값이 나올 때까지 search 해야합니다. 

def BFS(arrInform, arrValue, start_point):

	time = 0
	dq = deque()
	# 큐에 시작점을 넣어줍니다. 	
	dq.append(start_point)

	while dq:	# 큐가 비어있지 않은 동안
		here = dq.popleft()		# pop은 방문하는 것
		here.setMovedDistance()
		# print(str(here.xpos)+" " + str(here.ypos)+" "+str(here.state) )

		time += 1

		# 만일 키 값이라면, 탐색을 종료하고 다시 시작합니다. 
		if here.state == 6:
			break

		# 갈수 있는 길을 탐색하여 자식 노드에 등록 후 큐에 넣도록 합니다.
		here.seekChildNodes(arrValue)		
		for child in here.childNodes:
			dq.append(child)

	key_length = here.backtrackPath()
	here.parentNode = None
	dq = deque()

	# key에서부터 목적지까지의 탐색을 다시 시작합니다. 
	dq.append(here)

	while dq:
		here = dq.popleft()
		here.setMovedDistance()
		time +=1 

		# 만일 goal 값이라면, 탐색을 종료합니다. 
		if here.state == 4:
			break

		here.seekChildNodes(arrValue)
		for child in here.childNodes:
			dq.append(child)

	goal_length = here.parentNode.backtrackPath() + 1
	whole_length = key_length + goal_length
	
	print("length :" + str(whole_length))
	print("time: " + str(time))

	return arrValue, whole_length, time


# Iterative Deepening Search
def IDS(arrInform, arrValue, start_point):

	# depth limit 은 DFS를 실시할 depth level을 제한합니다. 
	depth_limit = 0
	time = 0

	here = start_point
	
	while here.state != 6 and depth_limit < 5000:

		depth_limit += 1

		#double ended queue를 stack 으로 사용합니다. 
		stk = deque()
		stk.append(start_point)

		while stk:

			here = stk.pop()	
			time += 1

			if here.state == 6:
				break

			here.seekChildNodes(arrValue)
			for child in here.childNodes:
				child.setMovedDistance()
				if child.movedDistance > depth_limit:
					break
				stk.append(child)


	key_length = here.backtrackPath()
	here.parentNode = None
	key_point = here

	depth_limit = 0	

	while here.state != 4 and depth_limit < 5000:

		depth_limit += 1

		stk = deque()
		stk.append(key_point)

		while stk:

			here = stk.pop()	
			time += 1

			if here.state == 4:
				break

			here.seekChildNodes(arrValue)
			for child in here.childNodes:
				child.setMovedDistance()
				if child.movedDistance > depth_limit:
					break
				stk.append(child)

	goal_length = here.parentNode.backtrackPath() + 1
	whole_length = key_length + goal_length
	
	print("length :" + str(whole_length))
	print("time: " + str(time))

	return arrValue, whole_length, time



# Greedy best first search , A* 알고리즘은 informed search 입니다. 
# 각각의 노드로부터 키와 목적지까지의 heuristic 값을 계산하여 이를 감소시키는 방향으로 search하도록 합니다.

# Greedy best first search 는 휴리스틱 값만 고려합니다. 
def greedyBestFirst(arrInform, arrValue, start_point, key_point, goal_point):

	time = 0
	pq = []

	# 우선순위 큐에 시작점을 넣어줍니다. 
	# 우선순위는 휴리스틱 값으로 설정합니다. 
	start_point.heuristic(key_point)
	heapq.heappush(pq, (start_point.heuristicValue, start_point))

	while pq: 	#priority queue 가 비어있지 않은 동안

		# 휴리스틱 값이 가장 작은 node 부터 pop 하게 됩니다. 
		idle, here = heapq.heappop(pq)	
		time += 1

		# 만일 키 값이라면, 탐색을 종료하고 다시 시작합니다. 
		if here.state == 6:
			break

		# 키 값이 아니라면, 갈수 있는 길을 탐색하여 자식 노드에 등록 후 큐에 넣도록 합니다. 
		here.seekChildNodes(arrValue)
		for child in here.childNodes:
			# 모든 갈 수 있는 child node 에 대해서 휴리스틱 함수를 계산한 후에 우선순위 큐에 넣도록 합니다. 
			child.setMovedDistance()
			child.heuristic(key_point)
			heapq.heappush(pq, (child.heuristicValue, child))

	# 백트래킹하여 경로를 표시합니다. 
	key_length = here.backtrackPath()
	here.parentNode = None
	pq = []


	# key에서부터 목적지까지의 탐색을 다시 시작합니다. 
	here.heuristic(goal_point)
	heapq.heappush(pq, (here.heuristicValue, here))

	while pq:
		idle, here = heapq.heappop(pq)
		time += 1

		# 만일 goal 값이라면, 탐색을 종료합니다.
		if here.state == 4:
			break

		here.seekChildNodes(arrValue)
		for child in here.childNodes:
			child.setMovedDistance()
			child.heuristic(goal_point)
			heapq.heappush(pq, (child.heuristicValue, child))

	goal_length = here.parentNode.backtrackPath() + 1
	whole_length = key_length + goal_length


	print("length :" + str(whole_length))
	print("time: " + str(time))

	return arrValue, whole_length, time


# A* algorithm 은 휴리스틱 값 뿐만 아니라 지나온 거리와의 합도 고려합니다. 
def aStarSearch(arrInform, arrValue, start_point, key_point, goal_point):

	time = 0
	pq = []

	# 우선순위 큐에 시작점을 넣어줍니다. 
	# 우선순위는 지나온 path cost와 휴리스틱 값의 합으로 설정합니다. 
	start_point.heuristic(key_point)
	heapq.heappush(pq, (start_point.heuristicValue + start_point.movedDistance, start_point))

	while pq: 	#priority queue 가 비어있지 않은 동안

		# 이동한 거리와 휴리스틱 값을 더한 값이 가장 작은 node 부터 pop 하게 됩니다. 
		idle, here = heapq.heappop(pq)	
		time += 1

		# 만일 키 값이라면, 탐색을 종료하고 다시 시작합니다. 
		if here.state == 6:
			break

		# 키 값이 아니라면, 갈수 있는 길을 탐색하여 자식 노드에 등록 후 큐에 넣도록 합니다. 
		here.seekChildNodes(arrValue)
		for child in here.childNodes:
			# 모든 갈수 있는 child node 에 대해서 이동한 거리와 휴리스틱 함수를 계산한 후에 우선순위 큐에 넣도록 합니다. 
			child.setMovedDistance()
			child.heuristic(key_point)
			heapq.heappush(pq, (child.heuristicValue + child.movedDistance, child))

	# 백트래킹하여 경로를 표시합니다. 
	key_length = here.backtrackPath()
	here.parentNode = None
	pq = []


	# key에서부터 목적지까지의 탐색을 다시 시작합니다. 
	here.heuristic(goal_point)
	heapq.heappush(pq, (here.heuristicValue + here.movedDistance , here))

	while pq:
		idle, here = heapq.heappop(pq)
		time += 1

		# 만일 goal 값이라면, 탐색을 종료합니다.
		if here.state == 4:
			break

		here.seekChildNodes(arrValue)
		for child in here.childNodes:
			child.setMovedDistance()
			child.heuristic(goal_point)
			heapq.heappush(pq, (child.heuristicValue + child.movedDistance , child))

	goal_length = here.parentNode.backtrackPath() + 1
	whole_length = key_length + goal_length


	print("length :" + str(whole_length))
	print("time: " + str(time))

	return arrValue, whole_length, time



# 텍스트 파일을 입력받아 arrInform 리스트, arrValue 이중 리스트에 담아 리턴시키는 함수입니다. 
def read_and_print_file(path):

	f = open(os.path.expanduser(path))

	line = f.readline()
	line.rstrip('\n')
	arrInform = line.split(' ')
	arrInform = list(map(int, arrInform))
	# arrInform[0] == 층
	# arrInform[1] == 행의 개수
	# arrInform[2] == 열의 개수 
	print(arrInform)
		
	arrValue = []

	for i in range(0, arrInform[1]):		#행의 수 만큼 line 을 읽습니다. 

		line = f.readline()
		if not line:
			print("제시된 행의 수보다 입력된 행의 수가 부족합니다.")
			break
		# get a line

		line.rstrip('\n')
		lineArr = line.split(' ')
		nodeArr = []

		for j in range(0, arrInform[2]): 	#열의 수 만큼 node를 생성합니다. 
			tmp = Node(i, j, int(lineArr[j]) )
			#tmp.printit()
			nodeArr.append(tmp)

		arrValue.append(nodeArr)

	f.close()

	return arrInform, arrValue



# arrInform, arrValue 를 받아서 시작, 키, 목적 지점을 리턴하는 함수입니다. 
def find_points(arrInform, arrValue):

	start_point = None 
	key_point = None 
	goal_point = None

	for i in range(0, arrInform[2]):
		if arrValue[0][i].state == 3:
			#print(i)
			start_point = arrValue[0][i]
			break

	for i in range(1, arrInform[1]-1):
		for j in range(0, arrInform[2]):
			if arrValue[i][j].state == 6:
				#print(str(i)+" "+str(j))
				key_point = arrValue[i][j]
				break
		if key_point != None :
			break
			

	for i in range(0, arrInform[2]):
		if arrValue[arrInform[1]-1][i].state == 4:
			#print(i)
			goal_point = arrValue[arrInform[1]-1][i]
			break

	if start_point == None or key_point == None or goal_point == None:
		print("포인트를 찾지 못했습니다.")

	else:
		start_point.printit()
		key_point.printit()
		goal_point.printit()
	
	return start_point, key_point, goal_point


# arrValue 이중 리스트를 출력하기 위하여 스트링 형식으로 바꾸어 리턴하는 함수입니다. 
def arrToString(arrInform, arrValue):
	string = ""
	for i in range(arrInform[1]):
		for j in range(arrInform[2]):
			string+= str(arrValue[i][j].state)+" "

		string+="\n"

	return string




# 여기서부터 각각의 층에 대해 적합한 알고리즘을 이용해 미로찾기를 수행하는 함수입니다.
# 5개의 층 모두 greedy best first search 알고리즘이 최단시간 결과값이 나왔기에 이를 적용하였습니다. 

def first_floor():

	#arrInform은 각 층의 미로에 대한 행과 열의 정보, 
	#arrValue 는 각 층의 미로 구조에 대한 정보를 담고 있습니다.

	arrInform, arrValue = read_and_print_file("first_floor_input.txt")
	start, key, goal = find_points(arrInform, arrValue)
	
	changedArr, length, time = greedyBestFirst(arrInform, arrValue, start, key, goal)

	f = open(os.path.expanduser("first_floor_output.txt"), 'w', encoding='utf8')

	f.write( arrToString(arrInform, changedArr))
	f.write("---\nlength="+str(length)+"\ntime="+str(time))

	f.close()


def second_floor():

	arrInform, arrValue = read_and_print_file("second_floor_input.txt")
	start, key, goal = find_points(arrInform, arrValue)
	
	changedArr, length, time = greedyBestFirst(arrInform, arrValue, start, key, goal)

	f = open(os.path.expanduser("second_floor_output.txt"), 'w', encoding='utf8')

	f.write( arrToString(arrInform, changedArr))
	f.write("---\nlength="+str(length)+"\ntime="+str(time))

	f.close()


def third_floor():

	arrInform, arrValue = read_and_print_file("third_floor_input.txt")
	start, key, goal = find_points(arrInform, arrValue)
	
	changedArr, length, time = greedyBestFirst(arrInform, arrValue, start, key, goal)

	f = open(os.path.expanduser("third_floor_output.txt"), 'w', encoding='utf8')

	f.write( arrToString(arrInform, changedArr))
	f.write("---\nlength="+str(length)+"\ntime="+str(time))

	f.close()


def fourth_floor():

	arrInform, arrValue = read_and_print_file("fourth_floor_input.txt")
	start, key, goal = find_points(arrInform, arrValue)
	
	changedArr, length, time = greedyBestFirst(arrInform, arrValue, start, key, goal)

	f = open(os.path.expanduser("fourth_floor_output.txt"), 'w', encoding='utf8')

	f.write( arrToString(arrInform, changedArr))
	f.write("---\nlength="+str(length)+"\ntime="+str(time))

	f.close()


def fifth_floor():

	arrInform, arrValue = read_and_print_file("fifth_floor_input.txt")
	start, key, goal = find_points(arrInform, arrValue)
	
	changedArr, length, time = greedyBestFirst(arrInform, arrValue, start, key, goal)

	f = open(os.path.expanduser("fifth_floor_output.txt"), 'w', encoding='utf8')

	f.write( arrToString(arrInform, changedArr))
	f.write("---\nlength="+str(length)+"\ntime="+str(time))

	f.close()


def main():

	first_floor()
	second_floor()
	third_floor()
	fourth_floor()
	fifth_floor()


if __name__ == "__main__":
	main()