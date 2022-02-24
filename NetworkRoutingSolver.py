#!/usr/bin/python3


from CS312Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        total_length = 0

        index = destIndex
        if self.prev[index] < 0:                    #if the destination node has no prev, it wasn't
            return{'cost':float('inf'), 'path':[]}  #reached by the Dijkstra algorithm

        while self.prev[index] >= 0:                #follow the prev pointers down the path
            node = self.network.nodes[index]

            prev_index = self.prev[index]
            prev_node = self.network.nodes[prev_index]

            edge = None
            for e in prev_node.neighbors:           #get the edge that connects the two nodes
                if str(e.dest) == str(node):        #along the path
                    edge = e

            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length             #add the edges to the list and update length

            index = prev_node.node_id               #go to the next prev node
        if index != self.source:                            #if we didn't make it back to the start,
            return{'cost':float('inf'), 'path':path_edges}  #then it doesn't connect

        return {'cost':total_length, 'path':path_edges}     #return the length and path

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex

        t1 = time.time()

        self.prev = []                  #array for keeping track of prev pointers
        for n in self.network.nodes:    #O(|V|)
            self.prev.append(-1)
        
        queue = None
        if use_heap:
            queue = BinaryHeap()
        else:
            queue = ArrayQueue()
        queue.create(self.network, srcIndex)        #see complexity in implementation below

        while queue.size > 0:                       #for every node in the queue (|V|)
            info = queue.pop_min()                  #complexity in implementation

            node = self.network.nodes[info[0]]
            for edge in node.neighbors:             #for each edge going out of the node (|E|)
                dst_id = edge.dest.node_id
                dst_dist = queue.get_dist(dst_id)   #constant lookup for either implementation

                if dst_dist is None:                #we've already dealt with this one, pass
                    pass

                elif ( dst_dist < 0 ) or ( dst_dist > info[1]+edge.length ):#if we can shorten the dist
                    self.prev[dst_id] = info[0]                             #update prev pointer           
                    queue.decr_key(dst_id, info[1]+edge.length)             #see implementation

        t2 = time.time()
        return (t2-t1)

class BinaryHeap:
    def __init__(self):
        self.pointers = []
        self.heap = []
        self.size = 0
        self.fullSize = 0

    def get_dist(self, num):        #constant time lookup thanks to pointers list
        if not self.pointers[num]:
            return None
        return self.heap[self.pointers[num]][1]

    def create(self, network, srcIndex):    #creates starting heap, O(|V|) time
        index = 0
        self.pointers = [None] * len(network.nodes) #empty list for lookup pointers
        for n in network.nodes:                     #for each node (O|V|)
            self.heap.append([index, -1])           #initialize dist as infinite
            self.pointers[index] = index            #set up pointer
            self.size +=1
            index +=1
        self.heap[srcIndex][1] = 0                  #set start node to 0
        self.bubble_up(srcIndex)                    #"sort" the heap O(log|V|)

        self.fullSize = len(network.nodes)          #this is just for error checking later
        
    def bubble_up(self, index):     #move value up to the correct spot in tree, O(log|V|)
        if index == 0:              #can't move up if we're already at 0
            return
        current = self.heap[index]  #current value
        pIndex = (index-1)//2       
        parent = self.heap[pIndex]  #parent value

        if ( current[1] >= 0 and parent[1] < 0 ) or ( current[1] < parent[1] ): #if current < parent
            self.heap[index] = parent               #switch spots in the heap
            self.heap[pIndex] = current
            self.pointers[current[0]] = pIndex      #switch values in pointer list
            self.pointers[parent[0]] = index

            self.bubble_up(pIndex)                  #repeat until done, log|V| times at worst

    def decr_key(self, num, dist):      #decreases key value and updates heap, O(log|V|)
        index = self.pointers[num]      #get position in heap
        self.heap[index][1] = dist      #update dist value
        self.bubble_up(index)           #correct position, O(log|V|)

    def insert(self, num, dist):        #inserts new value into heap, log|V|
        self.heap[self.size][1] = dist  #add new value to bottom of heap
        self.pointers[num] = self.size  #add new pointer
        self.bubble_up(self.size)       #adjust position, O(log|V|)
        self.size += 1                  #update size

    def pop_min(self):                  #removes min value from heap, log|V|
        info = self.heap[0]             #store min value
        self.pointers[info[0]] = None   #"remove" it from heap

        self.heap[0] = self.heap[self.size-1]   #put bottom value into first position
        self.pointers[self.heap[0][0]] = 0      #adjust pointer
        self.heap[self.size-1] = None           
        self.size -= 1                          #adjust size value
        self.sift(0)                            #sift down to position, O(log|V|)

        return info

    def sift(self, index):          #move down tree to correct position, O(log|V|)
        current = self.heap[index]  #store current value
        c1_index = index*2 + 1      #left child index
        c2_index = index*2 + 2      #right child index

        if c1_index >= self.fullSize or c2_index >= self.fullSize:  #check if out of bounds
            return
        child1 = self.heap[c1_index]    #store left child value
        child2 = self.heap[c2_index]    #store right child value

        min = index     #keep track if index of minimum value
        #if left child is less than current
        if child1 and (( current[1] < 0 and child1[1] >= 0 ) or ( current[1] > child1[1] )):
            min = c1_index  #left child is new minimum

        #if right child is less than current minimum
        if child2 and (( self.heap[min][1] < 0 and child2[1] >= 0 ) or ( self.heap[min][1] > child2[1] )):
            if not (child2[1] < 0):
                min = c2_index  #right child is new minimum

        if min != index:                        #if the current value isn't the minimum
            temp = self.heap[index]             #switch current with minimum
            self.heap[index] = self.heap[min]
            self.heap[min] = temp

            self.pointers[temp[0]] = min        #adjust pointers
            self.pointers[self.heap[index][0]] = index

            self.sift(min)                      #repeat, worst case log|V| times



class ArrayQueue:
    def __init__(self):
        self.queue = []
        self.size = 0

    def get_dist(self, num):    #constant lookup function
        return self.queue[num]

    def create(self, network, srcIndex):    #initialize queue, O(|V|)
        for n in network.nodes:             #for each node, |V|
            self.queue.append(-1)           #set dist to infinity
            self.size += 1                  #update size value
        self.queue[srcIndex] = 0            #set first node distance to 0

    def insert(self, index, dist):          #add value to queue, O(1)
        self.queue[index] = dist            #append into queue
        self.size += 1                      #update size

    def decr_key(self, index, dist):        #change key value, O(1)
        self.queue[index] = dist

    def pop_min(self):      #remove minimum value from queue, O(|V|)
        min = -1            #set "minimum" to infinity
        min_index = -1      #set false index
        index = 0
        for n in self.queue:                #for each value in the queue O(|V|)
            if ( n is None ) or (n < 0):    #skip removed values
                pass
            elif ( n >= 0 and min < 0 ) or ( n < min ): #if it's less than the current minimum
                min = n                                 #set new minimum
                min_index = index

            index += 1

        self.queue[min_index] = None    #remove minimum value from list
        self.size -= 1
        return (min_index, min)
        