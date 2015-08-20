from django.db import models

class Candidate(models.Model):
    ## This is the human verified field -- see legislators.models.incumbent_challenger
    is_incumbent = models.BooleanField(default=False,help_text="Are they an incumbent? If not, they are a challenger")
    curated_election_year =  models.IntegerField(null=True, help_text="What year is their next election. Set this field--don't overwrite the fec's election year. ")
    display = models.BooleanField(default=False,help_text="Should they be displayed. Use this = False for off cycle candidates.")
    
    # foreign key to district
    # district = models.ForeignKey('District', null=True, help_text="Presidents have no district")

    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")

    not_seeking_reelection = models.BooleanField(default=False,help_text="True if they are an incumbent who is not seeking reelection.")
    other_office_sought = models.CharField(max_length=127, blank=True, null=True, help_text="E.g. are they running for senate?")
    other_fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="If they've declared for another federal position, what is it? This should be the *candidate id* not a committee id. ")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Incumbent name")
    pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent?")
    party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party")
    fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
    pcc = models.CharField(max_length=9, blank=True, null=True, help_text="FEC id for the candidate's primary campaign committee")
    
    # This is displayed--this needs to be maintained.
    election_year = models.PositiveIntegerField(blank=True, null=True, help_text="Year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    # cand_ici comes from the candidate master file, but is basically not accurate.
    # cand_ici = models.CharField(max_length=1, null=True, choices=(('I','Incumbent'), ('C', 'Challenger'), ('O', 'Open Seat')))
    
    
    
    # add on id fields
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    transparencydata_id = models.CharField(max_length=40, default='', null=True)

    #

    slug = models.SlugField()
    
    # independent expenditures data
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
     # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0)

    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    cash_on_hand_date = models.DateField(null=True)
    
    ## these two are currently not populated
    cand_cand_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="contributions from the candidate herself")
    cand_cand_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="loans from the candidate herself")
        

    class Meta:
        unique_together = ('fec_id', 'cycle')


