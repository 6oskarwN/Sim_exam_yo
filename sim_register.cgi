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

#  sim_register.cgi v 3.2.d
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.d red warning for using passwords over http
# ch 3.2.c implemented trusted user creator
# ch 3.2.b check done for caller page to be $trid_pagecode=1
# ch 3.2.a charset=utf-8 added in generated html
# ch 3.2.9 whitelisting user input instead of blacklisting
# ch 3.2.8 functions moved to ExamLib.pm
# ch 3.2.7 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.6 extended registration period from 7 days to 14 days to observe the impact on user retention
# ch 3.2.5 compute_mac() changed from MD5 to SHA1 and user password is saved as hash for https://github.com/6oskarwN/Sim_exam_yo/issues/11
# ch 3.2.4 integrated sub timestamp_expired(); epoch replacing utc_time
# ch 3.2.3 changed next_login_time from 0 0 0 0 0 0 to 0 0 0 1 0 0
# ch 3.2.2 implemented silent discard Status 204 for https://github.com/6oskarwN/Sim_exam_yo/issues/5
# ch 3.2.1 deploy latest dienice()
# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3
# ch 3.0.5 table sync after sim_ver0 v 0.0.8
# ch 3.0.4 ANRCTI replaced by ANCOM
# ch 3.0.3 change "window" button with form method="link"
# ch 3.0.2 - slash permitted again, for development purpose
# ch 3.0.1 login-ul should not contain '/' character
# ch 3.0.0 OK button redirects from registration to authentication (ad-hoc improvement idea)
# ch 0.0.7 fixed trouble ticket 26
# ch 0.0.6 forestgreen and aquamarine colors changed to hex value
# ch 0.0.5 W3C audit passed
# ch 0.0.4 solved trouble ticket nr.7
# ch 0.0.3 solved trouble ticket nr.1 
# ch 0.0.2 solved trouble ticket nr. 4
# ch 0.0.1 generated from sim_register.cgi v.0.1.9, a HAM-eXam component

use strict;
use warnings;
use lib '.';
use My::ExamLib qw(ins_gpl timestamp_expired compute_mac dienice);

#GLOBAL VARIABLES
#variables extracted from POST data
my %answer=();		#hash used for depositing the answers
my $post_login;
my $post_passwd1;
my $post_passwd2;
my $post_tipcont;	#tip cont: 0-training, 1,2,3,4=cl 1,2,3,3r
my $post_trid;

#my $trid_id;                    #transaction ID extracted from transaction file
my $trid_login;                 #login extracted from transaction file
my $trid_pagecode;              #pagecode extracted from transaction file

#Global flags
my $f_valid_login;
my $f_valid_tipcont;
my $f_pass_eq;
my $f_xuser;					#flag says if login already exists in database

my @tridfile;					#slurped transaction file
my $trid;	#the Transaction-ID of the generated page
my $hexi;	#the trid+timestamp_ssh
my $entry;	#it's a bit of TRID

my $epochTime=time();	#epoch

my @slurp_userfile;            	#RAM-userfile

###########################################
#BLOCK: Process inputs ###
###########################################
{
my $buffer=();
my @pairs;
my $pair;
my $name;
my $value;

# Read input text, POST or GET

  if($ENV{'REQUEST_METHOD'} =~ m/GET/i) # i is modifier for case insensitive matching  
      {
      dienice ("ERR20",0,\"null");  #silently discard, Status 204 No Content
      }
## end of GET

else    { 
        read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
        }
#this else is not really nice but it's correct for the moment.

@pairs=split(/&/, $buffer); #POST-technology

#@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology

foreach $pair(@pairs) 
		{
($name,$value) = split(/=/,$pair);

#needed transform for text reflow, dar trateaza si + si / al token-ului

$value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$value=~ s/<*>*<*>/\//g; #inlocuiesc cu slash, sa dea eroare la check

if(defined($name) and defined($value)){

                 %answer = (%answer,$name,$value);        #hash filled in
					}

		} #.end foreach

} #.end process inputs

#now we have the hash table with answers. error: they can be less answers than needed
#or they can be less answers than all, but this is not error. answers for questions are not
#Mandatory, but Optional parameters. User can answer all or less questions.
#Occam check  -not implemented yet
#this should silently discard if not all mandatory parameters are received

$post_trid = $answer{'transaction'};
$post_login = $answer{'login'};
$post_passwd1 = $answer{'passwd1'};
$post_passwd2 = $answer{'passwd2'};
$post_tipcont = $answer{'tipcont'};




if(defined($post_trid)){} #do nothing
   else {dienice ("ERR01",1,\"undef trid"); } # no transaction or with void value

