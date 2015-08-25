from django.db import models
from django.utils import timezone


class Update_Time(models.Model):
  key = models.SlugField()
  update_time = models.DateTimeField()

  def save(self, *args, **kwargs):
      ''' On save, update timestamps '''
      self.update_time = timezone.now()
      super(Update_Time, self).save(*args, **kwargs)


class Candidate(models.Model):
    ## This is the human verified field -- see legislators.models.incumbent_challenger
    slug = models.SlugField(null=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    
    
    ### SEMI-CURATED FIELDS, THAT COULD BE SET BY SCRIPT. YOU PROBABLY WANT TO LOSE THESE
    is_incumbent = models.BooleanField(default=False,help_text="Are they an incumbent? If not, they are a challenger")
    curated_election_year =  models.IntegerField(null=True, help_text="What year is their next election. Set this field--don't overwrite the fec's election year. ")
    display = models.BooleanField(default=False,help_text="Should they be displayed. Use this = False for off cycle candidates.")
    display_name = models.CharField(max_length=255, null=True, help_text="FEC often has wrong name")
    not_seeking_reelection = models.BooleanField(default=False,help_text="True if they are an incumbent who is not seeking reelection.")
    other_office_sought = models.CharField(max_length=127, blank=True, null=True, help_text="E.g. are they running for senate?")
    other_fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="If they've declared for another federal position, what is it? This should be the *candidate id* not a committee id. ")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Set this from US Congress repo or soemthing. Only applies to senators.")
    
    
    #### FEC DATA
    name = models.CharField(max_length=255, blank=True, null=True, help_text="name")
    pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party?")
    party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party")
    fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
    pcc = models.CharField(max_length=9, blank=True, null=True, help_text="FEC id for the candidate's primary campaign committee")
    election_year = models.PositiveIntegerField(blank=True, null=True, help_text="Year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    fec_data_update_time = models.DateTimeField(null=True, blank=True, help_text="When was this last set?")
    #### END FEC DATA 
    
    
    ##### ID FIELDS -- ADD MORE! 
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    transparencydata_id = models.CharField(max_length=40, default='', null=True)
    
    ###### IE TOTALS FOR OR AGAINST THIS CANDIDATE
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    ie_update_time = models.DateTimeField(null=True, blank=True, help_text="When were ie totals last updated?")
    #### END IE TOTALS
    
    
    ###### CANDIDATE TOTALS
    # from the sum of all authorized committees -- one might also do something that includes leadership pacs.
     # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0)
    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    as_of_date = models.DateField(null=True, help_text="When are the totals as of? This is slightly dicey because it's theoretically possible that there could be different filing deadlines, but in practice this almost never happens.")
    candidate_total_update_time = models.DateTimeField(null=True, blank=True, help_text="When were candidate totals last updated?")
    ##### END CANDIDATE TOTALS
    
    # Setting this whenever a filing lands allows one to select which candidates need totals updated, rather than running all of them... 
    is_dirty = models.NullBooleanField(null=True, default=True, help_text="Do summary numbers need to be recomputed?")    
    
    

    class Meta:
        unique_together = ('fec_id', 'cycle')


class Committee(models.Model):
    cycle = models.CharField(max_length=4)
    slug = models.SlugField(max_length=255) 
    
    
    ###### MAYBE CURATED FIELDS / SOME SET BY SCRIPT / SOME USELESS TO YOU
    is_paper_filer = models.NullBooleanField(null=True, default=False, help_text="True for most senate committees, also NRSC/DSCC, some others.")    
    curated_candidate = models.ForeignKey('Candidate', related_name='related_candidate', null=True, help_text="For house and senate: Only include if it's a P-primary campaign committee or A-authorized campaign committee with the current cycle as appears in the candidate-committee-linkage file. Check this by hand for presidential candidates though, because many committees claim to be authorized by aren't")
    leadership_pac_candidate = models.ForeignKey('Candidate', related_name='leadership_candidate', null=True, help_text="If this is a leadership pac with a candidate affilate, put the candidate here.")
    leadership_pac_leader = models.CharField(max_length=200, blank=True, null=True, help_text="Leadership pacs are often affiliated with someone who's not a candidate (yet), and maybe never will be. Put their name as text here.")
    
    # This needs to be curated to be worthwhile--FEC records don't specify this, but it's interesting. 
    # Would only apply to ctype=I -- non-committee filers.
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

    # what's their orientation? Sunlight maintained this on outside spenders only, which was helpful for looking at overall picture of outside spending, esp if the non-profit status is maintained. 
    political_orientation = models.CharField(max_length=1,null=True, help_text="The political orientation of the group, as coded by administrators. ", choices=[
                        ('R', 'backs Republicans'),
                        ('D', 'backs Democrats'),
                        ('U', 'unknown'),
                          ])
    political_orientation_verified = models.BooleanField(default=False, help_text="Check this box if the political orientation has been verified by a human")
    
    
    is_dirty = models.NullBooleanField(null=True, default=True, help_text="Do summary numbers need to be recomputed?")    


    # direct from the raw fec table
    name = models.CharField(max_length=255, help_text="The committee name.")
    fec_id = models.CharField(max_length=9, blank=True, help_text="The FEC id of the filing committee")
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
      
    fec_data_update_time = models.DateTimeField(null=True, help_text="When was data sourced from FEC about candidate last updated")

    ####### COMMITTEE SUMS
    # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total receipts for this committee ceived during the entire cycle. ")
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total disbursements by this committee ceived during the entire cycle")
    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0, help_text="Total outstanding loans as of the cash_on_hand_date")
    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Cash on hand as of the end of committee's most recent periodic report; this date appears as cash_on_hand_date")
    cash_on_hand_date = models.DateField(null=True, help_text="The end of the most recent periodic filing; the date that the cash on hand was reported as of.")
    committee_sum_update_time = models.DateTimeField(null=True, help_text="When were totals from FEC about candidate last updated")
    committee_sum_update_time = models.DateTimeField(null=True, help_text="When was data sourced from FEC about candidate last updated")
    ###### END COMMITTEE SUMS

    ##### IE SUMS 
    has_independent_expenditures = models.NullBooleanField(null=True, default=False)
    total_independent_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="Total independent expenditures made this cycle.")
    ie_support_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Democratic candidates")
    ie_oppose_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Democratic candidates")
    ie_support_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Republican candidates")
    ie_oppose_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Republican candidates")
    tot_pres_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    ie_sum_update_time = models.DateTimeField(null=True, help_text="When was data sourced from FEC about candidate last updated")
    ###### END IE SUMS

    
    
    class Meta:
        unique_together = (("cycle", "fec_id"),)


