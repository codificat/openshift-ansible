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

class FilterModule(object):
    def filters(self):
        return {'ptr_record': ptr_record}
