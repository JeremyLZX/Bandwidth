#run scapy
# send some packets, sniff the reply

# note: the P4 program will clear mac src/dst addr to 0, which is used for separating replies from responses.

from scapy.all import *
import time
import sys

def int_to_mac(i):
    #start from lower
    def to_two_hex(num):
        assert(0<=num<=255)
        return hex(256+num)[-2:]
    ret=[]
    for _ in range(6):
        remainder=i%256
        ret.append(to_two_hex(remainder))
        i=i//256
    return ':'.join(reversed(ret))

def int_to_ip(i):
    ret=[]
    for _ in range(4):
        remainder=i%256
        ret.append(str(remainder))
        i=i//256
    return '.'.join(reversed(ret))

def ip_to_int(ip):
    numarr=[int(x) for x in ip.split('.')]
    ret=0
    for i in numarr:
        ret*=256
        ret+=i
    return ret

def build_input_packet(id,numerator,denominator,t_mid,delta_t_log,interp_op):
    assert(t_mid > 2**delta_t_log)
    assert(numerator <= denominator <= 2**32)
    assert(interp_op in [1,2])

    return Ether(
        src=int_to_mac(numerator),
        dst=int_to_mac(denominator)
    )/IP(
        id=id,#IPID is used as testcase ID
        src=int_to_ip(t_mid)
    )/UDP(
        sport=delta_t_log,
        dport=interp_op
    )


testcase_list=[
    {"numerator":i*100*1000,"denominator":1000*1000,"t_mid":5000,"delta_t_log":11,"interp_op":1}
    for i in range(10)
]+[
    {"numerator":i*100*1000,"denominator":1000*1000,"t_mid":5000,"delta_t_log":11,"interp_op":2}
    for i in range(10)
]

testcase_input_map={
    idx:build_input_packet(id=idx,**case)
    for idx,case in enumerate(testcase_list)
}
testcase_ans_map={idx:None for idx,case in enumerate(testcase_list)}


iface='veth0'
def sniff_thread(iface, num_wait,end_event):
    #when received >=num_wait responses, set end_event threading.Event
    received_counter={'x':0}
    print('start sniffing, expecting total output:',(num_wait))
    def proc_packet(p):
        #p.show2()
        if p['Ether'].src==int_to_mac(0) and p['Ether'].dst==int_to_mac(0):
            #this is response
            id=p['IP'].id
            ret=p['IP'].dst
            ret_parsed=ip_to_int(ret)
            print('*** got response:',id,ret, ret_parsed)
            testcase_ans_map[id]=ret_parsed
            received_counter['x']+=1
            if received_counter['x'] >= num_wait:
                print('that should be all')
                end_event.set()
        return 
    sniff(iface=iface,prn=proc_packet)

_=sniff(iface=iface,timeout=1) #clear previous packets

wait_event=threading.Event()
t = threading.Thread(target=sniff_thread, args=(iface, len(testcase_list), wait_event))
t.start()
time.sleep(0.5)
#sendp all packet
sendp(list(testcase_input_map.values()), iface=iface)
wait_event.wait()
sys.exit(0)