class Committee(models.Model):
    cycle = models.CharField(max_length=4)
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to PCC of senators.")
    is_paper_filer = models.NullBooleanField(null=True, default=False, help_text="True for most senate committees, also NRSC/DSCC, some others.")    
    curated_candidate = models.ForeignKey('Candidate', related_name='related_candidate', null=True, help_text="For house and senate: Only include if it's a P-primary campaign committee or A-authorized campaign committee with the current cycle as appears in the candidate-committee-linkage file. Check this by hand for presidential candidates though, because many committees claim to be authorized by aren't")
    leadership_pac_leader = models.ForeignKey('Candidate', related_name='leadership_candidate', null=True, help_text="If this is a leadership pac with a candidate affilate, put the candidate here.")

    is_dirty = models.NullBooleanField(null=True, default=True, help_text="Do summary numbers need to be recomputed?")    


    # direct from the raw fec table
    name = models.CharField(max_length=255, help_text="The committee name.")
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True, help_text="The FEC id of the filing committee")
    slug = models.SlugField(max_length=255)
    party = models.CharField(max_length=3, blank=True, null=True)
    treasurer = models.CharField(max_length=200, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True, help_text='the state where the pac mailing address is')
    connected_org_name=models.CharField(max_length=200, blank=True, null=True)
    filing_frequency = models.CharField(max_length=1, blank=True, null=True)

    candidate_id = models.CharField(max_length=9,blank=True, null=True)
    candidate_office = models.CharField(max_length=1, blank=True, null=True, help_text="The office of the candidate that this committee supports. Not all committees support candidates.")    


    has_contributions = models.NullBooleanField(null=True, default=False)
    # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total receipts for this committee ceived during the entire cycle. ")
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total disbursements by this committee ceived during the entire cycle")

    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0, help_text="Total outstanding loans as of the cash_on_hand_date")

    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Cash on hand as of the end of committee's most recent periodic report; this date appears as cash_on_hand_date")
    cash_on_hand_date = models.DateField(null=True, help_text="The end of the most recent periodic filing; the date that the cash on hand was reported as of.")

    # independent expenditures
    has_independent_expenditures = models.NullBooleanField(null=True, default=False)
    total_independent_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="Total independent expenditures made this cycle.")
    ie_support_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Democratic candidates")
    ie_oppose_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Democratic candidates")
    ie_support_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Republican candidates")
    ie_oppose_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Republican candidates")
    total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    # Typically only party committees make coordinated expenditures
    # has_coordinated_expenditures = models.NullBooleanField(null=True, default=False)
    # total_coordinated_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    # has_electioneering = models.NullBooleanField(null=True, default=False)
    # total_electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

      ## new

    # what kinda pac is it? 
    # is_superpac = models.NullBooleanField(null=True, default=False)    
    # is_hybrid = models.NullBooleanField(null=True, default=False)  
    # is_noncommittee = models.NullBooleanField(null=True, default=False)

    
    # This needs to be curated to be worthwhile. 
    org_status = models.CharField(max_length=31,
        choices=(('501(c)(4)', '501(c)(4)'),
                 ('501(c)(5)', '501(c)(5)'),
                 ('501(c)(6)', '501(c)(6)'),
                 ('527', '527'),
                 ('LLC', 'LLC'), 
                 ('Other private business', 'Other private business'),
                 ('Public business', 'Public business'),
                 ('Individual', 'individual'),
        ),
        blank=True, null=True, help_text="We're only tracking these for non-committees")

    # what's their orientation
    political_orientation = models.CharField(max_length=1,null=True, help_text="The political orientation of the group, as coded by administrators. This is only added for groups making independent expenditures.", choices=[
                        ('R', 'backs Republicans'),
                        ('D', 'backs Democrats'),
                        ('U', 'unknown'),
                          ])
    political_orientation_verified = models.BooleanField(default=False, help_text="Check this box if the political orientation has been verified by a human")

    designation = models.CharField(max_length=1,
                                  blank=False,
                                  null=True,
                                  choices=[('A', 'Authorized by Candidate'),
                                           ('J', 'Joint Fund Raiser'),
                                           ('P', 'Principal Committee of Candidate'),
                                           ('U', 'Unauthorized'),
                                           ('B', 'Lobbyist/Registrant PAC'),
                                           ('D', 'Leadership PAC')]
    )

    ctype = models.CharField(max_length=1,
                        blank=False,
                        help_text="The FEC defined committee type.",
                        null=True,
                        choices=[('C', 'Communication Cost'),
                                   ('D', 'Delegate'),
                                   ('E', 'Electioneering Communication'),
                                   ('H', 'House'),
                                   ('I', 'Independent Expenditure (Not a Committee'),
                                   ('N', 'Non-Party, Non-Qualified'),
                                   ('O', 'Super PAC'),
                                   ('P', 'Presidential'),
                                   ('Q', 'Qualified, Non-Party'),
                                   ('S', 'Senate'),
                                   ('U', 'Single candidate independent expenditure'),
                                   ('V', 'PAC with Non-Contribution Account - Nonqualified'),
                                   ('W', 'PAC with Non-Contribution Account - Qualified'),
                                   ('X', 'Non-Qualified Party'),
                                   ('Y', 'Qualified Party'),
                                   ('Z', 'National Party Organization') ])  

    class Meta:
        unique_together = (("cycle", "fec_id"),)
        ordering = ('-total_indy_expenditures', )


