from datetime import date

from django.core.management.base import BaseCommand, CommandError

from efilings.utils.summary_utils import update_committee_totals
from efilings.models import Committee
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'
    
class Command(BaseCommand):
    help = "Redo the summaries of all committees, whether or not they are marked as dirty"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_committees = Committee.objects.filter(cycle=CURRENT_CYCLE)
        for committee in all_committees:
            update_committee_totals(committee, CURRENT_CYCLE)
            committee.is_dirty=False
            committee.save()


