#!/usr/bin/env python
#----------------------------------------------------------------------
# Utility to reparse the schemas and determine which DTDs are out of
# date in the manifest for the client.
#----------------------------------------------------------------------

import sys
from lxml import etree
import cdr

CLIENT_FILES_DIR = len(sys.argv) > 1 and sys.argv[1] or cdr.CLIENT_FILES_DIR
def getDocTypeResponses(docType):
    opts = dict(Type=docType, OmitDtd="Y", GetEnumValues="Y")
    cmd = etree.Element("CdrGetDocType", **opts)
    commands = etree.Element("CdrCommandSet")
    etree.SubElement(commands, "SessionId").text = "guest"
    wrapper = etree.SubElement(commands, "CdrCommand")
    wrapper.append(cmd)
    response = cdr._Control.send_commands(commands)
    xml = etree.tostring(response.node, encoding="utf-8")
    start = xml.find('<CdrGetDocTypeResp')
    if start < 0:
        sys.stderr.write("CdrGetDocType FAILURE: " + xml + "\n")
        raise Exception("CdrGetDocType FAILURE: " + xml)
    end = xml.find('</CdrGetDocTypeResp>')
    if not end:
        sys.stderr.write("CdrGetDocType FAILURE: " + xml + "\n")
        raise Exception("CdrGetDocType FAILURE: " + xml)
    return xml[start:end] + '</CdrGetDocTypeResp>\n'

def saveDocTypeResponses(docTypeFilePath, docTypeResponses):
    f = file(docTypeFilePath, 'wb')
    f.write(docTypeResponses)
    f.close()

def loadDocTypeResponses(docTypeFilePath):
    f = file(docTypeFilePath, 'rb')
    docTypeResponses = f.read()
    f.close()
    return docTypeResponses

directory       = '%s/Rules' % CLIENT_FILES_DIR
docTypeFileName = 'CdrDocTypes.xml'
docTypeFilePath = '%s/%s' % (CLIENT_FILES_DIR, docTypeFileName)
docTypes = cdr.getDoctypes('guest')
docTypeResponses = ['<DocTypeResponses>\n']
for docType in docTypes:
    if docType.upper() in ("FILTER", "CSS", "SCHEMA"): continue
    try:
        dtInfo = cdr.getDoctype('guest', docType)
        docTypeResponses.append(getDocTypeResponses(docType))
        #sys.stderr.write("new DTD retrieved\n")
        if not dtInfo.dtd:
            sys.stderr.write("Can't get new DTD for %s\n" % repr(docType))
            continue
        start = dtInfo.dtd.find("<!ELEMENT")
        #sys.stderr.write("new start is at %d\n" % start)
        if start == -1:
            sys.stderr.write("Malformed DTD for %s type\n" % repr(docType))
            #print dtInfo.dtd
            continue
        newDtd = dtInfo.dtd[start:]
        path = "%s/%s.dtd" % (directory, docType)
        #sys.stderr.write("checking %s\n" % path)
        try:
            current = open(path).read()
        except Exception as e:
            sys.stderr.write("failure opening %s: %s\n" % (path, str(e)))
            current = None
        #sys.stderr.write("old DTD read\n")
        if current:
            start = current.find('<!ELEMENT')
            if start == -1:
                sys.stderr.write("Malformed DTD: %s.dtd\n" % docType)
                continue
            #sys.stderr.write("old start is at %d\n" % start)
            current = current[start:]
            if newDtd == current:
                print "DTD for %25s  is current" % docType
                continue
            else:
                print "DTD for %25s has changed" % docType
        else:
            print "DTD for %25s     added" % docType
        try:
            open(path, "w").write(dtInfo.dtd)
        except Exception as e:
            sys.stderr.write("failure writing %s: %s\n" % (path, str(e)))
    except Exception, e:
        sys.stderr.write(str(e) + "\n")
        #pass
docTypeResponses.append('</DocTypeResponses>\n')
docTypeResponses = "".join(docTypeResponses)
try:
    if loadDocTypeResponses(docTypeFilePath) != docTypeResponses:
        print "%s changed" % repr(docTypeFileName)
        saveDocTypeResponses(docTypeFilePath, docTypeResponses)
    else:
        print "%s unchanged" % repr(docTypeFileName)
except:
    print "saving new %s" % repr(docTypeFileName)
    saveDocTypeResponses(docTypeFilePath, docTypeResponses)
print "*** DON'T FORGET TO RUN RefreshManifest.py IF APPROPRIATE! ***"