class Filing(models.Model):
    """
    There's no foreign key to a committee or candidate here. You could have one, of course. 
    """
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="The even-numbered year that ends a two-year cycle.")
    fec_id = models.CharField(max_length=9, null=True, blank=True, help_text="The FEC id of the committee filing this report")
    committee_name = models.CharField(max_length=200, null=True, blank=True, help_text="The committee's name as reported to the FEC")
    #### FILING NUMBER IS NOT NUMERIC BECAUSE PAPER FILING NUMBERS BEGIN WITH A P
    # filing_number = models.IntegerField(primary_key=True, help_text="The numeric filing number assigned to this electronic filing by the FEC")
    filing_number = models.CharField(max_length=15, primary_key=True, help_text="The numeric filing number assigned to this electronic filing by the FEC")
    
    form_type = models.CharField(max_length=7, null=True, blank=True, help_text="The type of form used.")
    filed_date = models.DateField(null=True, blank=True, help_text="The date that this filing was processed")
    coverage_from_date = models.DateField(null=True, blank=True, help_text="The start of the reporting period that this filing covers. Not all forms list this.")
    coverage_to_date = models.DateField(null=True, blank=True, help_text="The end of the reporting period that this filing covers. Not all forms include this")
    process_time = models.DateTimeField(null=True, blank=True, help_text="This is the time that FEC processed the filing")
    # is_superpac = models.NullBooleanField(help_text="Is this group a super PAC?")
    
    # populate from committee_master file. Helpful to have this here; a foreign key to committee might be missing.
    committee_designation = models.CharField(max_length=1, null=True, blank=True, help_text="See the FEC's committee designations")
    committee_type = models.CharField(max_length=1, null=True, blank=True, help_text="See the FEC's committee types")
    committee_slug = models.SlugField(max_length=255, null=True, blank=True)
    party = models.CharField(max_length=3, blank=True, null=True)
    
    
    
    ### processing status flags
    filing_is_downloaded = models.NullBooleanField(default=False)
    header_is_processed = models.NullBooleanField(default=False)
    previous_amendments_processed = models.NullBooleanField(default=False)
    new_filing_details_set = models.NullBooleanField(default=False)
    data_is_processed = models.NullBooleanField(default=False)
    body_rows_superseded = models.NullBooleanField(default=False)
    ie_rows_processed = models.NullBooleanField(default=False)
    
    filing_error = models.NullBooleanField(default=False)
    filing_error_message = models.TextField(null=True, blank=True, "What is the blocking error message")
    
    ### summary data only available after form is parsed:
    
    # populated for periodic reports only
    coh_start = models.DecimalField(max_digits=14, decimal_places=2, null=True, help_text="The cash on hand at the start of the reporting period. Not recorded on all forms.")
    coh_end = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0, help_text="The cash on hand at the end of the reporting period. ")
    # Did they borrow *new* money this period ? 
    new_loans = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0, help_text="The amount of new loans taken on by the committee during this reporting period.")
    
    # if applicable:
    tot_raised = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0, help_text="The total amount raised in this report. This is total receipts for periodic reports.")
    tot_spent = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0, help_text="The total amount spent in this report.")
    
    tot_ies = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures ")
    tot_coordinated = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0)
    
    # which filing types are contained? Store as a dict. 
    # lines_present =  DictionaryField(db_index=True, null=True, help_text="A dictionary of the type of lines present in this report by schedule. ")
    
    
    ## Models migrated from old form_header model

    # header_data = DictionaryField(db_index=False, null=True)
    
    # does this supersede another an filing?
    is_amendment=models.BooleanField()
    # if so, what's the original?
    amends_filing=models.IntegerField(null=True, blank=True)
    amendment_number = models.IntegerField(null=True, blank=True)
    
    # Is this filing superseded by another filing, either a later amendment, or a periodic filing.
    superseded_by_amendment=models.BooleanField(default=False, help_text="Is this filing superseded by another filing, either a later amendment, or a periodic filing")
    # which filing is this one superseded by? 
    amended_by=models.IntegerField(null=True, blank=True)
    
    # Is this a 24- or 48- hour notice that is now covered by a periodic (monthly/quarterly) filing, and if so, is ignorable ? 
    covered_by_periodic_filing=models.BooleanField(default=False)
    covered_by=models.IntegerField(null=True, blank=True)
    
    
    # F5's can be monthly/quarterly or immediate. We need to keep track of which kind is which so we can supersede them. The filers sometimes fuck their filings up pretty substantially though, so this might not be advisable. 
    is_f5_quarterly=models.BooleanField(default=False)
    
    class Meta:
        unique = ('filing_number')


