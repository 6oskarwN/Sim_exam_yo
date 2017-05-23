#!c:\Perl\bin\perl

#  tugetxr2.cgi v.3.2.0 (c)2007 Francisc TOTH
#  status: under development
#  This is a module of the online radioamateur examination program
#  "sim eXAM", created for YO6KXP ham-club located in Sacele, ROMANIA
#  All rights reserved by YO6OWN Francisc TOTH
#  Made in Romania

# ch 3.2.0 - implement a token exchange for authentication of the command
# ch 0.0.6 - trouble ticket 25 implemented: minimal transaction info decoded: pagecode
# ch 0.0.5 - removed the HAM-eXAM related file browsing(HAM-eXAM was decommisioned)
 
use strict;
use warnings;


#-for response retrieving
my %answer=();
my $post_token;   #token from input data

my $fline;
my $i;
my @splitline;
my @pairs;


###########################################
### Process inputs, generate hash table ###
###########################################
{
#my $buffer=(); #needed only for http POST
my $pair;
my $name;
my $value;

#read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST-technology
#$debug_buffer=$ENV{'QUERY_STRING'};
#@pairs=split(/&/, $buffer); #POST-technology
@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology
foreach $pair(@pairs) 
		{

($name,$value) = split(/=/,$pair);
if(defined($name) and defined($value)){
%answer = (%answer,$name,$value); }	#add defined pairs answers in hash
			  
		} #.end foreach

} #.end process inputs

$post_token= $answer{'token'}; #extract token from input data
#md MAC has + = %2B and / = %2F characters, must be reconverted
if(defined($post_token)) {
			$post_token =~ s/%2B/\+/g;
			$post_token =~ s/%2F/\//g;
                         }
else {dienice ("ERR01",2,\"undef token"); } # no token or with void value

#print qq!token received: $post_token<br>\n!; #debug
#transaction pattern: 
# admin_33_19_0_12_2_116_Trl5zxcXkaO5YcsWr4UYfg

#now we should check received transaction
#case 0: check md5 if correct
#        if not, must be recorded in cheat_file
#case 1: check if timestamp expired; if expired, no log in cheat
#case 2: check if it's an admin transaction
#        if not, record in cheat_file

my $string_token; # we compose the incoming transaction to recalculate mac
my $heximac;


@pairs=split(/_/,$post_token); #reusing @pairs variable for spliting results
# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ERR01",2,\$post_token); } # unstructured token
$string_token="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_token);

unless($heximac eq $pairs[7]) { dienice("ERR01",3,\$post_token);} #case of tampering

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) { 
                                             dienice("ERR02",0,\"null"); }

#check case 2
 elsif ($pairs[0] ne 'admin') {dienice("ERR03",3,\$post_token);}

#ACTION: open sim_transaction ID file
open(transactionFILE,"< sim_transaction") or die("can't open simtrans file: $!\n");					#open transaction file for writing
#flock(transactionFILE,1);		#just a read-lock

print "Content-type: text/html\n\n";
print "<html>\n";
print qq!<head><title>noname Sanity Check R2.0</title></head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;


print qq!<b><big>sim_transactions:</big></b><br>\n!;
while($fline=<transactionFILE>) 
{

chomp $fline;

@splitline=split(/ /, $fline);
if (defined $splitline[2]){
if($splitline[2] eq 2) { print qq!<small><font color="white">root-page:</font></small><br>\n!; }
elsif ($splitline[2] eq 4){ print qq!<small><font color="white">ex. I:</font></small><br>\n!; }
elsif ($splitline[2] eq 5){ print qq!<small><font color="white">ex. II:</font></small><br>\n!; }
elsif ($splitline[2] eq 6){ print qq!<small><font color="white">ex. III:</font></small><br>\n!; }
elsif ($splitline[2] eq 7){ print qq!<small><font color="white">ex. III-R:</font></small><br>\n!; }

if ($splitline[0] =~ m/\*/) {print qq!<strike>!;}

if(timestamp_expired($splitline[3],$splitline[4],$splitline[5],$splitline[6],$splitline[7],$splitline[8])>0)
  { print qq!<font color="lightgray">!;}
 else { print qq!<font color="#7fffd4">!; }
                         }                         
print qq!<small>$fline</small>!;
if (defined $splitline[2]){print qq!</font>!; }
if ($splitline[0] =~ m/\*/) {print qq!</strike>!;}

print qq!<br>\n!;

} #.end while
close (transactionFILE) or die("cant close transaction file\n");
print qq!file closed.<br>\n!;
print qq!----------------------------------------------<br><br>\n!;


