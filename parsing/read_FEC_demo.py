from form_parser import form_parser, ParserMissingError
from filing import filing

# load up a form parser
fp = form_parser()


# v 3.00 : 23132  
# v 3.00 : 23176
# v 3.00 : 23178
# v 5.3 : 255363
# v 5.3 : 312490
# v 6.1 : 314083
filingnumbers=(23132, 314083) 

for filingnum in filingnumbers:
    f1 = filing(filingnum)
    formtype = f1.get_form_type()
    version = f1.version

    print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)
    print "headers are: %s" % f1.headers
    
    if f1.is_amendment:
        print "Original filing is: %s" % (f1.headers['filing_amended'])
    
    
    if not fp.is_allowed_form(formtype):
        print "skipping form %s - %s isn't parseable" % (f1.filing_number, formtype)
        continue
        
    print "Version is: %s" % (version)
    firstrow = fp.parse_form_line(f1.get_first_row(), version)    
    #print "First row is: %s" % (firstrow)
    
    linenum = 0
    while True:
        linenum += 1
        row = f1.get_body_row()
        if not row:
            break
        
        try:
            linedict = fp.parse_form_line(row, version)
            print linedict
        except ParserMissingError:
            msg = 'process_filing_body: Unknown line type in filing %s line %s: type=%s Skipping.' % (filingnum, linenum, row[0])
            continue