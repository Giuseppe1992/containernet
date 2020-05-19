#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')
n_hosts=10
assert n_hosts > 1
net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
docker_hosts=[net.addDocker('d1', ip='10.0.0.1', dimage="master:latest")]
switches = [net.addSwitch('s1')]
net.addLink(docker_hosts[-1], switches[-1])
for i in range(2,n_hosts+1):
    docker_hosts.append(net.addDocker('d{}'.format(i), ip='10.0.0.{}'.format(i), dimage="worker:latest"))
    switches.append(net.addSwitch('s{}'.format(i)))
    net.addLink(docker_hosts[-1], switches[-1])
info('*** Creating switch links\n')
for s1,s2 in zip(switches[:-1],switches[1:]):
    net.addLink(s1, s2, cls=TCLink, bw=100)

info('*** Starting network\n')
net.start()
for host in docker_hosts:
    host.cmd("service ssh start")

master = docker_hosts[0]
workers = docker_hosts[1:]

master.cmd("""bash -c "echo '127.0.0.1 master ' >> /etc/hosts" """)

info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()

