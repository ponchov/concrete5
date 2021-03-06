#!/usr/bin/python
"""Set Concrete5 admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively

"""

import re
import sys
import getopt
import hashlib

from dialog_wrapper import Dialog
from mysqlconf import MySQL

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Concrete5 Password",
            "Enter new password for the Concrete5 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Concrete5 Email",
            "Enter email address for the Concrete5 'admin' account.",
            "admin@example.com")

    salt = ''
    config = '/var/www/concrete5/config/site.php'
    for s in file(config).readlines():
        s = s.strip()
        m = re.match("define\('PASSWORD_SALT', '(.*)'\);", s)
        if m:
            salt = m.group(1)
            break

    if not salt:
        usage("Could not identify salt from: %s" % config)

    hashpass = hashlib.md5(':'.join([password, salt])).hexdigest()

    m = MySQL()
    m.execute('UPDATE concrete5.Users SET uPassword=\"%s\" WHERE uName=\"admin\";' % hashpass)
    m.execute('UPDATE concrete5.Users SET uEmail=\"%s\" WHERE uName=\"admin\";' % email)

if __name__ == "__main__":
    main()

