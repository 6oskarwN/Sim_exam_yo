#!c:\Perl\bin\perl

#Prezentul simulator de examen impreuna cu formatul bazelor de intrebari, rezolvarile 
#problemelor, manual de utilizare, instalare, SRS, cod sursa si utilitarele aferente 
#constituie un pachet software gratuit care poate fi distribuit/modificat in termenii 
#licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in 
#versiunea 2 sau intr-o versiune ulterioara. Programul, intrebarile si raspunsurile sunt 
#distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio garantie, 
#sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii.
#Utilizatorul programului, manualelor, codului sursa si utilitarelor are toate drepturile
#descrise in licenta publica GPL.
#In distributia de pe https://github.com/6oskarwN/Sim_exam_yo trebuie sa gasiti o copie a 
#licentei GNU GPL, de asemenea si versiunea in limba romana, iar daca nu, ea poate fi
#descarcata gratuit de pe pagina http://www.fsf.org/
#Textul intrebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, 
#nefacand obiectul licentierii GNU GPL, copyrightul fiind al statului roman, dar 
#fiind folosibil in virtutea legii 544/2001 privind liberul acces la informatiile 
#de interes public precum al legii 109/2007 privind reutilizarea informatiilor din
#institutiile publice.

#This program together with question database formatting, solutions to problems, manuals, 
#documentation, sourcecode and utilities is a  free software; you can redistribute it 
#and/or modify it under the terms of the GNU General Public License as published by the 
#Free Software Foundation; either version 2 of the License, or any later version. This 
#program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY or
#without any implied warranty. See the GNU General Public License for more details. 
#You should have received a copy of the GNU General Public License along with this software
#distribution; if not, you can download it for free at http://www.fsf.org/ 
#Questions marked with ANCOM makes an exception of above-written, as ANCOM is a romanian
#public authority(similar to FCC in USA) so any use of the official questions, other than
#in Read-Only way, is prohibited. 

# Made in Romania

# (c) YO6OWN Francisc TOTH, 2008 - 2019

#  tugetxr2.cgi v 3.2.4
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.4 implementing the revocation of admin token
# ch 3.2.3 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.2 - input changet to POST to lower the chance for replay-attack with admin token.
# ch 3.2.1 - md5 changed to sha1 in compute_mac()
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
my @tridfile;                   #slurped transaction file

###########################################
### Process inputs, generate hash table ###
###########################################
{
my $buffer; #needed only for http POST
my $pair;
my $name;
my $value;

if($ENV{'REQUEST_METHOD'} eq "GET")
      {
      dienice ("ERR20",0,\"null");  #silently discard, Status 204 No Content
      }
## end of GET

else    {
	read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
        }


#read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST-technology, read
@pairs=split(/&/, $buffer); #POST-technology    #POST, split

#@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology, read and split
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
#case 0: check sha1 hash if correct
#        if not, must be recorded in cheat_file
#case 1: check if timestamp expired; if expired, no log in cheat
#case 2: check if it's an admin transaction
#case 3: check whether the admin transaction was revoked. if it is, dienice()
#        if none of above cases found, it's a valid one, go forward

my $string_token; # we compose the incoming transaction to recalculate mac
my $heximac;

unless(defined($post_token)) {dienice ("ERR01",1,\"undef token"); } # no token or with void value
@pairs=split(/_/,$post_token); #reusing @pairs variable for spliting results
# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ERR01",2,\$post_token); } # unstructured token
$string_token="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_token);

unless($heximac eq $pairs[7]) { dienice("ERR01",5,\$post_token);} #case of tampering

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) { 
                                             dienice("ERR02",0,\"null"); }

#check case 2
 elsif ($pairs[0] ne 'admin') {dienice("ERR03",3,\$post_token);}

#check case 3 (stub) if transaction is revoked. if is revoked, dienice()