class Filing(models.Model):
    """
    There's no foreign key to a committee or candidate here. You could have one, of course. 
    I'm assuming that somewhere you have the candidate-committee linkage file downloaded regularly
    and can reference that as needed. 
    """
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="The even-numbered year that ends a two-year cycle.")
    fec_id = models.CharField(max_length=9, null=True, blank=True, help_text="The FEC id of the committee filing this report")
    #### FILING NUMBER IS NOT NUMERIC BECAUSE PAPER FILING NUMBERS BEGIN WITH A P
    # filing_number = models.IntegerField(primary_key=True, help_text="The numeric filing number assigned to this electronic filing by the FEC")
    filing_id = models.CharField(max_length=15, primary_key=True, unique=True, help_text="The alphanumeric filing number assigned to this electronic filing by the FEC")
    filing_number = models.IntegerField(help_text="The integer part of the filing number assigned to this electronic filing by the FEC", null=True)
    filing_type = models.CharField(max_length=1, help_text="Filing type: E = electronic, P = paper, S = experimental senate filing", null=True)
    discovery_method = models.CharField(help_text=b'How did we detect the filing? : R=RSS, F=find_filings, Q=query, A=Archived daily filings -- add your own here...', max_length=1, null=True, blank=True)
    
    form_type = models.CharField(max_length=7, null=True, blank=True, help_text="The type of form used.")
    filed_date = models.DateField(null=True, blank=True, help_text="The date that this filing was processed")
    coverage_from_date = models.DateField(null=True, blank=True, help_text="The start of the reporting period that this filing covers. Not all forms list this.")
    coverage_to_date = models.DateField(null=True, blank=True, help_text="The end of the reporting period that this filing covers. Not all forms include this")
    process_time = models.DateTimeField(null=True, blank=True, help_text="This is the time that we first located the filing")
    
    # Denormalized committee data--because the filings table is hit *a lot*.
    
    committee_name = models.CharField(max_length=200, null=True, blank=True, help_text="The committee's name as reported to the FEC")
    committee_designation = models.CharField(max_length=1, null=True, blank=True, help_text="See the FEC's committee designations")
    committee_type = models.CharField(max_length=1, null=True, blank=True, help_text="See the FEC's committee types")
    committee_slug = models.SlugField(max_length=255, null=True, blank=True)
    party = models.CharField(max_length=3, blank=True, null=True)
    
    
    ###############STATUS TRACKING FIELDS
    ### May want to finesse these; 0 = not done, 1 = done, E = error; add codes as needed.
    ### May also want to time stamp these to track efficiency. 
    ### Also consider moving this to mongo or elsewhere if to0 many writes are required.
    filing_is_downloaded = models.CharField(max_length=1, default="0")
    header_is_processed = models.CharField(max_length=1, default="0")
    previous_amendments_processed = models.CharField(max_length=1, default="0")
    new_filing_details_set = models.CharField(max_length=1, default="0")
    data_is_processed = models.CharField(max_length=1, default="0")
    body_rows_superseded = models.CharField(max_length=1, default="0")
    ie_rows_processed = models.CharField(max_length=1, default="0")
    filing_error = models.NullBooleanField(default=False)
    filing_error_message = models.TextField(null=True, blank=True, help_text="What is the blocking error message")
    #################END STATUS TRACKING FIELDS.
    
    ############ summary data only available after form is parsed:
    
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
    
    # Useful to track this stuff generally... 
    skeda_linecount = models.IntegerField(null=True, blank=True)
    skedb_linecount = models.IntegerField(null=True, blank=True)
    skedc_linecount = models.IntegerField(null=True, blank=True) # not really supported yet
    skedd_linecount = models.IntegerField(null=True, blank=True) # ditto
    skede_linecount = models.IntegerField(null=True, blank=True)
    skedo_linecount = models.IntegerField(null=True, blank=True) # a count of 'other' lines. 
    
    ####### AMENDMENTS ETC
    # does this supersede another an filing?
    is_amendment=models.NullBooleanField()
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
    
    ##### HACK B/C OF NO HSTORES
    ##### BECAUSE WE DON'T HAVE A DICTIONARY / JSON OBJECT AVAILABLE, JUST SAVE THE HEADER DICT AS TEXT
    ##### THERE'S A BETTER APPROACH (FOREIGN KEY TO MONGO? BINARIZATION ? PROTOCOL BUFFERS ? 
    ##### IS THERE A PICKLE OPERATION THAT DOESN'T FREAK OUT ABOUT QUOTE CHARS? OR MORE RESEARCH ON 
    ##### WHETHER HAVING A QUOTE CHAR SOMEHOW WORKS (MY RECOLLECTION IS THAT IT DOESN'T))
    #### IT'S POSSIBLE ONE DOESN'T REALLY WANT THIS DATA, BUT IT'S PRETTY DARN USEFUL.
    form_line_data =  models.TextField(null=True) 
    
    

# field sizes are based on v8.0 specs, generally
class SkedA(models.Model):
    """
    There's no foreign key to committee or filing.
    Nor there is there a unique_together for filing_number and transaction_id (though these are unique)
    """
    # additional fields 
    line_sequence = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
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
    line_sequence = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
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
    line_sequence = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    # can be superseded by amendment or by later filing
    superseded_by_amendment = models.BooleanField(default=False)

    ## Data added fields. Party isn't part of the original data, so...
    candidate_targeted = models.ForeignKey('Candidate', null=True, help_text="The candidate targeted by this independent expenditure.")
    
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
    line_sequence = models.IntegerField() # The line number that this filing appears in--it's useful to maintain the original order for memo fields like 'see below'
    filing_number = models.CharField(max_length=15)
    superseded_by_amendment = models.BooleanField(default=False)

    # Standardized name of the parser we use to process it.
    form_parser = models.CharField(max_length=6, blank=True)

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)

    # Store all other line data as a python stringified dict. pickling wasn't working out. 
    line_data =  models.TextField(null=True) #
