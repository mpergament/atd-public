import sys, jsonrpclib
sys.path.append('/usr/lib64/python2.7/site-packages/')
import yaml
from cvplibrary import CVPGlobalVariables as cvpGV
from cvplibrary import GlobalVariableNames as GVN

def sendCmd(commands):
  ztp = cvpGV.getValue(GVN.ZTP_STATE)
  hostip = cvpGV.getValue(GVN.CVP_IP)
  if ztp == 'true':
    user = cvpGV.getValue(GVN.ZTP_USERNAME)
    passwd = cvpGV.getValue(GVN.ZTP_PASSWORD)
  else:
    user = cvpGV.getValue(GVN.CVP_USERNAME)
    passwd = cvpGV.getValue(GVN.CVP_PASSWORD)
    
  url = "https://%s:%s@%s/command-api" % (user, passwd, hostip)
  switch = jsonrpclib.Server(url)
  response = switch.runCmds(1, commands)[0]
  return response


hostname = sendCmd(['show hostname'])['hostname']
f = open('hostvars/%s.yml' % hostname )
info = yaml.load(f)

if 'interfaces' not in info.keys():
  print ''
else:
  print 'ip routing'
  print '!'
  for d in info['interfaces']:
    print 'interface %s' % d['interface']
    if 'Loopback' not in d['interface']:
      print '   no switchport'
    print '   ip address %s/%s' % (d['ip'], d['cidr'])
    print '!'

if 'bgp' not in info.keys():
  print ''
else:
  print 'router bgp %s' % info['bgp']['as']
  print '   maximum-paths 4 ecmp 4'
  for d in info['bgp']['bgp_neighbors']:
    print '   neighbor %s remote-as %s' % (d['ip'], d['remote-as'])
  for n in info['bgp']['networks']:
    if n == '172.16.134.0/24' or n == '172.16.112.0/24':
      continue
    print '   network %s' % n
  print '!'

if 'mlag' not in info.keys():
  print ''
elif 'spine' in hostname:
  print ''
else:
  print 'vlan %s' % info['mlag']['peer_vlan']
  print '   name MLAGPeerLink'
  print '   trunk group mlagPeer'
  print '!'
  print 'no spanning-tree vlan %s' % info['mlag']['peer_vlan']
  print '!'
  for i in info['mlag']['peer_interfaces']:
    print 'interface %s' % i
    print '   channel-group %s mode active' % info['mlag']['peer_link'].replace('Port-Channel','')
    print '!'
    
  print 'interface %s' % info['mlag']['peer_link']
  print '   description MLAGPeerLink'
  print '   switchport mode trunk'
  print '   switchport trunk group mlagPeer'
  print '!'
  
  print 'interface Vlan%s' % info['mlag']['peer_vlan']
  print '   description MLAGPeerIP'
  print '   ip address %s/%s' % (info['mlag']['ip'], info['mlag']['cidr'])
  print '!'
  
  print 'mlag configuration'
  print '   domain %s' % info['mlag']['domain']
  print '   local-interface Vlan%s' % info['mlag']['peer_vlan']
  print '   peer-address %s' % info['mlag']['peer_ip']
  print '   peer-link %s' % info['mlag']['peer_link']
  print '!'
  
  for m in info['mlag']['mlags']:
    for i in m['interfaces']:
      if m['mlag'] == 12 or m['mlag'] == 34:
        continue
      else:
        print 'interface %s' % i
        if (hostname == 'leaf2' and i == 'Ethernet4'):
          print '   shutdown'
        print '   channel-group %s mode active' % m['mlag']
        print '!'
        print 'interface Port-Channel%s' % m['mlag']
        print '   mlag %s' % m['mlag']
        if m['trunk']:
          print '   switchport mode trunk'
        elif m['access']:
          print '   switchport mode access'
          print '   switchport access vlan %s' % m['vlan']
        print '!'

if 'vxlan_svis' not in info.keys():
  print ''
else:
  varp = False    
  for s in info['vxlan_svis']:
    print 'interface Vlan%s' % s['vlan']
    print '   description VLAN%sSVI' % s['vlan']
    print '   ip address %s/%s' % (s['ip'], s['cidr'])
    print '   no autostate'
    if s['varp']:
      varp = True
      print '   ip virtual-router address %s' % s['varp_ip']
    print '!'
  
  if varp:
    print 'ip virtual-router mac-address 00:1C:73:00:00:01'
    print '!'
  
if 'vxlan' not in info.keys():
  print ''
else:
  print 'interface Vxlan1'
  print '   vxlan source-interface %s' % info['vxlan']['vtep']
  print '   vxlan flood vtep %s' % ' '.join(info['vxlan']['flood_vteps'])
  for v in info['vxlan']['vnis']:
    print '   vxlan vlan %s vni %s' % (v['vlan'], v['vni'])
  print '!'
