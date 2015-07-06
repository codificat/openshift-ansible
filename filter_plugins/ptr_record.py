#!/usr/bin/python

def ptr_record(ip):
    # It gets an IPv4 address X.Y.Z.A # and returns only the last byte (A)
    # It treats everything as a string though (not bytes) and
    # doesn't perform any real checks.
    # Meant to be useful while building DNS PTR records e.g.
    # for the zone Z.Y.X.in-addr.arpa.
    index = ip.rfind('.')
    if index > 0:
        return ip[index+1:]
    else:
        return ip

def reverse_zone(subnet):
    # From "192.168.1" it returns "1.168.192.in-addr.arpa"
    zone = subnet.split('.')
    zone.reverse()
    return '.'.join(zone) + ".in-addr.arpa"

class FilterModule(object):
    def filters(self):
        return { 'ptr_record': ptr_record, 'reverse_zone': reverse_zone }
