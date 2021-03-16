# Token Bus Simulation

This project is a simulation of the IEEE 802.4 Token Bus Protocol in a distributed real-time system, for a number of load factors. It was developed using the Discrete Event Simulation (DES) python framework SimPy.

## Simulation Model

The model follows the IEEE 802.4 standard, but the following conditions are applied:
<ol type="a">
  <li>The number of nodes remains constant during the simulation.</li>
  <li>The nodes operate without fault during the simulation.</li>
  <li>There is no noise in the channel.</li>
  <li>Only messages of Class A and Class B are transmitted.</li>
</ol>

## Parameter Selection

The simulation parameters, such as channel bandwidth, mean packet size, token size, packet size distribution and packet time distribution follow <a href="https://ieeexplore.ieee.org/abstract/document/31502">this article</a>.<br>
The main parameters that change the behaviour and determine whether the protocol is fit for real-time application are the two timer parameters. These two, along with the number of nodes, can be changed from the User Interface.

## Instructions

Once the application is started, the user can choose the simulation parameters, or leave them to their default values, and click the button to start the simulations. After the ten simulations are over, two figures will be presented showing the variation of the system and the per node delay with the load factor, for the two different classes of messages.<br>
The user can experiment with different values and see the network's behaviour on real time control messages (class A) and on data messages (class B).