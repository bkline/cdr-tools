perl CdrQuery.pl "CdrCtl/DocType = 'Term'" | CdrCmd  | SabCmd filters/ReindexDocs.xsl | CdrCmd >> output\ReindexTest2.out
less output/ReindexTest2.out
