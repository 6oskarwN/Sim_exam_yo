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

# (c) YO6OWN Francisc TOTH, 2008 - 2020

#  sim_ver0.cgi v 3.2.b
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.b red warning for using unprotected passwords and http
# ch 3.2.a check done for caller page to be $trid_pagecode=0
# ch 3.2.9 charset=utf-8 added
# ch 3.2.8 whitelisting inputs 
# ch 3.2.7 functions moved to ExamLib.pm
# ch 3.2.6 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.5 compute_mac() changed from MD5 to SHA1
# ch 3.2.4 minor: change a dropdown option from class III-R to IV
# ch 3.2.3 implement epoch time and expired_timestamp with epoch
# ch 3.2.2 implemented silent discard Status 204
# ch 3.2.1 deploy latest dienice()
# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3
# ch 0.0.8 explanations moved to table
# ch 0.0.7 ANRCTI replaced by ANCOM
# ch 0.0.6 fixed rebel link from window type to method="link" button
# ch 0.0.5 fixed trouble ticket 26
# ch 0.0.4 forestgreen and aquamarine colors changed to hex value
# ch 0.0.3 W3C audit passed
# ch 0.0.2 solved trouble ticket nr. 1
# ch 0.0.1 generated from ver0.cgi of HAMEXAM

use strict;
use warnings;

use lib '.';
use My::ExamLib qw(ins_gpl timestamp_expired compute_mac dienice);

#-hash table for response retrieving
my %answer=();		#hash used for depositing the answers
my $post_trid;                  #transaction ID from POST data

my $debug_buffer; #debugging I/O


#my $trid_id;                    #transaction ID extracted from transaction file
my $trid_login;       		#login extracted from transaction file
my $trid_pagecode;		#pagecode extracted from transaction file 


#- for refreshing transaction list
my @tridfile;
my $trid;			#the Transaction-ID of the generated page
my $hexi;   			#the trid+timestamp_MD5
my $entry;              	#it's a bit of TRID
# - for search transaction in transaction list
my $expired;			#0 - expired/nonexisting transaction, n - existing transaction, n=pos. in the transaction list
my $correct;			#how many correct answers you gave




###########################################
#BLOCK: Process inputs ###
###########################################
{
my $buffer=();
my @pairs;
my $pair;
my $stdin_name;
my $stdin_value;

# Read input text, POST
if($ENV{'REQUEST_METHOD'} =~ m/POST/i)
     {
      read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
     }
else {dienice("ERR20",0,\"request method other than POST");} #request method other than POST is discarded

#transform params sent by POST
$buffer=~ tr/+/ /;
$buffer=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #special characters come like this

#split on &
@pairs=split(/&/, $buffer); #POST-technology


foreach $pair(@pairs)  {
        ($stdin_name,$stdin_value) = split(/=/,$pair);

if($stdin_name =~ m/^transaction$/){
         if ($stdin_value =~ m/^[0-9,A-F]{6}_(\d{1,2}_){5}\d{3}_[0-9,a-f]{40}$/)
                           {
           %answer = (%answer,$stdin_name,$stdin_value);        #hash filled in     
                           }
         else {dienice("ver0ERR05",1,\"whitelist catch on transaction, $stdin_value");}
                                    }
elsif($stdin_name =~ m/^answer$/){
         if ($stdin_value =~ m/^EVALUARE$/)
                           {     
           %answer = (%answer,$stdin_name,$stdin_value);        #hash filled in
                           }
         else {dienice("ver0ERR05",1,\"whitelist catch on EVALUARE text, $stdin_value");}
                                }

elsif( ($stdin_name =~ m/^question[0-9]{1,2}$/) and defined($stdin_value) and ($stdin_value =~ m/^[0-3]{1}$/))
          {
#next 4 transforms are specific to sim_verX
           $stdin_value =~ tr/0/a/;
	   $stdin_value =~ tr/1/b/;
	   $stdin_value =~ tr/2/c/;
	   $stdin_value =~ tr/3/d/;

           %answer = (%answer,$stdin_name,$stdin_value);        #hash filled in
	  }

		} #.end foreach
#check for existence of mandatory params:
if((defined $answer{'transaction'}) and (defined $answer{'answer'}))
  {
    $post_trid= $answer{'transaction'};
  }
  else{ dienice("verERR08",2,\"mandatory input missing"); }

} #.end process inputs

