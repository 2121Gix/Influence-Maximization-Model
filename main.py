# libraries
import dynetx
from tqdm import tqdm
import random
import matplotlib.pyplot as plt
import numpy as np
import math


class Edge:
    def __init__(self, id, src, dst, t):
        self.id = int(id)
        self.src = src
        self.dst = dst
        self.t = t


# class node - to give each node its properties
class Node:
    def __init__(self, id):
        self.id = int(id)
        self.status = 0
        self.cost = 0
        self.degree = 0
        self.prox = []
        self.prev = []
        self.cover = []
        self.msg = 0
        self.msgs = 0
        self.first = -1

    def __str__(self):
        return 'Node: ' + str(self.id) + ' State: ' + str(self.status)


def checktarget(nd, targ): #strat optimization
    fl = True
    for nodo in nd.prox:
        if nodo in targ:
            fl = False
    return fl


def irraggiungibilimsg(nodes, w): #strat 5.2
    cw = 0
    k = 0
    y = []
    nodes2 = nodes.copy()
    targ = []

    nodes2.sort(key=lambda x: x.msg, reverse=True)
    nodes2.sort(key=lambda x: x.msgs, reverse=False)

    while cw <= w - 1 and k < len(nodes2):
        nodo = nodes2[k]
        if nodo.cost <= w - cw and nodo.first != -1:
            if checktarget(nodo, targ):
                y.append(nodo)
                cw += nodo.cost
                targ += nodo.prox
                nodes2.remove(nodes2[k])
            else:
                k += 1
        else:
            nodes2.remove(nodes2[k])

    return y


def irraggiungibilitime(nodes, w): #strat 5
    cw = 0
    k = 0
    y = []
    nodes2 = nodes.copy()
    targ = []

    nodes2.sort(key=lambda x: x.first, reverse=False)
    nodes2.sort(key=lambda x: x.msgs, reverse=False)

    while cw <= w - 1 and k < len(nodes2):
        nodo = nodes2[k]
        if nodo.cost <= w - cw and nodo.first != -1:
            if checktarget(nodo, targ):
                y.append(nodo)
                cw += nodo.cost
                targ += nodo.prox
                nodes2.remove(nodes2[k])
            else:
                k += 1
        else:
            nodes2.remove(nodes2[k])

    return y
    
    


def timeorder(nodes, w): #strat 4
    cw = 0
    k = 0
    y = []
    nodes2 = nodes.copy()
    targ = []
    
    nodes2.sort(key=lambda x: x.msg, reverse=True)
    nodes2.sort(key=lambda x: x.first, reverse=False)
    
    while cw <= w - 1 and k < len(nodes2):
        nodo = nodes2[k]
        if nodo.cost <= w - cw and nodo.first != -1:
            if checktarget(nodo, targ):
                y.append(nodo)
                cw += nodo.cost
                targ += nodo.prox
                nodes2.remove(nodes2[k])
            else:
                k += 1
        else:
            nodes2.remove(nodes2[k])
    
    return y
    
    
def greedy(nodes, w): #strat 3
    cw = 0
    k = 0
    y = []
    nodes2 = nodes.copy()
    targ = []
    
    nodes2.sort(key=lambda x: x.msg, reverse=True)
    
    while cw <= w - 1 and k < len(nodes2):
        nodo = nodes2[k]
        if nodo.cost <= w - cw:
            if checktarget(nodo, targ):
                y.append(nodo)
                cw += nodo.cost
                targ += nodo.prox
                nodes2.remove(nodes2[k])
            else:
                k += 1
        else:
            nodes2.remove(nodes2[k])
    
    return y
    
def neighbors(nodes, w): #strat 2
    cw = 0
    k = 0
    
    y = []
    nodes2 = nodes.copy()
    targ = []
    
    nodes2.sort(key=lambda x: x.msg, reverse=True)

    while cw <= w - 1 and k < len(nodes2):
        nodo = nodes2[k]
        nodo.prev.sort(key=lambda x: x.first, reverse=False)
        scelto = False
        index = 0
        while not scelto and index < len(nodo.prev):
            node = nodo.prev[index]
            if node.cost <= w - cw and checktarget(node, targ):
                y.append(node)
                cw += node.cost
                targ += node.prox
                scelto = True
            index += 1
        k += 1   
          
    
    return y
        

def maxcover(nodes, w): #strat 1
    cw = 0
    k = 0  
    y = []
    nodes2 = nodes.copy()
    reach = []
    scelto = False
    nodes2.sort(key=lambda x: x.first, reverse=False)
    nodes2.sort(key=lambda x: len(x.cover), reverse=True)
    
    while cw <= w - 1 and k < len(nodes2):
        if scelto:
            nodes2.sort(key=lambda x: len(list(set(x.cover)-set(reach))), reverse=True)
            scelto = False
        nodo = nodes2[k]

        if nodo.cost <= w - cw:
            y.append(nodo)
            cw += nodo.cost
            reach = list(set(reach + nodo.cover))
            scelto = True
        nodes2.remove(nodo)
    
    return y
        
        
