#!/usr/bin/env python
#######################################################
# Get one XML document from pub_proc_cg to stdout
#######################################################
import sys, cdrdb, cdr

if len(sys.argv) != 2:
    sys.stderr.write("usage: getPubProcCGdoc.py docId\n")
    sys.stderr.write("       Enter docId as plain integer\n")
    sys.stderr.write("       Writes xml to stdout\n")
    sys.exit(1)

docId = int(sys.argv[1])

conn = cdrdb.connect("CdrGuest")
cursor = conn.cursor()
cursor.execute("SELECT xml FROM pub_proc_cg WHERE id=%d" % docId)
row = cursor.fetchone()
if not row:
    sys.stderr.write("Doc %d not found in pub_proc_cg")
    sys.exit(1)
print(row[0].encode("utf-8"))

