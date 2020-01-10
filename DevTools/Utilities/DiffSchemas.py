#!/usr/bin/env python
#----------------------------------------------------------------------
#
# Compare schemas in working sandbox with those in the CDR.
# Name individual schema files on the command line or use wildcards.
# If no schemas are named, all files ending in ".xml" in the
# current working directory are compared.  If -q is passed on the
# command line (before any file name patterns), then the program
# only identifies which schema files do not match the corresponding
# CDR document and reports errors.
#
#----------------------------------------------------------------------
import cdr, sys, glob, difflib, os.path

differ = difflib.Differ()
session = 'guest'
quiet = False
if len(sys.argv) > 1 and sys.argv[1] == '-q':
    quiet = True
    sys.argv.remove('-q')
args = sys.argv[1:] or ["*.xml"]
for arg in args:
    for name in glob.glob(arg):
        baseName = os.path.basename(name)
        try:
            localDoc = open(name).read().replace("\r", "").splitlines(True)
        except Exception as e:
            print("... unable to open %s: %s" % (name, e))
            continue
        query = "CdrCtl/Title = {}".format(baseName)
        results = cdr.search(session, query, doctypes=["schema"])
        if len(results) < 1:
            print("... schema %s not found in CDR" % baseName)
        else:
            for result in results:
                if not quiet:
                    print("comparing %s to %s" % (result.docId, name))
                doc = cdr.getDoc(session, result.docId, getObject = True)
                if type(doc) in (str, unicode):
                    print("... getDoc(%s): %s" % (result.docId, doc))
                else:
                    cdrDoc = doc.xml.replace("\r", "").splitlines(True)
                    diffSeq = differ.compare(localDoc, cdrDoc)
                    diff = []
                    for line in diffSeq:
                        if line[0] != ' ':
                            diff.append(line)
                    diff = "".join(diff)

                    # Account for the fact that the final newline is stripped
                    # from the schema when it is stored in the CDR
                    # XXX Find out where this happens and think about whether
                    #     it's appropriate.
                    if diff.endswith("+ \n"):
                        diff = diff[:-3]
                    if quiet:
                        if diff:
                            print("%s does not match %s" % (result.docId, name))
                    elif diff.strip():
                        print(diff)