###############################
### combined refresh-search ###    
###############################

#BLOCK: Refresh transaction file, rewrite but don't close file
{
#ACTION: open transaction ID file
open(transactionFILE,"+< sim_transaction") or dienice("ERR01_op",1,\"err06-1");					#open transaction file for writing
flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances

#ACTION: refresh transaction file
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

my @livelist=();
my @linesplit;

# transaction pattern in file: 
# B00058_33_19_0_12_2_116_Trl5zxcXkaO5YcsWr4UYfg anonymous 0 33 19 0 12 2 116

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   chomp $linesplit[8]; #\n is deleted

#exam transactions are not refreshed here because sim_authent.cgi has ...
# ...a special refresh for punishing expired abandoned exams
if (($linesplit[2] > 3) && ($linesplit[2] < 8)) {@livelist=(@livelist, $i);}#if this is an exam transaction, don't touch it

# next 'if' is changed into 'elsif'
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8]) > 0 ) {} #if timestamp expired do nothing = transaction will not refresh
else {@livelist=(@livelist, $i);} #not expired, refresh it
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
my $missingLocally=1;  #flag which checks if posted transaction id is found in transaction file
                #flag init to 'not found'

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{  
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $post_trid) {
   				    $missingLocally=0;
                                    #$trid_id   =$linesplit[0]; #extract transaction
				    $trid_login=$linesplit[1]; #extract trid_login 
                                    $trid_pagecode=$linesplit[2]; #extract pagecode
				    #nu se adauga inregistrarea asta in @livelist
   				   }
	else {@livelist=(@livelist, $i);} #se adauga celelalte inregistrari in livelist
  } #.end for

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
  
} #.end unless

#**********************************************************************************
#if received transaction id was not found in the transaction file

if($missingLocally) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);		#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR02_cl",1,\"err07-1 $! $^E $?");

#now we should check why received transaction was not found in sim_transaction file
#case 0: it's an illegal transaction if MAC hash check fails
#        must be recorded in cheat_file
#case 1: MAC hash correct but transaction timestamp expired
#        must be announced to user
#case 2: MAC hash ok, timestamp ok, it must have been used up already OR might be a trusted hash

#check case 0
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ' - to be updated
#incoming is like 'trustee_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ' - to be updated
{ #local block start
my @pairs; #local
my $string_trid; # we compose the incoming transaction to recalculate mac
my $heximac;


@pairs=split(/_/,$post_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("regERR05",1,\$post_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("ERR01",1,\"transaction id sha1 mismatch: $post_trid");}

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6]) > 0) { 
                                             dienice("ERR02",0,\"timestamp was already expired"); }

#else is case 2
#must discriminate between the two types of transaction
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ' - transaction has been used already
#incoming is like 'trustee_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ' - trusted type of tansaction

if($pairs[0] =~ m/[0-9a-fA-F]{6}/) { dienice("regERR03",0,\"good transaction but already used");  } 
         else #MAC verifies, timestamp valid, not matching internal transaction - so it's a trusted request
                {
                  $trid_login = $pairs[0]; #name of trusted link
                  $trid_pagecode = 1; #allowed to register
		#verify if the transaction is revoked.
		my $isRevoked = 'n';
		#open sim_transaction read-only
		open(transactionFILE,"< sim_transaction") || dienice("admERR04",1,\"null"); #open readonly
		flock(transactionFILE,1);
		seek(transactionFILE,0,0);              #go to the beginning
		@tridfile = <transactionFILE>;          #slurp file into array
		#DEVEL
		for(my $i=0;($i <= $#tridfile and $isRevoked eq 'n');$i++) #search between saved transactions to see if it's revoked or not
			{
			if ($tridfile[$i] =~ $post_trid) {$isRevoked = 'y';} #if transaction contains the token then it is revoked
			}
		close(transactionFILE);

		if ($isRevoked eq 'y') { dienice("admERR06",0,\"null");}

		#if trusted transaction was not revoked, it can go ahead

                 #reopen the transaction file for read-write, that was closed for case 1,2,3a but should be open for 3b
                 open(transactionFILE,"+< sim_transaction") or dienice("ERR01_op",1,\"err06-4");		#open transaction file for writing
                 flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
		 seek(transactionFILE,0,0);		#go to the beginning
		 @tridfile = <transactionFILE>;		#slurp file into array

                 }

} #end of local block


} #.end expired
				
} #.END extraction BLOCK


