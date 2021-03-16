import simpy
import random
import math
from scipy.stats import expon

## Global Parameters ##

Tm = 1024  # Bits
Toh = 184  # Overhead Bits
Ttoken = 184  # Token bits
Bandwidth = 10  # 10Mbps
step = (Toh + Ttoken) / Bandwidth  # interval time for checking the bus
Ts = 500  # default hi_pri_token_hold_time
Trt = 15000  # default Target_Rotation_time for class B
NumNodes = 10  # default number of nodes


def createNodes(NumberOfNodes, env, bus, load, givenTs, givenTrt):
    """
    Creates the Nodes of the network and establishes the logical ring
    """
    global Ts, Trt, NumNodes
    Ts = givenTs
    Trt = givenTrt
    NumNodes = NumberOfNodes
    addresses = []
    nodes = []
    for i in range(NumberOfNodes):
        while True:
            add = str(random.randint(10000000, 99999999))
            if add not in addresses:
                addresses.append(add)
                break
        nodes.append(Node(env, add, bus, load))
    # Create the logical ring
    for i in range(NumberOfNodes):
        nodes[i - 1].fend.next = addresses[i]
    # Choose a node to start with the token
    token_address = addresses[random.randint(0, NumberOfNodes - 1)]
    return token_address, nodes


def interArrival(pkt_class, load):
    """
    Time distribution of Packet Generator
    """
    arr_lambda = (Bandwidth * load) / ((Tm + Toh) * NumNodes)
    if pkt_class == "A":
        return round(1 / arr_lambda)
    elif pkt_class == "B":
        p = random.random()
        # Poisson Process
        return round(-math.log(1.0 - p) / arr_lambda)


def distSize(pkt_class):
    """
    Size distribution of Packets is Constant for A class packets 
    and exponentially distributed with mean Tm for B class packets
    """
    Tmin = 800
    Tmax = 1248
    if pkt_class == "A":
        return Tm
    elif pkt_class == "B":
        Size = expon.rvs(scale=Tm, loc=0, size=1)  # Scale is the mean
        if Size[0] < Tmin:
            return Tmin
        elif Size[0] > Tmax:
            return Tmax
        else:
            return math.floor(Size[0])


def report(nodes, meanDictA, maxDictA, meanDictB, maxDictB):
    """
    Placeholder function to show the Mean and the Max delay times of each class for every node
    """
    ("Nodes:")
    i = 1
    for node in nodes:
        if len(node.times_listA) != 0:
            meanDictA[i].append(sum(node.times_listA) / (1000 * len(node.times_listA)))
            maxDictA[i].append(max(node.times_listA) / 1000)
        else:
            meanDictA[i].append(10000)
            maxDictA[i].append(10000)

        if len(node.times_listB) != 0:
            meanDictB[i].append(sum(node.times_listB) / (1000 * len(node.times_listB)))
            maxDictB[i].append(max(node.times_listB) / 1000)
        else:
            meanDictB[i].append(10000)
            maxDictB[i].append(10000)

        i += 1
    ##        print(node)
    ##        print(
    ##            "Class A: Mean={:.2f} Max={:.2f}".format(
    ##                sum(node.times_listA) / len(node.times_listA), max(node.times_listA)
    ##            )
    ##        )
    ##        print(
    ##            "Class B: Mean={:.2f} Max={:.2f}".format(
    ##                sum(node.times_listB) / len(node.times_listB), max(node.times_listB)
    ##            )
    ##        )
    return meanDictA, maxDictA, meanDictB, maxDictB


class Bus(object):
    """
    The bus of the network. It holds one packet at a time, and is being read by every node.
    A node can send a packet in the bus only if it holds the token which is also being passed
    through the bus.

    Parameters
    ----------
    env : simpy.Environment
        the simulation environment
    pkt : Packet object
        the packet that is being transmitted 
    """

    def __init__(self, env):
        self.env = env

    def createToken(self, address):
        self.pkt = Packet(0, Ttoken + Toh, 0, dst=address, type_id=1)

    # function to send a packet in the bus
    def send(self, pkt):
        # print("%.2fus = " % self.env.now, pkt)
        self.pkt = pkt

    # function to read a packet from the bus
    def read(self):
        return self.pkt


class Packet(object):
    """
    The packet of the network.

    Parameters
    ----------
    time : float
        the time the packet was created by the PacketGenerator.
    size : float
        the size of the packet in bytes
    id : int
        an identifier for the packet, 
    src, dst : string
        addresses for source and destination nodes
    type_id : int
        if the value is 1 the packet is the token (Default = 0).
    pkt_class : str
        either A or B depending on the class of the packet. The tokens have the default class ""
    """

    def __init__(self, time, size, id, src="", dst="", type_id=0, pkt_class=""):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.type_id = type_id
        self.pkt_class = pkt_class

    def __repr__(self):
        return "id: {}, src: {}, dst: {}, time: {}, size: {}, type: {}, class: {}".format(
            self.id,
            self.src,
            self.dst,
            self.time,
            self.size,
            self.type_id,
            self.pkt_class,
        )

    # function to read the dst field of the packet
    def get_dest(self):
        return self.dst

    # function to identify the type of the packet
    def get_type(self):
        return self.type_id


