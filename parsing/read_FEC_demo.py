from form_parser import form_parser
from filing import filing

# load up a form parser
fp = form_parser()



filingnumbers=(767585, 800502, 808218, 842576, 841933) 

for filingnum in filingnumbers:
    f1 = filing(filingnum)
    formtype = f1.get_form_type()
    version = f1.version

    print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)
    if f1.is_amendment:
        print "Original filing is: %s" % (filing.headers['filing_amended'])
    
    
    if not fp.is_allowed_form(formtype):
        print "skipping form %s - %s isn't parseable" % (f1.filing_number, formtype)
        continue
        
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
            #print linedict
        except ParserMissingError:
            msg = 'process_filing_body: Unknown line type in filing %s line %s: type=%s Skipping.' % (filingnum, linenum, row[0])
            continue