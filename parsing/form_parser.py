"""
Load up line parsers for the forms that we care about.
By keeping them in one central wrapper class we don't have to keep initializing them.
"""

import re
from parsing.line_parser import line_parser


class ParserMissingError(Exception):
 pass


class BaseParser(object):
    """
    Base class both the form_parser and paper_form_parser can inherit from.
    """

    def is_allowed_form(self, form_name):
        """
        Checks the top level form name but not the individual lines by testing the 'base' form as returned 
        by filing.get_form_type(), i.e. with the trailing A|N|T designator removed.
        """
        try:
            self.allowed_forms[form_name]
            return True

        except KeyError:
            return False

    def get_line_parser(self, form_type):
        """
        Ignore some v6.4 debt reporting cycles.
        'SC/10' and 'SC/12' are line types from v. 6.4, but they can be parsed by 'SC'.
        """
        for regex in self.regex_tuple:

            if re.match(regex,form_type, re.I):
                parser = self.line_dict[regex]
                return parser

        return None
        
    def parse_form_line(self, line_array, version):
        form_type = line_array[0].replace('"', '').upper()
        parser = self.get_line_parser(form_type)

        if parser:
            parsed_line = parser.parse_line(line_array, version)
            parsed_line['form_parser'] = parser.form  # Records the line parser name.
            return parsed_line

        else:
            raise ParserMissingError ("Couldn't find parser for form type %s, v=%s" % (form_type, version))  


class form_parser(BaseParser):
    """ Matches a form to a set of headers, then passes to line_parser for each row."""

    def __init__(self):
        self.allowed_forms = {
            'F3': 1,
            'F3X': 1,
            'F3P': 1,
            'F9': 1,
            'F5': 1,
            'F24': 1, 
            'F6':1,
            'F7':1,
            'F4':1,
            'F3L':1,
            'F13':1,
        }
                
        # F3P periodic presidential filing
        f3p = line_parser('F3P')

        # F3X -- periodic pac filing
        f3x = line_parser('F3X')
        f3ps = line_parser('F3PS')
        
        # F4 inaugural committees
        f4 = line_parser('F4')
        
        # schedules
        sa = line_parser('SchA')
        sa3l = line_parser('SchA3L')
        sb = line_parser('SchB')
        sc1 = line_parser('SchC1')
        sc2 = line_parser('SchC2')
        sc = line_parser('SchC')
        sd = line_parser('SchD')
        se = line_parser('SchE')
        sf = line_parser('SchF')
        h1 = line_parser('H1')
        h2 = line_parser('H2')
        h3 = line_parser('H3')
        h4 = line_parser('H4')
        h5 = line_parser('H5')
        h6 = line_parser('H6')
        sl = line_parser('SchL')
                
        # F24 -- 24 hr ie report
        f24 = line_parser('F24')

        #F9 -- Electioneering communication
        f9 = line_parser('F9')
        f91 = line_parser('F91')
        f92 = line_parser('F92')
        f93 = line_parser('F93')
        f94 = line_parser('F94')

        # IE report by non-committee, roughly
        f5 = line_parser('F5')
        f56 = line_parser('F56')
        f57 = line_parser('F57')
        
        # 48-hr report from candidate committee
        f6 = line_parser('F6')
        f65 = line_parser('F65')
        
        # communication cost - these are typically filed in print
        f7 = line_parser('F7')
        f76 = line_parser('F76')
        
        # F3 Periodic report for candidate
        f3 = line_parser('F3')
        f3s = line_parser('F3S')
        
        # lobbyist bundling
        f3l = line_parser('F3L')

        # Allow text in lines
        text = line_parser('TEXT')
        
        f13 = line_parser('F13')
        f132 = line_parser('F132')
        f133 = line_parser('F133')

        # match form type to appropriate parsers; must be applied with re.I
        # the leading ^ are redundant if we're using re.match, but...
        self.line_dict = {
            '^SA': sa,
            '^SB': sb,
            '^SC': sc,
            '^SC1': sc1,
            '^SC2': sc2,
            '^SD': sd,
            '^SE': se,
            '^SF': sf,
            '^SL':sl,
            '^H1':h1,
            '^H2':h2,
            '^H3':h3,
            '^H4':h4,
            '^H5':h5,
            '^H6':h6,
            '^F3X[A|N|T]': f3x,
            '^F3P[A|N|T]': f3p,
            '^F3L[A|N]':f3l,
            '^F4[A|N|T]': f4,
            '^F3PS':f3ps,
            '^F3S': f3s,
            '^F3[A|N|T]$': f3,
            '^F6[A|N]*$':f6,
            '^F65':f65,
            '^F91': f91,
            '^F92': f92,
            '^F93': f93,
            '^F94': f94,
            '^F9': f9,
            '^F57': f57,
            '^F56': f56,            
            '^F5': f5,
            '^TEXT': text,
            '^F24': f24,
            '^F7[A|N]$': f7,
            '^F76$': f76,
            '^SA3L':sa3l,
            '^F13[A|N]$':f13,
            '^F132':f132,
            '^F133':f133,
        }

        # The regex parsers must be tested in a certain order and must be an exact match, since it will use the
        # resulting headers as the keys in the output dictionaries.
        self.regex_tuple = ('^SA3L','^SA','^SB','^SC1','^SC2','^SC','^SD','^SE','^SF','^F3X[A|N|T]','^F3P[A|N|T]','^F3S','^F3[A|N|T]$','^F91','^F92','^F93','^F94','^F9','^F6[A|N]*$','^F65','^F57','^F56','^F5','^TEXT','^F24','^H1','^H2','^H3','^H4','^H5','^H6','^SL','^F3PS','^F76$','^F7[A|N]$','^F4[A|N|T]','^F3L[A|N]','^F13[A|N]$','^F132','^F133')


class paper_form_parser(BaseParser):

    def __init__(self):
        """
        There are SC1 and SC2 variants that should be ignored. 
        """
        self.allowed_forms = {
            'F3': 1,
            'F3X':1,
        }
        
        # F3X -- periodic pac filing.
        f3x = line_parser('F3X', True)
        f3 = line_parser('F3', True)
        sa = line_parser('SchA', True)
        sb = line_parser('SchB', True)
        sc = line_parser('SchC', True)
        sd = line_parser('SchD', True)
        se = line_parser('SchE', True)

        # Match form type to appropriate parsers; must be applied with re.I
        self.line_dict = {
            '^SA': sa,
            '^SB': sb,
            '^SC\/': sc,
            '^SD': sd,
            '^SE': se,
            '^F3[A|N|T]$': f3,
            '^F3X[A|N|T]$': f3x,
        }

        # The regex parsers must be tested in a certain order and must be an exact match, since it will use the
        # resulting headers as the keys in the output dictionaries.
        self.regex_tuple = ('^F3X[A|N|T]$','^F3[A|N|T]$','^SB','^SA','^SE','^SD','^SC\/')
