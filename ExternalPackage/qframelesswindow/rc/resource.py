# -*- coding: utf-8 -*-

# Resource object code
#
# Created by: The Resource Compiler for PyQt5 (Qt v5.15.2)
#
# WARNING! All changes made in this file will be lost!

#from PyQt5 import QtCore
from PySide2 import QtCore
qt_resource_data = b"\
\x00\x00\x01\x0e\
\x3c\
\x73\x76\x67\x20\x77\x69\x64\x74\x68\x3d\x22\x34\x35\x70\x74\x22\
\x20\x68\x65\x69\x67\x68\x74\x3d\x22\x33\x30\x70\x74\x22\x20\x76\
\x65\x72\x73\x69\x6f\x6e\x3d\x22\x31\x2e\x31\x22\x20\x76\x69\x65\
\x77\x42\x6f\x78\x3d\x22\x30\x20\x30\x20\x31\x35\x2e\x38\x37\x35\
\x20\x31\x30\x2e\x35\x38\x33\x22\x20\x78\x6d\x6c\x6e\x73\x3d\x22\
\x68\x74\x74\x70\x3a\x2f\x2f\x77\x77\x77\x2e\x77\x33\x2e\x6f\x72\
\x67\x2f\x32\x30\x30\x30\x2f\x73\x76\x67\x22\x3e\x0d\x0a\x20\x3c\
\x67\x20\x66\x69\x6c\x6c\x3d\x22\x6e\x6f\x6e\x65\x22\x20\x73\x74\
\x72\x6f\x6b\x65\x3d\x22\x23\x30\x30\x30\x22\x20\x73\x74\x72\x6f\
\x6b\x65\x2d\x77\x69\x64\x74\x68\x3d\x22\x2e\x31\x37\x36\x33\x39\
\x22\x3e\x0d\x0a\x20\x20\x3c\x70\x61\x74\x68\x20\x64\x3d\x22\x6d\
\x36\x2e\x31\x32\x39\x35\x20\x33\x2e\x36\x36\x30\x31\x20\x33\x2e\
\x32\x36\x33\x32\x20\x33\x2e\x32\x36\x33\x32\x7a\x22\x2f\x3e\x0d\
\x0a\x20\x20\x3c\x70\x61\x74\x68\x20\x64\x3d\x22\x6d\x39\x2e\x33\
\x39\x32\x37\x20\x33\x2e\x36\x36\x30\x31\x2d\x33\x2e\x32\x36\x33\
\x32\x20\x33\x2e\x32\x36\x33\x32\x7a\x22\x2f\x3e\x0d\x0a\x20\x3c\
\x2f\x67\x3e\x0d\x0a\x3c\x2f\x73\x76\x67\x3e\x0d\x0a\
"

qt_resource_name = b"\
\x00\x10\
\x0a\xb5\xe4\x07\
\x00\x71\
\x00\x66\x00\x72\x00\x61\x00\x6d\x00\x65\x00\x6c\x00\x65\x00\x73\x00\x73\x00\x77\x00\x69\x00\x6e\x00\x64\x00\x6f\x00\x77\
\x00\x09\
\x06\x98\x8e\xa7\
\x00\x63\
\x00\x6c\x00\x6f\x00\x73\x00\x65\x00\x2e\x00\x73\x00\x76\x00\x67\
"

qt_resource_struct_v1 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x26\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

qt_resource_struct_v2 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x26\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x85\x86\x8c\x35\x15\
"

qt_version = [int(v) for v in QtCore.qVersion().split('.')]
if qt_version < [5, 8, 0]:
    rcc_version = 1
    qt_resource_struct = qt_resource_struct_v1
else:
    rcc_version = 2
    qt_resource_struct = qt_resource_struct_v2

def qInitResources():
    QtCore.qRegisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
