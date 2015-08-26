# assumes this is run one dir up, using: 'python -m helpers.flush_all_rows'

from parsing.utils.db_utils import get_connection

# swiped from: https://gist.github.com/garrettdreyfus/8153571 
def yes_or_no(question):
    reply = str(raw_input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")

if yes_or_no("This will permanently remove all line items from the db. Do you really want to proceed"):
    print "Blowing it all up!"
    
    connection = get_connection()
    connection.set_isolation_level(0)
    cursor = connection.cursor()
    
    for table in ['efilings_skeda', 'efilings_skedb', 'efilings_skede', 'efilings_otherline']:
        cmd = "delete from %s" % (table)
        print "Running cmd: %s" % cmd
        cursor.execute(cmd)
        print "Executed command; %s affected rows\n\n" % (cursor.rowcount)
        
        
else:
    print "Ok, aborting."