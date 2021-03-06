#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller,RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from time import sleep
setLogLevel('info')
n_hosts=30
assert n_hosts > 1
net = Containernet(controller=Controller)
info('*** Adding controller\n')
c0 = RemoteController( 'c0', ip='127.0.0.1' )
net.addController(c0)
info('*** Adding docker containers\n')

docker_hosts=[net.addDocker('d1', ip='10.0.0.1', dimage="hadoop:new",cpuset_cpus="0,1",ports=[8088, 50070], port_bindings={8088:8088,50070:50070},)]
switches = [net.addSwitch('s1')]
net.addLink(docker_hosts[-1], switches[-1])
cpu_set=(2, 3)
for i in range(2,n_hosts+1):
    docker_hosts.append(net.addDocker('d{}'.format(i), ip='10.0.0.{}'.format(i),
                                      dimage="hadoop:new",cpuset_cpus="{},{}".format(cpu_set[0],cpu_set[1]),
                                      mem_limit="6500m", memswap_limit="50m"))
    switches.append(net.addSwitch('s{}'.format(i)))
    net.addLink(docker_hosts[-1], switches[-1])
    cpu_set = cpu_set[0]+2,cpu_set[1]+2
    if cpu_set[1] > 35:
        cpu_set = (0, 1)
info('*** Creating switch links\n')
for s1,s2 in zip(switches[:-1],switches[1:]):
    net.addLink(s1, s2, cls=TCLink, bw=1000)

info('*** Starting network\n')
net.start()


master = docker_hosts[0]
workers = docker_hosts[1:]

#   StrictHostKeyChecking no
master.cmd("""bash -c "echo '10.0.0.1' >> /usr/local/hadoop/etc/hadoop/masters" """)
for host in docker_hosts:
    host.cmd("""bash -c "echo '    StrictHostKeyChecking no' >> /etc/ssh/ssh_config" """)
    host.cmd("service ssh start")
    host.cmd("""bash -c "echo '10.0.0.1 master ' >> /etc/hosts" """)
    host.cmd("""bash -c "echo '10.0.0.1 hadoop-master ' >> /etc/hosts" """)


w_ips=[]
for w in workers:
    ip = w.IP()
    w_ips.append(ip)
    master.cmd("""bash -c "echo '{}' >> /usr/local/hadoop/etc/hadoop/slaves" """.format(w))

#for wor in workers:
#    for ip in w_ips:
#        wor.cmd("""bash -c "echo '{}' >> /usr/local/hadoop/etc/hadoop/slaves" """.format(w))

for wor in docker_hosts:
    wor.cmd("""bash -c "echo '10.0.0.1  d1' >> /etc/hosts" """.format(w))
    for w in workers:
        wor.cmd("""bash -c "echo '{} {}' >> /etc/hosts" """.format(w.IP(), w))

        wor.cmd("""bash -c "echo '{}' >> /usr/local/hadoop/etc/hadoop/slaves" """.format(w))

info ("# DO PINGALL\n")
net.pingAllFull()

info ("# Start Hadoop in the cluster\n")
info ("# Format HDFS\n")
info (master.cmd('bash -c "/usr/local/hadoop/bin/hdfs namenode -format -force"'))
sleep(2)
info ("# Launch HDFS\n")
info (master.cmd('bash -c "/usr/local/hadoop/sbin/start-dfs.sh"'))
sleep(2)
info ("# Launch YARN\n")
info (master.cmd('bash -c "/usr/local/hadoop/sbin/start-yarn.sh"'))
sleep(2)
info ("# Create a directory for the user\n")
info (master.cmd('bash -c "/usr/local/hadoop/bin/hdfs dfs -mkdir -p /user/root"'))
sleep(2)
pi_cmd="hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar pi  400 400"
info (master.cmd(pi_cmd))


info('*** Running CLI\n')
#CLI(net)
info('*** Stopping network')
net.stop()


'''
w_ips=[]
for w in workers:
    ip = w.IP()
    w_ips.append(ip)
    master.cmd("""bash -c "echo '{}' >> /root/hadoop-2.7.6/etc/hadoop/slaves" """.format(ip))

for wor in workers:
    for ip in w_ips:
        wor.cmd("""bash -c "echo '{}' >> /root/hadoop-2.7.6/etc/hadoop/slaves" """.format(ip))


info ("# Start Hadoop in the cluster\n")
info ("# Format HDFS\n")
info (master.cmd('bash -c "/root/hadoop-2.7.6/bin/hdfs namenode -format -force"'))
sleep(2)
info ("# Launch HDFS\n")
info (master.cmd('bash -c "/root/hadoop-2.7.6/sbin/start-dfs.sh"'))
sleep(2)
info ("# Launch YARN\n")
info (master.cmd('bash -c "/root/hadoop-2.7.6/sbin/start-yarn.sh"'))
sleep(2)
info ("# Create a directory for the user\n")
info (master.cmd('bash -c "/root/hadoop-2.7.6/bin/hdfs dfs -mkdir -p /user/root"'))
sleep(1)
pi_cmd="/root/hadoop-2.7.6/bin/hadoop jar  /root/hadoop-2.7.6/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.6.jar pi 20 100"
#info (master.cmd(pi_cmd))
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
'''
