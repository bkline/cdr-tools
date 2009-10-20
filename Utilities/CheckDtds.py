#----------------------------------------------------------------------
#
# $Id$
#
# Utility to reparse the schemas and determine which DTDs are out of
# date in the manifest for the client.
#
# $Log: not supported by cvs2svn $
# Revision 1.8  2006/06/08 22:25:12  bkline
# Added code to pack up more doctype info for the client.
#
# Revision 1.7  2006/01/31 19:10:03  bkline
# Modified to use new client files area.
#
# Revision 1.6  2005/08/10 21:13:22  venglisc
# Minor changes to format the output.
#
# Revision 1.5  2003/04/08 18:40:14  bkline
# Better error handling reading old DTD.
#
# Revision 1.4  2002/08/30 16:32:35  bkline
# Removed hardcoded CDR account credentials.
#
# Revision 1.3  2002/06/27 20:35:40  bkline
# fixed rules path
#
# Revision 1.2  2002/06/27 19:30:36  bkline
# Added command-line argument for www path base.
#
# Revision 1.1  2002/06/06 15:44:00  bkline
# Utility to bring client DTDs up to date.
#
#----------------------------------------------------------------------

import cdr, sys

def getDocTypeResponses(docType):
    cmd = "<CdrGetDocType Type='%s' OmitDtd='Y' GetEnumValues='Y'/>" % docType
    response = cdr.sendCommands(cdr.wrapCommand(cmd, 'guest'))
    start = response.find('<CdrGetDocTypeResp')
    if not start:
        sys.stderr.write("CdrGetDocType FAILURE: " + response + "\n")
        raise Exception("CdrGetDocType FAILURE: " + response)
    end = response.find('</CdrGetDocTypeResp>')
    if not end:
        sys.stderr.write("CdrGetDocType FAILURE: " + response + "\n")
        raise Exception("CdrGetDocType FAILURE: " + response)
    return response[start:end] + '</CdrGetDocTypeResp>\n'

def saveDocTypeResponses(docTypeFilePath, docTypeResponses):
    f = file(docTypeFilePath, 'wb')
    f.write(docTypeResponses)
    f.close()

def loadDocTypeResponses(docTypeFilePath):
    f = file(docTypeFilePath, 'rb')
    docTypeResponses = f.read()
    f.close()
    return docTypeResponses

directory       = '%s/Rules' % cdr.CLIENT_FILES_DIR
docTypeFileName = 'CdrDocTypes.xml'
docTypeFilePath = '%s/%s' % (cdr.CLIENT_FILES_DIR, docTypeFileName)
docTypes = cdr.getDoctypes('guest')
docTypeResponses = ['<DocTypeResponses>\n']
for docType in docTypes:
    if docType.upper() in ("FILTER", "CSS"): continue
    try:
        dtInfo = cdr.getDoctype('guest', docType)
        docTypeResponses.append(getDocTypeResponses(docType))
        #sys.stderr.write("new DTD retrieved\n")
        if not dtInfo.dtd:
            sys.stderr.write("Can't get new DTD for %s\n" % docType)
            continue
        start = dtInfo.dtd.find("<!ELEMENT")
        #sys.stderr.write("new start is at %d\n" % start)
        if start == -1:
            sys.stderr.write("Malformed DTD for %s type\n" % docType)
            #print dtInfo.dtd
            continue
        newDtd = dtInfo.dtd[start:]
        path = "%s/%s.dtd" % (directory, docType)
        #sys.stderr.write("checking %s\n" % path)
        try:
            current = open(path).read()
        except:
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
        except:
            sys.stderr.write("failure writing %s\n" % path)
    except Exception, e:
        sys.stderr.write(str(e))
        #pass
docTypeResponses.append('</DocTypeResponses>\n')
docTypeResponses = "".join(docTypeResponses)
try:
    if loadDocTypeResponses(docTypeFilePath) != docTypeResponses:
        print "%s changed" % docTypeFileName
        saveDocTypeResponses(docTypeFilePath, docTypeResponses)
    else:
        print "%s unchanged" % docTypeFileName
except:
    print "saving new %s" % docTypeFileName
    saveDocTypeResponses(docTypeFilePath, docTypeResponses)
print "*** DON'T FORGET TO RUN RefreshManifest.py IF APPROPRIATE! ***"
