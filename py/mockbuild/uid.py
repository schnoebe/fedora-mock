# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:
# License: GPL2 or later see COPYING
# Written by Michael Brown
# Copyright (C) 2007 Michael E Brown <mebrown@michaels-house.net>

import os
import ctypes

from .trace_decorator import traceLog

_libc = ctypes.CDLL(None, use_errno=True)

# class
class UidManager(object):
    @traceLog()
    def __init__(self, unprivUid=-1, unprivGid=-1):
        self.privStack = []
        self.unprivUid = unprivUid
        self.unprivGid = unprivGid

    @traceLog()
    def becomeUser(self, uid, gid=-1):
        # save current ruid, euid, rgid, egid
        self._push()
        self._becomeUser(uid, gid)

    @traceLog()
    def dropPrivsTemp(self):
        # save current ruid, euid, rgid, egid
        self._push()
        self._becomeUser(self.unprivUid, self.unprivGid)

    @traceLog()
    def restorePrivs(self):
        # back to root first
        self._elevatePrivs()

        # then set saved
        privs = self.privStack.pop()
        os.setregid(privs['rgid'], privs['egid'])
        setresuid(privs['ruid'], privs['euid'])

    @traceLog()
    def dropPrivsForever(self):
        self._elevatePrivs()
        os.setregid(self.unprivGid, self.unprivGid)
        os.setreuid(self.unprivUid, self.unprivUid)

    @traceLog()
    def _push(self):
         # save current ruid, euid, rgid, egid
        self.privStack.append({
            "ruid": os.getuid(),
            "euid": os.geteuid(),
            "rgid": os.getgid(),
            "egid": os.getegid(),
            })

    @traceLog()
    def _elevatePrivs(self):
        setresuid(0, 0, 0)
        os.setregid(0, 0)

    @traceLog()
    def _becomeUser(self, uid, gid=None):
        self._elevatePrivs()
        if gid is not None:
            os.setregid(gid, gid)
        setresuid(uid, uid, 0)

    @traceLog()
    def changeOwner(self, path, uid=None, gid=None, recursive=False):
        self._elevatePrivs()
        if uid is None:
            uid = self.unprivUid
        if gid is None:
            gid = self.unprivGid
        os.chown(path, uid, gid)
        if recursive:
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    os.chown(os.path.join(root, d), uid, gid)
                for f in files:
                    os.chown(os.path.join(root, f), uid, gid)

def getresuid():
    ruid = ctypes.c_long()
    euid = ctypes.c_long()
    suid = ctypes.c_long()
    res = _libc.getresuid(ctypes.byref(ruid), ctypes.byref(euid), ctypes.byref(suid))
    if res:
        raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
    return (ruid.value, euid.value, suid.value)

def setresuid(ruid=-1, euid=-1, suid=-1):
    ruid = ctypes.c_long(ruid)
    euid = ctypes.c_long(euid)
    suid = ctypes.c_long(suid)
    res = _libc.setresuid(ruid, euid, suid)
    if res:
        raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))

def getresgid():
    rgid = ctypes.c_long()
    egid = ctypes.c_long()
    sgid = ctypes.c_long()
    res = _libc.getresgid(ctypes.byref(rgid), ctypes.byref(egid), ctypes.byref(sgid))
    if res:
        raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
    return (rgid.value, egid.value, sgid.value)

def setresgid(rgid=-1, egid=-1, sgid=-1):
    rgid = ctypes.c_long(rgid)
    egid = ctypes.c_long(egid)
    sgid = ctypes.c_long(sgid)
    res = _libc.setresgid(rgid, egid, sgid)
    if res:
        raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))

