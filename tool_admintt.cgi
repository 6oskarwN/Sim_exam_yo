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

#  tool_admintt.cgi v 3.2.5
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.5 functions moved to ExamLib.pm
# ch 3.2.4 implementing the revocation of admin token
# ch 3.2.3 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.2 MD5 changed to sha1 in compute_mac() 
# ch 3.2.1 implemented silent discard Status 204
# ch 3.2.0 implement admin authentication using an md5 token, guestbook should be alliminated
# ch 0.0.6 displaying db_tt data better after sim_ver1 and troubleticket solved &specials; "overline" problems
# ch 0.0.5 using POST 
# ch 0.0.4 expelled KXP from title, has nothing to do now
# ch 0.0.3 added >>if (defined $ENV{'QUERY_STRING'})<<
# ch 0.0.2 solved troubleticket19


use strict;
use warnings;
use lib '.';
use My::ExamLib qw(ins_gpl timestamp_expired compute_mac dienice);


#-hash table for response retrieving
my %answer=();    #hash used for depositing the answers
my $post_token;   #token from input data
my $get_buffer; #intrarea originala

my $call_switch=0; #1 - correct first call,only token, shows the listing
            #2 - correct 2nd call, token+reflow text, will modify
            #3 - admin token revoke call, will add special transaction
            #0 - bogus call - not even token received
            
my @pairs;
my @tridfile;                   #slurped transaction file
my $trid;                    #transaction ID extracted from transaction file
my @splitter;

my $fline; #linia de fisier
my @dbtt;  #for slurp
my @newdbtt; #for writeback

###########################################
#BLOCK: Process inputs ###
###########################################
{
my $buffer=();
my $pair;
my $kee;
my $name;
my $value;

# Read input text, POST or GET
  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case 
  if($ENV{'REQUEST_METHOD'} eq "GET") 
  { 
dienice ("ERR20",0,\"null");  #silently discard, Status 204 No Content
       }
## end of GET

else    { 
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
        }

@pairs=split(/&/, $buffer); #split into name - value pairs
                      
#print qq!input: $buffer <br><br>\n!; #debug

foreach $pair(@pairs) 
		{
($name,$value) = split(/=/,$pair);

#transformarea asta e pentru textele reflow, dar trateaza si + si / al token-ului MD5(obsolete)
$value=~ s/\+/ /g; 
$value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$value=~ s/\r\l\n$//g;
$value=~ s/\r\l\n/<br>/g;

 %answer = (%answer,$name,$value); #hash filled in with key+value

		} #end foreach

#hash it is filled in now

$post_token = $answer{'token'}; #extract token from input data
## double POST debug
#not implemented
#@ Occam check
#not implemented




#print qq!token received: $post_token<br>\n!; #debug
#token pattern: 
# admin_33_19_0_12_2_116_96f51641c44348b2626316a840e01f7fb32ce759

#now we should check received transaction
#case 0: check sha1 hash if correct
#        if not, must be recorded in cheat_file
#case 1: check if timestamp expired; if expired, no log in cheat
#case 2: check if it's an admin transaction
#case 3: check whether the admin transaction was revoked. if it is, dienice()
#        if none of above cases found, it's a valid one, go forward

my $string_token; # we compose the incoming transaction to recalculate mac
my $heximac;

unless(defined($post_token)) {dienice ("admERR01",1,\"undef token"); } # no token or with void value
@pairs=split(/_/,$post_token); #reusing @pairs variable for spliting results
# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("admERR01",2,\$post_token); } # unstructured token
$string_token="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_token);

unless($heximac eq $pairs[7]) { dienice("admERR01",5,\$post_token);} #case of tampering

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) { 
                                             dienice("admERR02",0,\"null"); }

#check case 2
 elsif ($pairs[0] ne 'admin') {dienice("admERR03",3,\$post_token);}

#check case 3 (stub) if transaction is revoked. if is revoked, dienice()