# field sizes are based on v8.0 specs, generally
class SkedA(models.Model):
    """
    There's no foreign key to committee or filing.
    Nor there is there a unique_together for filing_number and transaction_id (though these are unique)
    """
    # additional fields 
    line_number = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    superseded_by_amendment = models.BooleanField(default=False)

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    # Should be wrapped to newer version? 
    contributor_name = models.CharField(max_length=200, blank=True, null=True, help_text="deprecated as a field since v5.3")
    contributor_organization_name = models.CharField(max_length=200, blank=True, null=True)
    contributor_last_name  = models.CharField(max_length=30, blank=True, null=True)
    contributor_first_name = models.CharField(max_length=20, blank=True, null=True)
    contributor_middle_name = models.CharField(max_length=20, blank=True, null=True)
    contributor_prefix= models.CharField(max_length=10, blank=True, null=True)
    contributor_suffix = models.CharField(max_length=10, blank=True, null=True)
    contributor_street_1 = models.CharField(max_length=34, blank=True, null=True)
    contributor_street_2 = models.CharField(max_length=34, blank=True, null=True)
    contributor_city = models.CharField(max_length=30, blank=True, null=True)
    contributor_state = models.CharField(max_length=2, blank=True, null=True)
    contributor_zip = models.CharField(max_length=9, blank=True, null=True)
    election_code = models.CharField(max_length=5, blank=True, null=True)
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="required if election code starts with 'O' for other")
    contribution_date = models.CharField(max_length=8, blank=True, null=True, help_text="exactly as it appears")
    contribution_date_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    contribution_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    contribution_aggregate = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    contribution_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="deprecated")
    contribution_purpose_descrip = models.CharField(max_length=100, blank=True, null=True)
#    increased_limit_code = models.CharField(max_length=10, blank=True, null=True, help_text="deprecated after 6.4 or so")
    contributor_employer = models.CharField(max_length=38, blank=True, null=True)
    contributor_occupation = models.CharField(max_length=38, blank=True, null=True)
    donor_committee_fec_id = models.CharField(max_length=9, blank=True, null=True)
    donor_committee_name = models.CharField(max_length=200, blank=True, null=True)
    donor_candidate_fec_id = models.CharField(max_length=9, blank=True, null=True)
    # should be updated to new, if possible... 
    donor_candidate_name = models.CharField(max_length=200, blank=True, null=True, help_text="deprecated")
    donor_candidate_last_name = models.CharField(max_length=30, blank=True, null=True)
    donor_candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    donor_candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    donor_candidate_prefix  = models.CharField(max_length=10, blank=True, null=True)
    donor_candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    donor_candidate_office = models.CharField(max_length=1, blank=True, null=True)
    donor_candidate_state = models.CharField(max_length=2, blank=True, null=True)
    donor_candidate_district = models.CharField(max_length=2, blank=True, null=True)
    conduit_name = models.CharField(max_length=200, blank=True, null=True)
    conduit_street1 = models.CharField(max_length=34, blank=True, null=True)
    conduit_street2 = models.CharField(max_length=34, blank=True, null=True)
    conduit_city = models.CharField(max_length=30, blank=True, null=True)
    conduit_state = models.CharField(max_length=2, blank=True, null=True)
    conduit_zip = models.CharField(max_length=9, blank=True, null=True)
    memo_code = models.CharField(max_length=1, blank=True, null=True)
    memo_text_description = models.CharField(max_length=100, blank=True, null=True)
    reference_code = models.CharField(max_length=9, blank=True, null=True)