# main
if __name__ == '__main__':
    firsttime = 0
    f = open('college.txt', 'r') #insert dataset filename
    nodeList = []
    g = dynetx.DynDiGraph(edge_removal=True)


    print('Parsing network')
    interactions = []
    nnodes = 0
    j = 1
    for line in tqdm(f):
        i = 1
        for word in line.split():
            iw = int(word)
            if i == 1 or i == 2:
                if sum(p.id == iw for p in nodeList) == 0:
                    nodeList.append(Node(iw))
                    nnodes += 1
                if i == 1:
                    idSrc = iw
                else:
                    idDst = iw
            else:
                time = iw
                if j == 1:
                    firsttime = iw
            i += 1
        g.add_interaction(idSrc, idDst, time)
        interactions.append(Edge(j, idSrc, idDst, time))
        j += 1
    i = 0

    
    # initialize data tracking
    graphYS = []
    graphYI = []
    graphX = []
    nSusceptible = nnodes
    nInfected = 0
    graphYS.append(nSusceptible)
    graphYI.append(nInfected)
    graphX.append(firsttime)

    print('Scanning Network')
    for e in tqdm(g.stream_interactions()):
        for node in nodeList:
            if node.id == e[0]:
                break
        for node2 in nodeList:
            if node2.id == e[1]:
                break
        if node not in node.prox:
            node.prox.append(node)
        if node2 not in node.prox:
            node.prox.append(node2)
        if node2 not in node2.prox:
            node2.prox.append(node2)
        if node not in node2.prev:
            node2.prev.append(node)
        if node2 not in node2.prev:
            node2.prev.append(node2)
        node2.msgs += 1
        node.msg += 1
        if node.first == -1:
            node.first = int(e[3])

    print('Scanning more useful info')
    for ed in tqdm(reversed(interactions)):
        for node in nodeList:
            if node.id == ed.src:
                break
        for node2 in nodeList:
            if node2.id == ed.dst:
                break

        if node not in node.cover:
            node.cover.append(node)
        if node2 not in node2.cover:
            node2.cover.append(node2)

        node.cover = list(set(node.cover + node2.cover))

    # iteration to compute cost
    avgdeg = 0
    for node in nodeList:
        n = node.id
        node.degree = g.out_degree(n)
        avgdeg += node.degree
        if node.msg > 300:
            node.cost = math.exp(300)
        else:
            node.cost = math.exp(node.msg)
    avgdeg /= nnodes

    

    # strategy for infection (seeding)
    budget = 150 #insert budget limit
    pspread = 1 #probability of influence spreading on a contact
    seedSet = maxcover(nodeList, budget) #call a different function depending on what strategy
    print('Initial seed set is: ' + str(len(seedSet)) + 'elements: ')
    # apply first infections
    for node in nodeList:
        for nodz in seedSet:
            if node.id == nodz.id:
                print(node.id)
                nInfected += 1
                nSusceptible -= 1
                node.status = -1

    print('Simulating infection')
    # update data tracking
    graphYS.append(nSusceptible)
    graphYI.append(nInfected)
    graphX.append(firsttime)

    # simulation
    currenttime = firsttime
    nInteractions = 0
    for e in tqdm(g.stream_interactions()):
        timestamp = e[3]

        if timestamp != currenttime:
            graphX.append(currenttime)
            graphYI.append(nInfected)
            graphYS.append(nSusceptible)
            currenttime = timestamp

        for node in nodeList:
            if e[0] == node.id:
                srcStatus = node.status
                break
        for node in nodeList:
            if e[1] == node.id:
                dstIndex = nodeList.index(node)
                dstStatus = node.status
                break

        if srcStatus == -1 and dstStatus == 0:
            nInteractions += 1
            p = random.uniform(0, 1)
            if p <= pspread:
                nodeList[dstIndex].status = -1
                nInfected += 1
                nSusceptible -= 1

    graphX.append(time)
    graphYI.append(nInfected)
    graphYS.append(nSusceptible)

    print('Simulation Over With: ' + str(nnodes) + ' total nodes and: ' + str(nInteractions) + ' active interactions' )
    print(str(nInfected) + ' infected nodes')
    print(str(nSusceptible) + ' susceptible nodes')
    
    #plotting
    vX = np.array(graphX)
    vYI = np.array(graphYI)
    vYS = np.array(graphYS)

    plt.plot(vX, vYI, 'r-', label='Infected Nodes Number')
    plt.plot(vX, vYS, 'b-', label='Susceptible Nodes Number')
    plt.legend()
    plt.ylabel('Number of Nodes')
    plt.xlabel('Network Time Window')

    plt.suptitle('BUDGET=' + str(budget), fontsize=14, fontweight='bold')

    plt.show()
    input("Press enter to exit;")