#ACTION: open user file
open(xfile_handler,"< sim_users") or die("can't open transaction file: $!\n");					#open transaction file for writing
#flock(xfile_handler,1);		#just a read-lock
$i=1;
print qq!<small><br>\n!;
while($fline=<xfile_handler>) 
{
#@splitline=split(/ /,$fline);
if($i==1 or $i==6 or $i==7) #camp inreg, primul=1
{chomp $fline;
print qq!$fline - !;
}
if($i==7) {
			print qq!<br>\n!;
            $i=0;
			}
$i++;

}
print qq!</small><br>\n!;
close (xfile_handler) or die("cant close transaction file\n");
print qq!file closed.<br>\n!;
print qq!----------------------------------------------<br><br>\n!;


print qq!<b><big>CHEATER-LOG(entering obsolete):</big></b><br>\n!;
#ACTION: open transaction ID file
open(xfile_handler,"< cheat_log") or die("can't open transaction file: $!\n");					#open transaction file for writing
#flock(xfile_handler,1);		#just a read-lock
while($fline=<xfile_handler>) 
{
chomp $fline;
print qq!$fline<br>\n!;
}
close (xfile_handler) or die("cant close transaction file\n");
print qq!file closed.<br>\n!;
print qq!----------------------------------------------<br><br>\n!;

print qq!</body>\n</html>!;

#-------------------------------------
sub compute_mac {

use Digest::MD5;
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
    Digest::MD5::md5_base64($secret, Digest::MD5::md5($secret, $message));
} #end of compute_mac

#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year UTC
#out: seconds since expired MAX 99999, 0 = not expired.

sub timestamp_expired
{
use Time::Local;

my($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year)=@_;

my $timediff;
my $actualTime = time();
my $dateTime= timegm($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year);
$timediff=$actualTime-$dateTime;

return($timediff);  #here is the general return

} #.end sub timestamp

#--------------------------------------
#---development---- treat the "or die" case
#how to use it
#$error_code is a string, you see it, this is the text selector
#$counter: if it is 0, error is not logged. If 1..5 = threat factor
#reference is the reference to string that is passed to be logged.

sub dienice
{
my ($error_code,$counter,$err_reference)=@_; #in vers. urmatoare counter e modificat in referinta la array/string

#my $timestring=localtime(time);
my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "authentication fail, logged.",
              "ERR02" => "authentication token expired",
              "ERR03" => "authentication fail, logged.",
              "ERR04" => "reserved $$err_reference",
              "ERR05" => "reserved",
              "ERR06" => "reserved",
              "ERR07" => "reserved",
              "ERR08" => "reserved",
              "ERR09" => "reserved",
              "ERR10" => "reserved",
              "ERR11" => "reserved",
              "ERR12" => "reserved",
              "ERR13" => "reserved",
              "ERR14" => "reserved",
              "ERR15" => "reserved",
              "ERR16" => "reserved",
              "ERR17" => "reserved",
              "ERR18" => "reserved",
              "ERR19" => "reserved",
              "ERR20" => "reserved"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "token has been tampered with, md5 mismatch",    #test ok
              "ERR02" => "timestamp expired",           #test ok
              "ERR03" => "good transaction but token not admin",             #test ok
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "reserved",
              "ERR07" => "reserved",
              "ERR08" => "reserved",
              "ERR09" => "reserved",
              "ERR10" => "reserved",
              "ERR11" => "reserved",
              "ERR12" => "reserved",
              "ERR13" => "reserved",
              "ERR14" => "reserved",
              "ERR15" => "reserved",
              "ERR16" => "reserved",
              "ERR17" => "reserved",
              "ERR18" => "reserved",
              "ERR19" => "reserved",
              "ERR20" => "reserved"
                );


#if commanded, write errorcode in cheat_file
if($counter > 0)
{
# write errorcode in cheat_file
#ACTION: append cheat symptoms in cheat file
open(cheatFILE,"+< db_tt"); #open logfile for appending;
#flock(cheatFILE,2);		#LOCK_EX the file from other CGI instances
seek(cheatFILE,0,2);		#go to the end

printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
#CUSTOM
printf cheatFILE "\<br\>reported by: tugetxr2.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
}

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
#ins_gpl(); #this must exist
print qq!v.3.1.0\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
#print qq!<center>In situatiile de congestie, incercati din nou in cateva momente.<br> In situatia in care erorile persista va rugam sa ne contactati pe e-mail, pentru explicatii.</center>\n!;
print qq!</body>\n</html>\n!;

exit();

} #end sub