my $isRevoked = 'n';
#open sim_transaction read-only
open(transactionFILE,"< sim_transaction") || dienice("admERR04",1,\"null"); #open for appending
#flock(transactionFILE,1);
seek(transactionFILE,0,0);              #go to the beginning
@tridfile = <transactionFILE>;          #slurp file into array
#DEVEL
for(my $i=0;($i <= $#tridfile and $isRevoked eq 'n');$i++)
{
if ($tridfile[$i] =~ $post_token) {$isRevoked = 'y';}
}
close(transactionFILE);

if ($isRevoked eq 'y') { dienice("admERR06",0,\"null");}

#we determine here if is display order ($call_switch=1) or writing order(=2) or revoke order (=3)

if( exists($answer{'admintxt0'}) and exists($answer{'token'})) { $call_switch = 2;}
elsif(exists($answer{'revoke'}) and $answer{'revoke'} eq 'yes' and exists($answer{'token'})) {$call_switch = 3;}
elsif(exists($answer{'token'})) {$call_switch = 1;}
else {$call_switch = 0; }

#print qq!call_switch: $call_switch<br>\n!;#debug

} #.end block process inputs
#-----------

#### if it's 1st type call(display was ordered)

if($call_switch == 1) #it's  a display order
{
open(INFILE,"<","db_tt") or die(); #open read-only the tickets file

#flock(INFILE,1);		        #LOCK_SH, file can be read

seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>; #slurp

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v 3.2.5</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="#228b22" text="black" link="white" alink="white" vlink="white">\n!;

print qq!<center>\n!;
print qq!<font color="white">Troubleticket administration v 3.2.5 for examYO &copy; YO6OWN, 2007-2019</font><br>\n!;
print qq!<form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;

print qq!<table border="1" width="90%">\n!;

#se parcurge fisierul de-andoaselea si se afiseaza toate inregistrarile de guestbook
for(my $i=0;$i<($#dbtt+1)/4;$i++)
{
print qq!<tr>\n!;
if($dbtt[$i*4+1] < 6){
print qq!<td bgcolor="lightblue">\n!;
                     }
else {print qq!<td bgcolor="lightgreen">\n!;
      } 

chomp $dbtt[$i*4+1];

print qq!<font color="black"><b>$dbtt[$i*4]</b></font>&nbsp;!;  #print nick

if($dbtt[$i*4+1] < 6)     #if it's a guestbook record
                    {
for (my $istar=0; $istar < $dbtt[$i*4+1]; $istar++)
{print qq!<IMG src="http://localhost/star.gif" WIDTH="15">\n!;
}
                     } #.end it's a guestbook record
else {   #else it is a trouble ticket
print qq!<select size="1" name="rating$i">\n!;

if($dbtt[$i*4+1] eq 6) {print qq!<option value="6" selected="y">nou</option>\n!;}
         else          {print qq!<option value="6">nou</option>\n!;}
if($dbtt[$i*4+1] eq 7) {print qq!<option value="7" selected="y">citit de admin</option>\n!;}
         else          {print qq!<option value="7">citit de admin</option>\n!;}
if($dbtt[$i*4+1] eq 8) {print qq!<option value="8" selected="y">rezolvat</option>\n!;}
         else          {print qq!<option value="8">rezolvat</option>\n!;}

print qq!</select>\n!;
print qq!\n!;
} #else trouble ticket

my $toprint=$dbtt[$i*4+2];
$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

print qq!<font color="black" size="-1">$toprint</font><br>\n!;

unless ($dbtt[$i*4+3] eq "\n") {
print qq!<textarea name="admintxt$i" rows="3" cols="120" wrap="soft">$dbtt[$i*4+3]</textarea>\n!;
                               }
                               else {
                               print qq!<textarea name="admintxt$i" rows="2" cols="120" wrap="soft"></textarea>\n!;
                                    }
                   print qq!>>> Delete record: <input type="checkbox" value="on" name="delete$i">!;
print qq!</td>\n!;
print qq!</tr>\n!;                              

} #.end for/4
#----------------------

print qq!</table>\n!;

print qq!<center><INPUT type="hidden" name="token" value="$post_token">\n!;
print qq!<center><INPUT type="submit"  value="Modify">\n!;
print qq!<INPUT type="reset"  value="Reset"> </center>\n!;
print qq!</form>\n!;
print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;
print qq!<center><INPUT type="hidden" name="token" value="$post_token">\n!;
print qq!<center><INPUT type="submit"  value="Refresh"> </center>\n!;
print qq!</form>\n!;
print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;
print qq!<center><INPUT type="hidden" name="token" value="$post_token">\n!;
print qq!<center><INPUT type="hidden" name="revoke" value="yes">\n!;
print qq!<center><INPUT type="submit"  value="Revoke Admin token"> </center>\n!;
print qq!</form>\n!;
print qq!</center>!;
#}
print qq!</body>\n!;
print qq!</html>\n!;

close (INFILE) || die("cannot close, $!\n");
#} #.end if(open(db_tt))
#else  {dienice("admERR04",0,\"null");}
} #.end first call of tool_admintt.cgi


#### if it's 2nd type call

elsif ($call_switch == 2)    #it's 2nd call if  'admintxt0=' exists - should be imlpemented
{

open(INFILE,"+<","db_tt"); #am fixat la db_tt, ca un hacker sa poata corupe doar pe asta.
seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>;

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v 3.2.5</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="gray" text="black" link="white" alink="white" vlink="white">\n!;

for(my $ki=0;$ki<($#dbtt+1)/4;$ki++)
{

if(exists $answer{"delete$ki"}) #daca exista vreo modificare de hash pt aceast ainregistrare
                              {} #do nothing, do not copy it over
 else #make replacements    
 {
@newdbtt=(@newdbtt,$dbtt[$ki*4]); #nick unchanged
if(exists $answer{"rating$ki"}) {@newdbtt=(@newdbtt,$answer{"rating$ki"});
                                 @newdbtt=(@newdbtt,"\n"); 
                                }
else {@newdbtt=(@newdbtt,$dbtt[$ki*4+1]);}
 
@newdbtt=(@newdbtt,$dbtt[$ki*4+2]); #text unchanged

if(exists $answer{"admintxt$ki"}) {@newdbtt=(@newdbtt,$answer{"admintxt$ki"});
                                   @newdbtt=(@newdbtt,"\n"); 
                                   }
else {@newdbtt=(@newdbtt,$dbtt[$ki*4+1]);}

 }                       
}

print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;
print qq!<input type="text" name="token" size="40" value="$post_token"><br>\n!;
print qq!<input type="submit" value="AGAIN">\n!;
print qq!</form></center>\n!; 
print qq!</body></html>!;

truncate(INFILE,0);			#
seek(INFILE,0,0);				#go to beginning of transactionfile
for(my $j=0;$j <= $#newdbtt;$j++)
{
printf INFILE "%s",$newdbtt[$j]; #we have \n at the end of each element
}
close(INFILE);
} #.end 2nd type call

#### if it's 3rd type call
# we must produce here the revoke transaction

elsif ($call_switch == 3)    #it's 3rd type call if  token and revoke command exists
{


#ACTION: open transaction ID file and adds revoked transaction

open(transactionFILE,"+< sim_transaction") || dienice("admERR04",1,\"null"); #open for appending
#flock(transactionFILE,2);

seek(transactionFILE,0,0);              #go to the beginning


@tridfile = <transactionFILE>;          #slurp file into array
$trid=$tridfile[0];  #take the first
chomp $trid;						#eliminate \n

$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF

#ACTION: generate a new transaction

##print qq!generate new transaction<br>\n!;
#trebuie extras timpul din tranzactie
@splitter = split(/_/,$post_token);

#generate transaction id and its sha1 MAC
my $hexi= sprintf("%+06X",$trid); #the transaction counter

#assemble the trid+timestamp
$hexi= "$hexi\_$splitter[1]\_$splitter[2]\_$splitter[3]\_$splitter[4]\_$splitter[5]\_$splitter[6]\_"; #adds the expiry timestamp and sha1

#compute mac for trid+timestamp
my $heximac = compute_mac($hexi); #compute SHA1 MessageAuthentication Code

$hexi= "$hexi$heximac"; #the full transaction id

##CUSTOM: pagecode=3 for revoked tokens
my $entry = "$hexi admin 3 $splitter[1] $splitter[2] $splitter[3] $splitter[4] $splitter[5] $splitter[6] $post_token\n";

#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);                              #go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
printf transactionFILE "%s",$entry; #we have \n at the end of each element

close(transactionFILE) || dienice("admERR04",1,\"null");
dienice("admERR05",0,\"null"); #finish the script here with a message

} #.end 3rd type call


else #bogus calls, do no offer them any chance to guess the right form of calling
{
dienice("admERR04",5,\"bogus"); #shouldn't we give a 204?
}
#-------------------------------------



