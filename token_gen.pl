#  token_gen.pl v 3.2.2 (c)2018 Francisc TOTH YO6OWN
#  status: ft1
#  This is a module of the online radioamateur examination program
#  "sim eXAM", created for YO6KXP ham-club located in Sacele, ROMANIA
#  All rights reserved by YO6OWN Francisc TOTH
#  Made in Romania

# this script is run locally, not in cgi-bin/
# by running this perl script, a token is generated. This token is inserted in 
# sanity check html form. This form sends the token to tugetxr2.cgi or 
# to tool_admintt.cgi in order to authenticate
# by this token, a secret is not propagated over the network, just used to create and verify a hash

# ch 3.2.2 - new transaction generated with epoch time, reducing complexity of the code
# ch 3.2.1 - md5 changed to sha1 in compute_mac()
# ch 3.2.0 - implement a token generation for authentication of the administrator
 
use strict;
use warnings;

#print qq!generate new transaction<br>\n!;
my $epochTime = time();
#CHANGE THIS for customizing
my $epochExpire = $epochTime + 1800; #30 minutes lifetime = 1800 sec
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];

#generate transaction id and its MAC

#assemble the trid+timestamp
my $hexi= "admin_$exp_sec\_$exp_min\_$exp_hour\_$exp_day\_$exp_month\_$exp_year\_"; #adds the expiry timestamp
#compute mac for timestamp 
my $heximac = compute_mac($hexi); #compute sha1 MessageAuthentication Code
$hexi= "$hexi$heximac"; #the full transaction id

print "Admin token, 30 min:\n$hexi\n";


#-------------------------------------
sub compute_mac {

use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
  hmac_sha1_hex($secret,$message);
} #end of compute_mac
#--------------------------------------

