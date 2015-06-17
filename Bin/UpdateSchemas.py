# ************************************************************************
# $Id$
#
# Program to replace a schema in the CDR database with a version found in
# a file, typically a file in a version control sandbox.
#
# Versions in the file should not have CdrDoc wrappers.  The wrapper is added
# by this program.
#
# Matching is done by searching the database for the name of the file, e.g.,
# "SummarySchema.xml", matching it against the title of the document
# in the database version of the document.  That title is created by
# this UpdateSchemas.py program - which should always be used when a schema
# update is required.
#
# If no match is found, we assume that the schema in the file is new.  It will
# be inserted into the database as a new schema document.
# ************************************************************************
import cdr, sys, glob

# Checking for sufficient command line arguments
# ----------------------------------------------
if len(sys.argv) < 4:
    print "usage: UpdateSchemas user-id password schema [schema ...]"
    sys.exit(1)

# Creating a session ID to access the CDR database
# ------------------------------------------------
session = cdr.login(sys.argv[1], sys.argv[2])
err = cdr.checkErr(session)
if err:
    print "failure logging in: " % err
    sys.exit(1)

# Stepping through the command line arguments (i.e. schema files)
# for processing
# If the schema doesn't exist in the CDR it will be added,
# otherwise the existing schema file will be replaced.
# --------------------------------------------------------------
for token in sys.argv[3:]:
    schemas = glob.glob(token)
    if not schemas:
        print "Schema file not in cwd: %s" % token
        sys.exit(1)

    for schema in schemas:
        print "schema: %s" % schema
        query = "CdrCtl/Title = '%s' and CdrCtl/DocType = 'schema'" % schema
        results = cdr.search(session, query)

        # Schema doesn't exist yet - create new in the CDR
        # ------------------------------------------------
        if len(results) < 1:
            doc = """\
<CdrDoc Type='schema' Id=''>
 <CdrDocCtl>
  <DocTitle>%s</DocTitle>
 </CdrDocCtl>
 <CdrDocXml><![CDATA[%s]]></CdrDocXml>
</CdrDoc>
""" % (schema, open(schema).read())
            id = cdr.addDoc(session, doc = doc, checkIn = 'Y', ver = 'Y')
            print "addDoc: " + id
        # Schema already exists and needs to be replaced.
        # -----------------------------------------------
        else:
            for result in results:
                doc = cdr.getDoc(session, result.docId, 'Y', getObject = 1)
                if type(doc) == type(""):
                    print "getDoc(%s): %s" % (result.docId, doc)
                else:
                    doc = """\
<CdrDoc Type='schema' Id='%s'>
 <CdrDocCtl>
  <DocTitle>%s</DocTitle>
 </CdrDocCtl>
 <CdrDocXml><![CDATA[%s]]></CdrDocXml>
</CdrDoc>
""" % (result.docId, schema, open(schema).read())
                    id = cdr.repDoc(session, doc = doc, checkIn='Y', ver = 'Y')
                    print "repDoc(%s): %s" % (result.docId, id)
cdr.logout(session)