#now we have the hash table with answers. error: they can be less answers than needed
#or they can be less answers than all, but this is not error. answers for questions are not
#Mandatory, but Optional parameters. User can answer all or less questions.
#Occam check  -not fully implemented yet
# NOT IMPLEMENTED this should silently discard if not all mandatory parameters are received

unless(defined($post_trid)) 
       {dienice ("ERR01",1,\"undef trid"); } # no transaction or with void value

#ACTION: open transaction ID file
open(transactionFILE,"+< sim_transaction") or dienice("ERR01_op",1,\"$! $^E $?");		#open transaction file for writing
flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
{
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

#ACTION:read transaction ID
#-----------------------------------------------
#chomp($tridfile[0]);			#eliminate \n
#$tridfile[0]=hex($tridfile[0]);		#transform in numeral

#-----------------------------------
#-----------------------------------
my @livelist=();
my @linesplit;


# transaction pattern in file: 
# B00058_33_19_0_12_2_116_Trl5zxcXkaO5YcsWr4UYfg anonymous 0 33 19 0 12 2 116

unless($#tridfile == 0) 		#unless transaction list is empty
 {
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   chomp $linesplit[8]; #\n is deleted

#check if it's normal exam transaction
if ($linesplit[2] =~ /[4-7]/) {@livelist=(@livelist, $i);} #if this is an exam transaction, do not refresh it even it's expired, is the job of sim_authent.cgi


# next 'if' is changed into 'elsif'
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8]) > 0 ) {} #if timestamp expired do nothing = transaction will not refresh
else {					#not expired
       @livelist=(@livelist, $i);       #keep it in the transaction list
      } #.end else

 } #.end for
#we have now the list of the live transactions

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

} #.end unless
} #.END BLOCK

#BLOCK: extract data from actual transaction and then delete it
{
my @livelist=();
my @linesplit;
my $expired=1;  #flag which checks if transaction has expired

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{  
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $post_trid) {
                                    $expired=0;
                                    #$trid_id   =$linesplit[0]; #extract transaction
                                    $trid_login=$linesplit[1]; #extract login
                                    $trid_pagecode=$linesplit[2]; #extract pagecode
                                   }
	else {@livelist=(@livelist, $i);}
  } #.end for

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
  
} #.end unless

#**********************************************************************************
#if received transaction id was not found in the transaction file

if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or dienice("ERR02_cl",1,\"err08-1 $! $^E $?");

#now we should check why received transaction was not found in sim_transaction file
#case 0: it's an illegal transaction if MAC check fails
#        must be recorded in cheat_file
#case 1: MAC correct but transaction timestamp expired, file was refreshed and wiped this transaction
#        must be announced to user
#case 2: MAC ok, timestamp ok, it must have been used up already
#        must be announced to user

#check case 0
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ'
{ #local block start
my @pairs; #local
my $string_trid; # we compose the incoming transaction to recalculate mac
my $heximac;

#unless(defined($post_trid)) {dienice ("ERR01",1,\"undef trid"); } # no transaction or with void value

@pairs=split(/_/,$post_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ver0ERR05",1,\$post_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("ERR01",5,\"transaction id has been tampered with, sha1 mismatch: $post_trid");} #threat level 5

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6]) > 0) { 
                                             dienice("ERR02",0,\"timestamp expired"); } #normally not logged

#else is really case 2
else { dienice("ver0ERR03",0,\"null");  }

} #end of local block

#exit();

} #.end expired
				
} #.END extraction BLOCK

