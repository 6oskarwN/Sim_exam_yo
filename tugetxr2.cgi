#!/usr/bin/perl

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

#  tugetxr2.cgi v 3.2.5
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.5 functions moved to ExamLib.pm
# ch 3.2.4 implementing the revocation of admin token
# ch 3.2.3 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.2 input changet to POST to lower the chance for replay-attack with admin token.
# ch 3.2.1 md5 changed to sha1 in compute_mac()
# ch 3.2.0 implement a token exchange for authentication of the command
# ch 0.0.6 trouble ticket 25 implemented: minimal transaction info decoded: pagecode
# ch 0.0.5 removed the HAM-eXAM related file browsing(HAM-eXAM was decommisioned)
 
use strict;
use warnings;
use lib '.';
use My::ExamLib qw(timestamp_expired compute_mac dienice);

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
else {dienice ("tugERR01",2,\"undef token"); } # no token or with void value

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

unless(defined($post_token)) {dienice ("tugERR01",1,\"undef token"); } # no token or with void value
@pairs=split(/_/,$post_token); #reusing @pairs variable for spliting results
# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("tugERR01",2,\$post_token); } # unstructured token
$string_token="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_token);

unless($heximac eq $pairs[7]) { dienice("tugERR01",5,\$post_token);} #case of tampering

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) { 
                                             dienice("tugERR02",0,\"null"); }

#check case 2
 elsif ($pairs[0] ne 'admin') {dienice("tugERR03",3,\$post_token);}

#check case 3 (stub) if transaction is revoked. if is revoked, dienice()

my $isRevoked = 'n';
#open sim_transaction read-only
open(transactionFILE,"< sim_transaction") || dienice("tugERR04",1,\"null"); #open for appending
#flock(transactionFILE,1);
seek(transactionFILE,0,0);              #go to the beginning
@tridfile = <transactionFILE>;          #slurp file into array
#DEVEL
for(my $i=0;($i <= $#tridfile and $isRevoked eq 'n');$i++)
{
if ($tridfile[$i] =~ $post_token) {$isRevoked = 'y';}
}
close(transactionFILE);

if ($isRevoked eq 'y') { dienice("tugERR06",0,\"null");}

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
   if ($splitline[2] eq 0){ print qq!<small><font color="white">4-questions for humanity</font></small><br>\n!; }
elsif ($splitline[2] eq 1){ print qq!<small><font color="white">new user recording</font></small><br>\n!; }
elsif ($splitline[2] eq 2){ print qq!<small><font color="white">entry menu</font></small><br>\n!; }
elsif ($splitline[2] eq 3){ print qq!<small><font color="white">revoked token</font></small><br>\n!; }
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