class SkedB(models.Model):
    # additional fields 
    line_number = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    superseded_by_amendment = models.BooleanField(default=False)

    # from the field
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    payee_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    payee_organization_name = models.CharField(max_length=200, blank=True, null=True)
    payee_last_name = models.CharField(max_length=30, blank=True, null=True)
    payee_first_name = models.CharField(max_length=20, blank=True, null=True)
    payee_middle_name  = models.CharField(max_length=20, blank=True, null=True)
    payee_prefix = models.CharField(max_length=10, blank=True, null=True)
    payee_suffix = models.CharField(max_length=10, blank=True, null=True)
    payee_street_1 = models.CharField(max_length=34, blank=True, null=True)
    payee_street_2 = models.CharField(max_length=34, blank=True, null=True)
    payee_city = models.CharField(max_length=30, blank=True, null=True)
    payee_state = models.CharField(max_length=2, blank=True, null=True)
    payee_zip = models.CharField(max_length=9, blank=True, null=True)
    election_code = models.CharField(max_length=5, blank=True, null=True)
    election_other_description = models.CharField(max_length=20, blank=True, null=True,  help_text="required if election code starts with 'O' for other")
    expenditure_date = models.CharField(max_length=8, blank=True, null=True, help_text="exactly as it appears")
    expenditure_date_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    expenditure_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    semi_annual_refunded_bundled_amt = models.DecimalField(max_digits=14, decimal_places=2, null=True, help_text="Used for F3L only")
    expenditure_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="deprecated")
    expenditure_purpose_descrip = models.CharField(max_length=100, blank=True, null=True)
    category_code = models.CharField(max_length=3, blank=True, null=True)
    beneficiary_committee_fec_id = models.CharField(max_length=9, blank=True, null=True)
    beneficiary_committee_name = models.CharField(max_length=200, blank=True, null=True)
    beneficiary_candidate_fec_id = models.CharField(max_length=9, blank=True, null=True)
    beneficiary_candidate_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    beneficiary_candidate_last_name = models.CharField(max_length=30, blank=True, null=True)
    beneficiary_candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_candidate_prefix = models.CharField(max_length=10, blank=True, null=True)
    beneficiary_candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    beneficiary_candidate_office = models.CharField(max_length=1, blank=True, null=True)
    beneficiary_candidate_state = models.CharField(max_length=2, blank=True, null=True)
    beneficiary_candidate_district = models.CharField(max_length=2, blank=True, null=True)
    conduit_name = models.CharField(max_length=200, blank=True, null=True)
    conduit_street_1 = models.CharField(max_length=34, blank=True, null=True)
    conduit_street_2 = models.CharField(max_length=34, blank=True, null=True)
    conduit_city  = models.CharField(max_length=30, blank=True, null=True)
    conduit_state = models.CharField(max_length=2, blank=True, null=True)
    conduit_zip = models.CharField(max_length=9, blank=True, null=True)
    memo_code = models.CharField(max_length=1, blank=True, null=True)
    memo_text_description = models.CharField(max_length=100, blank=True, null=True)

    #reference_to_si_or_sl_system_code_that_identifies_the_account
    ref_to_sys_code_ids_acct = models.CharField(max_length=9, blank=True, null=True)
    refund_or_disposal_of_excess = models.CharField(max_length=20, blank=True, null=True, help_text="deprecated")
    communication_date = models.CharField(max_length=9, blank=True, null=True, help_text="deprecated")

