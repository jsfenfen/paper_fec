from datetime import date

from django.core.management.base import BaseCommand, CommandError

from efilings.utils.summary_utils import update_candidate_totals
from efilings.models import Candidate
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'
    
class Command(BaseCommand):
    help = "Redo the summaries of all candidates, whether or not they are marked as dirty"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_candidates = Candidate.objects.filter(cycle=CURRENT_CYCLE)
        for candidate in all_candidates:
            update_candidate_totals(candidate, CURRENT_CYCLE)