#we have here the "login==anonymous" or "login = trust link name" and the pagecode of the guy
#ACTION: check request clearances pagecode == 1 (from sim_ver0 or sim_register)
#here the transaction file is open or closed #inconsistency
unless($trid_pagecode == 1) #CUSTOM: invoked from sim_ver0.cgi or sim_register page
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
my $cheatmsg="$trid_login, from wrong pagecode $trid_pagecode invoked sim_register.cgi";
dienice("verERR08",4,\$cheatmsg); #de customizat
}




#### sim_register.cgi specific logic

#BLOCK: Verify the POST data
{
#Action: Verify validity of login if it's an append form
#Verify by whitelist
if($post_login =~ /^[a-zA-Z0-9_]{4,25}$/) #must match regexp from sim_authent.cgi
       { $f_valid_login=0; } #password conforms whitelist
  else { $f_valid_login=1; }

#Action: Verify passwords by whitelist
if(($post_passwd1 =~ /^[a-zA-Z0-9!@#\$*\-_]{8,40}$/) && ($post_passwd2 =~ /^[a-zA-Z0-9!@#\$*\-_]{8,40}$/) && ($post_passwd1 eq $post_passwd2)) #must match regexp from sim_authent.cgi
       { $f_pass_eq=0; } #password conforms whitelist
  else { $f_pass_eq=1; }

#Action: Verify validity of tipcont. 0,1,2,3,4 only
if(($post_tipcont eq "0") || ($post_tipcont eq "1") || ($post_tipcont eq "2") || ($post_tipcont eq "3") || ($post_tipcont eq "4")) { $f_valid_tipcont=0;} #the condition is not accurate
else {$f_valid_tipcont=1;}
#$f_valid_tipcont=1;#debug only


$f_xuser=0;    #initializare


#ACTION: Verify for append only if login is unique in user database
#ACTION: open user account file

open(userFILE,"< sim_users") or dienice("ERR01_op",1,\"err06-2");	#open user file for writing
flock(userFILE,2);		#LOCK_EX the file from other CGI instances
seek(userFILE,0,0);		#go to the beginning
@slurp_userfile = <userFILE>;		#slurp file into array



#search record
unless($#slurp_userfile < 0) 		#unless  userlist is empty
{ #.begin unless
  for(my $account=0; $account < (($#slurp_userfile+1)/7); $account++)	#check userlist, account by account
  {
if($slurp_userfile[$account*7+0] eq "$post_login\n"){$f_xuser=1;}
  }
 } #.end unless empty userlist 

  
} #.END BLOCK

if($f_valid_login or $f_valid_tipcont or $f_pass_eq or $f_xuser)
#BLOCK: POST data is NOK, generate new form with a new transaction type 1/2
{
#Action: generate new transaction for the new form
#for regular transaction, will generate new transaction
#for trusted token, will just reuse the token

my @pairs; #local
@pairs=split(/_/,$post_trid); #reusing @pairs variable for spliting results
 
if($pairs[0] =~ m/[0-9a-fA-F]{6}/) #for regular transaction, will generate new transaction 
 { 

$trid=$tridfile[0];
chomp $trid;				#eliminate \n

$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF

#ACTION: generate a new transaction for anonymous

my $epochExpire = $epochTime + 900;		#15 min * 60 sec = 900 sec 
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];


#generate transaction id and its SHA1 MAC

$hexi= sprintf("%+06X",$trid); #the transaction counter
#assemble the trid+timestamp
$hexi= "$hexi\_$exp_sec\_$exp_min\_$exp_hour\_$exp_day\_$exp_month\_$exp_year\_"; #adds the expiry timestamp and MD5
#compute mac for trid+timestamp 
my $heximac = compute_mac($hexi); #compute MD5 MessageAuthentication Code
$hexi= "$hexi$heximac"; #the full transaction id

$entry = "$hexi anonymous 1 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n";

#printf "new entry: $entry<br>\n";
@tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array

#printf "new tridfile:<br> @tridfile[0..$#tridfile]<br>\n";
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

#print "Tridfile length befor write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR02_cl",1,\"err07-2 $! $^E $?");
}
else
{$hexi = $post_trid;} #else it's a trusted token, just copy&reuse without generating new transaction

#ACTION: Generate the form, again
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<meta charset=utf-8>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.d\n!; #version print for easy upload check
print qq!<h1 align="center"><font color="yellow">Eroare de completare formular</font></h1>\n!;
print "<br>\n";
#Action: Error descriptions in table
#print qq!<font color="yellow">Erori:</font><br>\n!;
print qq!<table border="0" width="80%" align="center"><tr><td>!;
if($f_valid_login) {print qq!<font color="yellow">- nume utilizator formatat incorect(vezi descrierea din dreptul parametrului)</font><br>\n!;}
if($f_xuser){print qq!<font color="yellow">- numele de utilizator ales există deja. Alege-ți un alt login.</font><br>\n!;}
if($f_valid_tipcont) {print qq!<font color="red">- $post_tipcont nu este o valoare acceptată</font><br>\n!;} #should be logged as cheat attempt maybe
if($f_pass_eq){print qq!<font color="yellow">- cele două parole nu sunt identice sau parola nu respectă normele de securitate(vezi descrierea din dreptul parametrului)</font><br>\n!;}
print qq!</td></tr></table>!;

print qq!<form action="http://localhost/cgi-bin/sim_register.cgi" method="post">\n!;
print qq!<p><center><b>Formular de înregistrare (valabil 15 minute)</b></center></p>\n!;

print qq!<table width="80%" align="center" border="1" bordercolor="red" cellpadding="4" cellspacing="2">\n!;
print qq!<tr><td>\n!;
print qq!Deoarece acest site este pe HTTP care transmite parolele în clar prin internet, vă rog să folosiți un login și parolă care dacă sunt furate, să nu fie relevante pentru altceva, să fie folosite doar aici, unde nu stochez date personale. Vă rog nu riscați să vă deschideți poarta altor conturi unde să folosiți aceeași combinație user+parolă\! Securitatea pe net e importantă dar veriga cea mai slabă e utilizatorul. Parolele sunt salvate de programul examyo în mod criptat dar asta e tot ce pot face. La acest provider de hosting gratuit nu se oferă certificat SSL gratuit de la Let's Encrypt, HTTPS este o opțiune contra-cost, 57EUR/an(accept sponsori pentru treaba asta)!;
print qq!</td></tr></table>\n!;

print qq!<table width="80%" align="center" border="1" cellpadding="4" cellspacing="2">\n!; 



print qq!<tr>\n!;
print qq!<td width="20%">!;
if($f_xuser or $f_valid_login) { print qq!<font color="yellow">Login:</font>!;}
else {print 'Login:';}
print qq!</td>\n!;

print qq!<td>!;
unless($f_xuser or $f_valid_login) {print qq!<input type="text" name="login"  value="$post_login" size="25">!;}
else {print qq!<input type="text" name="login" size="25">!;}
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Trebuie să aibă între 4 și 25 caractere din setul (a-z, A-Z, 0-9, _). login-ul trebuie să fie unic și să nu fie folosit deja.</font>!; #must match string from sim_ver0.cgi
print qq!</td>!;
print qq!</tr>\n!;
	 
print qq!<tr>\n!;
print qq!<td>!;
if($f_pass_eq) { print qq!<font color="yellow">Parola:</font>!;}
else {print 'Parola:';}
print qq!</td>\n!;
print qq!<td>!;
if($f_pass_eq) {print qq!<input type="password" name="passwd1" size="25">!;}
else {print qq!<input type="password" name="passwd1" value="$post_passwd1" size="25">!;}
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Parola trebuie să aibă între 8 și 25 caractere din setul (a-z, A-Z, 0-9, \!\@\#\$\*\-\_).</font>!; #must match string from sim_ver0.cgi
print qq!</td>!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td>!;
if($f_pass_eq) { print qq!<font color="yellow">Parola, din nou:</font>!;}
else {print 'Parola, din nou:';}
print qq!</td>\n!;
print qq!<td>!;
if($f_pass_eq) {print qq!<input type="password" name="passwd2" size="25">!;}
else {print qq!<input type="password" name="passwd2" value="$post_passwd2" size="25">!;}
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Trebuie să fie identică cu parola introdusă mai sus</font>!; 
print qq!</td>!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td>Tipul contului:</td>\n!;
print qq!<td><select size="1" name="tipcont">\n!;

print qq!<option value="0" !;
if(!$f_valid_tipcont && $post_tipcont eq "0"){ print qq!selected="y" !;}
print qq!>Cont de antrenament</option>\n!;

print qq!<option value="1" !;
if(!$f_valid_tipcont && ($post_tipcont eq "1")){ print qq!selected="y" !;}
print qq!>Examen simulat clasa I</option>\n!;

print qq!<option value="2" !;
if(!$f_valid_tipcont && ($post_tipcont eq "2")){ print qq!selected="y" !;}
print qq!>Examen simulat clasa II</option>\n!;

print qq!<option value="3" !;
if(!$f_valid_tipcont && ($post_tipcont eq "3")){ print qq!selected="y" !;}
print qq!>Examen simulat clasa III</option>\n!;

print qq!<option value="4" !;
if(!$f_valid_tipcont && ($post_tipcont eq "4")){ print qq!selected="y" !;}
print qq!>Examen simulat clasa IV</option>\n!;

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

print qq!</form><br>\n!;

print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="Abandon Inregistrare"></center>\n!; 
print qq!</form>\n!; 


print qq!</body>\n</html>\n!;
#ACTION: exit this process since it was an error
exit(); #ACTIVATE THIS since I think it must be here
} #.END BLOCK (NOK)
else
#BLOCK: POST data is OK, write it in userfile
{

unless ($trid_login eq "anonymous") {
                dienice("ERR19",1,\"$trid_login trusted link registered user: $post_login"); #silent logging user creation by trusted link
                #Action: revoke the trusted token
                $trid=$tridfile[0];  #take the transaction counter
                chomp $trid;                                            #eliminate \n
		$trid=hex($trid);               #convert string to numeric

		if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
		else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF

		#ACTION: generate a new transaction
		#trebuie extras timpul din tranzactie

		my @splitter = split(/_/,$post_trid); #reuse this vector name
		#generate transaction id and its sha1 MAC
		 $hexi= sprintf("%+06X",$trid); #the transaction counter

		#assemble the trid+timestamp
		$hexi= "$hexi\_$splitter[1]\_$splitter[2]\_$splitter[3]\_$splitter[4]\_$splitter[5]\_$splitter[6]\_"; #adds the expiry timestamp and sha1

		#compute mac for trid+timestamp
		my $heximac = compute_mac($hexi); #compute SHA1 MessageAuthentication Code

		$hexi= "$hexi$heximac"; #the full transaction id

		##CUSTOM: pagecode=3 for revoked tokens
		my $entry = "$hexi admin 3 $splitter[1] $splitter[2] $splitter[3] $splitter[4] $splitter[5] $splitter[6] $post_trid\n";
                @tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array

                                   } #.end silent logging and prepare revoked trusted transaction


#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or dienice("ERR02_cl",1,\"err07-3 $! $^E $?");

#BLOCK: re/write new user record
{
my $new_expiry; #generate for new user
my $epochExpire;
#ACTION: open user account file
open(userFILE,"+< sim_users") or dienice("ERR01_op",1,\"err06-3");	#open user file for writing
flock(userFILE,2);		#LOCK_EX the file from other CGI instances
seek(userFILE,0,0);		#go to the beginning
@slurp_userfile = <userFILE>;		#slurp file into array

#ACTION: generate account expiry time = +14 days from now (for all creation types, self- or inserted-)
#CUSTOM 14 * 24 * 60*60  = 1209600

if ($trid_login eq "anonymous") { $epochExpire = $epochTime + 1209600;} #CUSTOM
 else {$epochExpire = $epochTime + 15552000;} #6 months for the account created by trusted token

my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];
$new_expiry = "$exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n"; #\n is important

my $passHash=compute_mac($post_passwd1);
#ACTION: Append new record
@slurp_userfile = (@slurp_userfile,"$post_login\n"); #add login
@slurp_userfile = (@slurp_userfile,"0 0 0 1 0 0\n"); #add next allowed login time; $wday is [1..31]
@slurp_userfile = (@slurp_userfile,"$passHash\n"); #add password
@slurp_userfile = (@slurp_userfile,"0\n"); #add unsuccessful login attempts
@slurp_userfile = (@slurp_userfile,$new_expiry); #add account expiry time
@slurp_userfile = (@slurp_userfile,"$post_tipcont\n"); #add account type
@slurp_userfile = (@slurp_userfile,"0\n"); #add last awarded class - init:0

#ACTION: hard-rewrite userfile
truncate(userFILE,0);		#
seek(userFILE,0,0);				#go to beginning of transactionfile
for(my $i=0;$i <= $#slurp_userfile;$i++)
{
printf userFILE "%s",$slurp_userfile[$i]; #we have \n at the end of each element
}

close(userFILE);
} #.end BLOCK: re/write new user record


print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<meta charset=utf-8>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.d\n!; #version print for easy upload check
print qq!<h1 align="center">Înregistrare reușită.</h1>\n!;
print "<br>\n";

print "<center>Acum puteti sa va autentificati cu noile date.</center>\n";
print qq!<center>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_authent.cgi" method="post">\n!;
print qq!<input type="hidden" name="login"  value="$post_login">!;
print qq!<input type="hidden" name="passwd" value="$post_passwd1">!;
print qq!<center><INPUT type="submit"  value="OK"> </center>!;
print qq!</form>\n!; 
print qq!</center>\n!;
print "</body>\n</html>\n";

} #.END BLOCK (OK)