my $isRevoked = 'n';
#open sim_transaction read-only
open(transactionFILE,"< sim_transaction") || dienice("ERR04",1,\"null"); #open for appending
#flock(transactionFILE,1);
seek(transactionFILE,0,0);              #go to the beginning
@tridfile = <transactionFILE>;          #slurp file into array
#DEVEL
for(my $i=0;($i <= $#tridfile and $isRevoked eq 'n');$i++)
{
if ($tridfile[$i] =~ $post_token) {$isRevoked = 'y';}
}
close(transactionFILE);

if ($isRevoked eq 'y') { dienice("ERR06",0,\"null");}

#ACTION: open sim_transaction ID file
open(transactionFILE,"< sim_transaction") or die("can't open simtrans file: $!\n");					#open transaction file for writing
#flock(transactionFILE,1);		#just a read-lock
seek(transactionFILE,0,0);              #go to the beginning

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
elsif ($splitline[2] eq 7){ print qq!<small><font color="white">ex. IV:</font></small><br>\n!; }

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


print qq!</body>\n</html>!;

#-------------------------------------
sub compute_mac {

use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
  hmac_sha1_hex($secret,$message);
} #end of compute_mac

#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year UTC
#out: seconds since expired MAX 99999, (-minus to 0] = not expired.

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

#-------------------------------------
# treat the "or die" and all error cases
#how to use it
#$error_code is a string, you see it, this is the text selector
#$counter: if it is 0, error is not logged. If 1..5 = threat factor
#reference is the reference to string that is passed to be logged.
#ERR19 and ERR20 have special handling

sub dienice
{
my ($error_code,$counter,$err_reference)=@_; #in vers. urmatoare counter e modificat in referinta la array/string

my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "authentication fail, logged.",
              "ERR02" => "authentication token expired",
              "ERR03" => "authentication fail, logged.",
              "ERR04" => "reserved $$err_reference",
              "ERR05" => "reserved",
              "ERR06" => "admin token revoked.",
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
              "ERR19" => "error not displayed",
              "ERR20" => "silent discard"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "token has been tampered with, sha1 mismatch",    #test ok
              "ERR02" => "untampered but timestamp expired",           #test ok
              "ERR03" => "good transaction but not an admin token",             #test ok
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "admin token revoked",
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
              "ERR19" => "silent logging(if $counter>0), not displayed",
	      "ERR20" => "silent discard,(logged only if $counter>0)"
                );


#if commanded, write errorcode in cheat_file
if($counter > 0)
{
# write errorcode in cheat_file

# count the number of lines in the db_tt by counting the '\n'
# open read-only the db_tt
my $CountLines = 0;
my $filebuffer;
#TBD - flock to be analysed if needed or not on the read-only count
           open(DBFILE,"< db_tt") or die "Can't open db_tt";
           while (sysread DBFILE, $filebuffer, 4096) {
               $CountLines += ($filebuffer =~ tr/\n//);
           }
           close DBFILE;

#CUSTOM limit db_tt writing to max number of lines (4 lines per record) 
if($CountLines < 200) #CUSTOM max number of db_tt lines (200/4=50 records)
{
#ACTION: append cheat symptoms in cheat file
open(cheatFILE,"+< db_tt"); #open logfile for appending;
#flock(cheatFILE,2);		#LOCK_EX the file from other CGI instances
seek(cheatFILE,0,2);		#go to the end
#CUSTOM
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: tugetxr2.cgi\<br\>  %s: %s \<br\> UTC Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
} #.end max number of lines
} #.end $counter>0

if($error_code eq 'ERR20') #must be silently discarded with Status 204 which forces browser stay in same state
{
print qq!Status: 204 No Content\n\n!;
print qq!Content-type: text/html\n\n!;
}
else
{
unless($error_code eq 'ERR19'){ #ERR19 is silent logging, no display, no exit()
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl(); #this must exist
print qq!v.3.1.0\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;
                              }
}

exit();

} #end sub
#--------------------------------------
sub ins_gpl
{
print qq+<!--\n+;
print qq!SimEx Radio Release \n!;
print qq!SimEx Radio was created originally for YO6KXP radio amateur club located in\n!; 
print qq!Sacele, ROMANIA (YO) then released to the whole radio amateur community.\n!;
print qq!\n!;
print qq!Prezentul simulator de examen impreuna cu formatul bazelor de intrebari, rezolvarile problemelor, manual de utilizare,\n!; 
print qq!instalare, SRS, cod sursa si utilitarele aferente constituie un pachet software gratuit care poate fi distribuit/modificat in \n!;
print qq!termenii licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in versiunea 2 sau intr-o versiune \n!;
print qq!ulterioara. Programul, intrebarile si raspunsurile sunt distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio \n!;
print qq!garantie, sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii. Utilizatorul programului, \n!;
print qq!manualelor, codului sursa si utilitarelor are toate drepturile descrise in licenta publica GPL.\n!;
print qq!In distributia de pe https://github.com/6oskarwN/Sim_exam_yo trebuie sa gasiti o copie a licentei GNU GPL, de asemenea \n!;
print qq!si versiunea in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/\n!;
print qq!Textul intrebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL, \n!;
print qq!copyrightul fiind al statului roman, dar fiind folosibil in virtutea legii 544/2001 privind liberul acces la informatiile \n!;
print qq!de interes public precum al legii 109/2007 privind reutilizarea informatiilor din institutiile publice.\n!;
print qq!\n!;
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;
print qq!This program together with question database formatting, solutions to problems, manuals, documentation, sourcecode \n!;
print qq!and utilities is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License \n!;
print qq!as published by the Free Software Foundation; either version 2 of the License, or any later version. This program is distributed \n!;
print qq!in the hope that it will be useful, but WITHOUT ANY WARRANTY or without any implied warranty. See the GNU General Public \n!;
print qq!License for more details. You should have received a copy of the GNU General Public License along with this software distribution; \n!;
print qq!if not, you can download it for free at http://www.fsf.org/ \n!;
print qq!Questions marked with ANCOM makes an exception of above-written, as ANCOM is a romanian public authority(similar to FCC \n!;
print qq!in USA) so any use of the official questions, other than in Read-Only way, is prohibited. \n!;
print qq!\n!;
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;
print qq!Made in Romania\n!;
print qq+-->\n+;

}