class Node(object):
    """
    A Node of the network. The node consists of two parts, the PacketGenerator
    which simulates a process generating packets and the FrontEnd which interracts with the network

    Parameters
    ----------
    env : simpy.Environment
        the simulation environment
    id : string
        the address of the node
    bus : Bus object
        the bus of the network
    load : float
        the load of the network
    pg : PacketGenerator object
        the packet generator part of the node
    fend : FrontEnd object
        the front end part of the node
    memA, memB : list
        the memory of the node, where packets of each class are stored until they are transmitted
    times_listA, times_listB : list
        the time each packet waited on the queue
    """

    def __init__(self, env, id, bus, load):
        self.env = env
        self.id = id
        self.bus = bus
        self.load = load
        self.pg = PacketGenerator(env, id, interArrival, distSize, load, self)
        self.fend = FrontEnd(env, self, bus, id)
        self.times_listA = []
        self.times_listB = []
        self.memA = []
        self.memB = []

    # function to put a packet in the memory
    def put(self, pkt):
        if pkt.pkt_class == "A":
            self.memA.append(pkt)
        else:
            self.memB.append(pkt)

    # function to get a packet from the memory using FIFO
    def get(self, pkt_class):
        if pkt_class == "A":
            return self.memA.pop(0)
        else:
            return self.memB.pop(0)

    # function to check if the memory is empty
    def mem_empty(self, pkt_class):
        if pkt_class == "A":
            if len(self.memA) == 0:
                return True
            else:
                return False
        else:
            if len(self.memB) == 0:
                return True
            else:
                return False

    def __repr__(self):
        return "Address: {}".format(self.id)


class PacketGenerator(object):
    """ 
    The PacketGenerator part of the node. It generates packets with 
    a given time and size distribution.

    Parameters
    ----------
    env : simpy.Environment
        the simulation environment
    adist : function
        a no parameter function that returns the times the packets are created
    sdist : function
        a no parameter function that returns the sizes of the packets
    out : Node object
        the node the PacketGenerator is part of
    initial_delay : number
        Starts generation after an initial delay. Default = 0
    finish : number
        Stops generation at the finish time. Default is infinite
    """

    def __init__(
        self, env, id, adist, sdist, load, out, initial_delay=0, finish=float("inf"),
    ):
        self.id = id
        self.env = env
        self.adist = adist
        self.sdist = sdist
        self.load = load
        self.initial_delay = initial_delay
        self.finish = finish
        self.out = out
        self.packets_sent = 0
        # start the action methods as simpy processes
        self.actionA = env.process(self.processA())
        self.actionB = env.process(self.processB())

    # The generator function that produces packets of class A
    def processA(self):
        yield self.env.timeout(self.initial_delay)  # wait for the initial delay
        while self.env.now < self.finish:
            # wait until the time given by the distribution
            yield self.env.timeout(self.adist("A", self.load))
            self.packets_sent += 1
            p = Packet(
                self.env.now,
                Toh + self.sdist("A"),
                self.packets_sent,
                src=self.id,
                pkt_class="A",
            )
            self.out.put(p)  # send the packet to the node memory

    # The generator function that produces packets of class B
    def processB(self):
        yield self.env.timeout(self.initial_delay)  # wait for the initial delay
        while self.env.now < self.finish:
            # wait until the time given by the distribution
            yield self.env.timeout(self.adist("B", self.load))
            self.packets_sent += 1
            p = Packet(
                self.env.now,
                Toh + self.sdist("B"),
                self.packets_sent,
                src=self.id,
                pkt_class="B",
            )
            self.out.put(p)  # send the packet to the node memory


class FrontEnd(object):
    """
    The FrontEnd part of the node. It reads the packet being sent in the network
    and sends the packets of the node when he receives the token.

    Parameters
    ----------
    env : simpy.Environment
        the simulation environment
    node : Node object
        the node the FrontEnd is part of
    bus : Bus object
        the bus of the network
    dtrans : float
        the dtrans given a constant packet size and link speed. Default = 1
    id : string
        the node address
    next : string
        the address of the next node in the logical ring
    """

    def __init__(self, env, node, bus, id, nextnode=""):
        self.env = env
        self.node = node
        self.bus = bus
        self.id = id
        self.next = nextnode
        self.limitB = Trt  # initialize Trt
        # start the run function as simpy process
        self.action = env.process(self.run())

    def run(self):
        while True:
            pkt = self.bus.read()  # read the bus
            # if you receive the token start transmitting
            if self.is_token(pkt) == True:
                yield self.env.process(self.transmitt())
            else:
                yield self.env.timeout(step)

    # function to check if the packet received is the token
    def is_token(self, pkt):
        if (pkt.get_type() == 1) and (pkt.get_dest() == self.id):
            return True
        else:
            return False

    # function to start transmitting
    def transmitt(self):
        # set the hi pri token timer
        limitA = self.env.now + Ts
        # transmit the class A packets
        while (self.env.now < limitA) and (not (self.node.mem_empty("A"))):
            # get the packet from the memory and send it to the bus
            p = self.node.get("A")
            dtrans = p.size / Bandwidth
            yield self.env.timeout(dtrans)
            self.node.times_listA.append(self.env.now - p.time)
            self.bus.send(p)
        # transmit the class B packets until the Trt ends
        while (self.env.now < self.limitB) and (not (self.node.mem_empty("B"))):
            p = self.node.get("B")
            dtrans = p.size / Bandwidth
            yield self.env.timeout(dtrans)
            self.node.times_listB.append(self.env.now - p.time)
            self.bus.send(p)
        # set the new Trt
        self.limitB = self.env.now + Trt
        # send the token to the next node in the logical ring
        p = Packet(self.env.now, Toh + Ttoken, 0, self.id, self.next, type_id=1)
        dtrans = p.size / Bandwidth
        yield self.env.timeout(dtrans)
        self.bus.send(p)