class SkedE(models.Model):
    # additional fields 
    line_number = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    # can be superseded by amendment or by later filing
    superseded_by_amendment = models.BooleanField(default=False)

    ## Data added fields. Party isn't part of the original data, so...
    candidate_targeted = models.ForeignKey('Candidate', null=True, "The candidate targeted by this independent expenditure.")
    
    effective_date = models.DateField(null=True, help_text="What date should we use? Through version 8.0 of FECfile, there was only an 'expenditure date', but beginning with v8.1 there were two dates--a dissemination date and an expenditure date. For v8.1 use the dissemination date; for earlier version use the expenditure date.")


    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True, help_text="The transaction id from the original filing. These ids are unique per report, not necessarily per cycle.")
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')

    payee_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    payee_organization_name = models.CharField(max_length=200, blank=True, null=True, help_text="The name of the organization being paid")
    payee_last_name = models.CharField(max_length=30, blank=True, null=True)
    payee_first_name = models.CharField(max_length=20, blank=True, null=True)
    payee_middle_name = models.CharField(max_length=20, blank=True, null=True)
    payee_prefix = models.CharField(max_length=10, blank=True, null=True)
    payee_suffix = models.CharField(max_length=10, blank=True, null=True)
    payee_street_1 = models.CharField(max_length=34, blank=True, null=True, help_text="The street address of the payee")
    payee_street_2 = models.CharField(max_length=34, blank=True, null=True, help_text="The street address of the payee -- second part, if needed.")
    payee_city = models.CharField(max_length=30, blank=True, null=True, help_text="The payee's city")
    payee_state = models.CharField(max_length=2, blank=True, null=True, help_text="Payee state")
    payee_zip = models.CharField(max_length=9, blank=True, null=True, help_text="Payee ZIP code")
    election_code = models.CharField(max_length=5, blank=True, null=True, help_text="The code describing the election")
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="Any additional description of the election")
    expenditure_date = models.CharField(max_length=8, blank=True, null=True)
    expenditure_date_formatted = models.DateField(null=True, help_text="The date of the expenditure")
    dissemination_date = models.CharField(max_length=8, blank=True, null=True, help_text="The dissemination date, only in v8.1 and higher.")
    dissemination_date_formatted = models.DateField(null=True, help_text="The dissemination date, only in v8.1 and higher.")


    expenditure_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, help_text="The expenditure amount")
    calendar_y_t_d_per_election_office = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    expenditure_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="The filer-entered code of the expenditure. This isn't required.")
    expenditure_purpose_descrip = models.CharField(max_length=100, blank=True, null=True, help_text="The filer-described purpose of the expenditure")
    category_code = models.CharField(max_length=3, blank=True, null=True)
    payee_cmtte_fec_id_number = models.CharField(max_length=9, blank=True, null=True)
    support_oppose_code = models.CharField(max_length=1, blank=True, null=True)
    candidate_id_number = models.CharField(max_length=9, blank=True, null=True)
    candidate_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    candidate_last_name  = models.CharField(max_length=30, blank=True, null=True)
    candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    candidate_prefix = models.CharField(max_length=10, blank=True, null=True)
    candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    candidate_office = models.CharField(max_length=1, blank=True, null=True)
    candidate_state = models.CharField(max_length=2, blank=True, null=True)
    candidate_district = models.CharField(max_length=2, blank=True, null=True)
    completing_last_name = models.CharField(max_length=30, blank=True, null=True)
    completing_first_name = models.CharField(max_length=20, blank=True, null=True)
    completing_middle_name = models.CharField(max_length=20, blank=True, null=True)
    completing_prefix = models.CharField(max_length=10, blank=True, null=True)
    completing_suffix = models.CharField(max_length=10, blank=True, null=True)
    date_signed = models.CharField(max_length=8, blank=True, null=True)
    date_signed_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    memo_code = models.CharField(max_length=1, blank=True, null=True, help_text="This is an X for lines that are subitemizations")
    memo_text_description = models.CharField(max_length=100, blank=True, null=True, help_text="A text description of unique circumstances surrounding this expenditure.")



class OtherLine(models.Model):
    # additional fields 
    line_number = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    superseded_by_amendment = models.BooleanField(default=False)

    # Standardized name of the parser we use to process it.
    form_parser = models.CharField(max_length=6, blank=True)

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)

    # Store all other line data as a dict:
    line_data =  models.TextField(null=True) # maybe pickle the dictionary and store it here? 