#we have here the "login = anonymous" and the pagecode of the guy
#ACTION: check request clearances pagecode == 0
unless($trid_pagecode == 0) #CUSTOM: invoked from humanity test page
{
#ACTION: close all resources
truncate(transactionFILE,0);
seek(transactionFILE,0,0);                              #go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR02_cl",1,\"$! $^E $?");

#ACTION: append cheat symptoms in cheat file
#CUSTOM
my $cheatmsg="$trid_login from wrong pagecode $trid_pagecode invoked sim_ver0.cgi";
dienice("verERR08",4,\$cheatmsg); #de customizat
}




####open db_human file
open(INFILE,"<", "db_human") || dienice("ERR01_op",1,\"$! $^E $?"); #open the question file
flock(INFILE,1);		        #shared lock, file can be read


	
#BLOCK: Evaluare rezultate
{
#### sort the questions using their numbers, like 'question21'
my @q_nr=(); #temp split array
my @feedback=(); #numeric list of answered questions
my @key_q=keys %answer; #only the names

#print qq!keys: @key_q[0..$#key_q]<br>\n!; #debug

my $temp;
foreach $temp (@key_q)
 {
  if($temp =~ /question/) {@q_nr=split(/question/,$temp);
  	@feedback=(@feedback,$q_nr[1]);
       }
  }
@feedback = sort{$a <=> $b} @feedback;

#print qq!Sorted: @feedback[0..$#feedback]<br>\n!;		#debug
#-------
my $item;
my $fline;

seek(INFILE,0,0);	#rewind
$fline = <INFILE>;	#sarim peste versioning string
$fline = <INFILE>;	#sarim peste nr de intrebari din database

$correct=0; #initializare

foreach $item (@feedback)
{
#print "item: $item <br>\n"; #debug
do {
$fline = <INFILE>;
chomp($fline);
} #.end do-while
while (!($fline =~ /##$item#/));
##s-a gasit intrebarea
$fline = <INFILE>;				#se citeste raspunsul corect
chomp($fline);
#print "Q$item = $fline, ";
$temp= sprintf("question%s",$item);
#print "raspuns: $answer{$temp} ";

if($answer{$temp} eq $fline) { #print qq!<font color="blue">OK</font>/ \n!; 
                               $correct++;}
else {
      #print qq!<font color="red">ERR</font>/ \n!;
	  }

} #.end foreach

##############################
## split results as correct ##
##############################

close( INFILE ) || dienice("ERR02_cl",1,\"$! $^E $?");

if($correct>=3)
{

#ACTION: generate a new transaction for anonymous

$trid=$tridfile[0];
chomp $trid;						#eliminate \n
$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF

my $epochTime=time();	#Counted since UTC 00000
#$epochTime is the "now"

#CHANGE THIS for customizing
my $epochExpire = $epochTime + 300;		#5 min * 60 sec = 300 sec 
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];


#generate transaction id and its md5 MAC

$hexi= sprintf("%+06X",$trid); #the transaction counter
#assemble the trid+timestamp
$hexi= "$hexi\_$exp_sec\_$exp_min\_$exp_hour\_$exp_day\_$exp_month\_$exp_year\_"; #adds the expiry timestamp and MD5
#compute mac for trid+timestamp 
my $heximac = compute_mac($hexi); #compute MD5 MessageAuthentication Code
$hexi= "$hexi$heximac"; #the full transaction id

$entry = "$hexi anonymous 1 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n"; 

#print qq!mio entry: $entry <br>\n!; #debug
@tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array
#print "Trid-array after adding new-trid: @tridfile[0..$#tridfile]<br>\n"; #debug

#.end of generation of new transaction

#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction file
#print "Tridfile length befor write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

#closing transaction file, opens flock by default
close (transactionFILE) or dienice("ERR02_cl",1,\"err08-2 $! $^E $?");


###Generate the registration form ###
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<meta charset=utf-8>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.b\n!; #version print for easy upload check
#print qq![$debug_buffer]\n!; #debug
print qq!<br>\n!;
print qq!<h1 align="center">OK, ai dat $correct răspunsuri corecte din 4 întrebări</h1>\n!;

#printing form

print qq!<form action="http://localhost/cgi-bin/sim_register.cgi" method="post">\n!;

print qq!<p><center><b>Formular de înregistrare (valabil 15 minute)</b></center></p>\n!;

print qq!<table width="80%" align="center" border="1" bordercolor="red" cellpadding="4" cellspacing="2">\n!; 
print qq!<tr><td>\n!;
print qq!Deoarece acest site este pe HTTP care transmite parolele în clar prin internet, vă rog să folosiți un login și parolă care dacă sunt furate, să nu fie relevante pentru altceva, să fie folosite doar aici, unde nu stochez date personale. Vă rog nu riscați să vă deschideți poarta altor conturi unde să folosiți aceeași combinație user+parolă\! Securitatea pe net e importantă dar veriga cea mai slabă e utilizatorul. Parolele sunt salvate de programul examyo în mod criptat dar asta e tot ce pot face. La acest provider de hosting gratuit nu se oferă certificat SSL gratuit de la Let's Encrypt, HTTPS este o opțiune contra-cost, 57EUR/an(accept sponsori pentru treaba asta)!;
print qq!</td></tr></table>\n!;

print qq!<table width="80%" align="center" border="1" cellpadding="4" cellspacing="2">\n!; 

print qq!<tr>\n!;
print qq!<td width="20%">!;
print qq!Login:!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="text" name="login" size="25">!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Trebuie să aibă între 4 și 25 caractere din setul (a-z, A-Z, 0-9, _). login-ul trebuie să fie unic și să nu fie folosit deja.</font>!; #must match string from sim_register.cgi
print qq!</td>!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td>!;
print 'Parola:';
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="password" name="passwd1" size="25">!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Parola trebuie să aibă între 8 și 25 caractere din setul(a-z, A-Z, 0-9, \!\@\#\$\*\-\_) </font>!;  #must match string from sim_register.cgi
print qq!</td>!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td>!;
print 'Parola, din nou:';
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="password" name="passwd2" size="25">!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Trebuie să fie identică cu parola introdusă mai sus</font>!; 
print qq!</td>!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td>Tipul contului:</td>\n!;
print qq!<td><select size="1" name="tipcont">\n!;
print qq!<option value="0">Cont de antrenament</option>\n!;
print qq!<option value="1">Examen simulat clasa I</option>\n!;
print qq!<option value="2">Examen simulat clasa II</option>\n!;
print qq!<option value="3">Examen simulat clasa III</option>\n!;
print qq!<option value="4">Examen simulat clasa IV</option>\n!;
print qq!</select>\n!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Contul de antrenament permite să dai oricâte examene, examenul simulat este unic.</font>!;
print qq!</td>!;
print qq!</tr>\n!;



print qq!<tr>\n!;
print qq!<td>!;
print qq!<center><INPUT type="submit"  value="Inregistreaza"> </center>!;
print qq!</td>\n!;

print qq!<td colspan="2">!;
print qq!<center><INPUT type="reset"  value="Reset"> </center>!;
print qq!</td>\n!;

print qq!</tr>\n!;

print qq!</table>\n!;


#ACTION: inserare transaction ID in pagina HTML
{
print qq!<input type="hidden" name="transaction" value="$hexi">\n!;
}

print qq!</form>\n<br>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="Abandon Inregistrare"></center>\n!; 
print qq!</form>\n!; 

print qq!</body>\n</html>\n!;
	       
exit(); #form it's printed, files are closed
} #daca ai avut cel putin 3 raspunsuri corect(din 4)

else {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction file
#print "Tridfile length befor write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

#closing transaction file, opens flock by default
close (transactionFILE) or dienice("ERR02_cl",1,\"err08-3 $! $^E $?");

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<meta charset=utf-8>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.b\n!; #version print for easy upload check
#print qq![$debug_buffer]\n!; #debug
print qq!<br>\n!;
print qq!<h1 align="center">Insuficient, ai nimerit doar $correct din 4 întrebări.</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!; 

exit();
     }

} #.end transaction evaluation


