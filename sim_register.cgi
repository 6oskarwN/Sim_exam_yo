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

#Made in Romania

# (c) YO6OWN Francisc TOTH, 2008 - 2016

#  sim_register.cgi v 3.2.1
#  Status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.1 deploy latest dienice()
# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3
# ch 3.0.5 table sync dupa sim_ver0 v 0.0.8
# ch 3.0.4 ANRCTI replaced by ANCOM
# ch 3.0.3 inlocuit buton "window" cu form method="link"
# ch 3.0.2 - slash permitted again, for development purpose
# ch 3.0.1 eliminam / din caracterele ce pot forma login-ul
# ch 3.0.0 butonul de la OK face direct request de autentificare la authent.cgi(ad-hoc improvement idea)
# ch 0.0.7 fixed trouble ticket 26
# ch 0.0.6 forestgreen and aquamarine colors changed to hex value
# ch 0.0.5 W3C audit passed
# ch 0.0.4 solved trouble ticket nr.7
# ch 0.0.3 solved trouble ticket nr.1
# ch 0.0.2 solved trouble ticket nr. 4
# ch 0.0.1 generated from sim_register.cgi v.0.1.9, a HAM-eXam component

use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

#GLOBAL VARIABLES
#variables extracted from POST data
my $post_login;
my $post_passwd1;
my $post_passwd2;
my $post_tipcont;	#tip cont: 0-training, 1,2,3,4=cl 1,2,3,3r

my $post_trid;

my $trid_login; #the username from the transactionfile, corresponding to the active transaction

#Global flags
my $f_valid_login;
my $f_valid_tipcont;
my $f_pass_eq;
my $f_xuser;					#flag says if login already exists in database

my @tridfile;					#slurped transaction file
my $trid;	#the Transaction-ID of the generated page
my $hexi;	#the trid+timestamp_MD5
my $entry;	#it's a bit of TRID

my @utc_time=gmtime(time);     	#the 'present' time, generated only once

my @slurp_userfile;            	#RAM-userfile

#BLOCK: Input: acquire input data
{
my $buffer;
my @pairs;
my $pair;
my $stdin_name;
my $stdin_value;


@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology

foreach $pair(@pairs) {
($stdin_name,$stdin_value) = split(/=/,$pair);

$stdin_value=~ s/\+/ /g;
$stdin_value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$stdin_value=~ s/<*>*<*>//g;

#nu e tratat cazul in care ceva este undefined.

if($stdin_name eq 'login') {$post_login=$stdin_value;}
elsif($stdin_name eq 'passwd1') {$post_passwd1=$stdin_value;}
elsif($stdin_name eq 'passwd2') {$post_passwd2=$stdin_value;}
elsif($stdin_name eq 'tipcont') {$post_tipcont=$stdin_value;}
elsif($stdin_name eq 'transaction') {$post_trid=$stdin_value;}
} #.end foreach
} #.end block
#.END BLOCK

#md MAC has + = %2B and / = %2F characters, must be reconverted
if(defined($post_trid)){
	$post_trid =~ s/%2B/\+/g;
	$post_trid =~ s/%2F/\//g;
			}
   else {dienice ("ERR04",1,\"undef trid"); } # no transaction or with void value

###############################
### combined refresh-search ###    
###############################

#BLOCK: Refresh transaction file, rewrite but don't close file
{
#ACTION: open transaction ID file
open(transactionFILE,"+< sim_transaction") or dienice("ERR06",1,\"err06-1");					#open transaction file for writing
#flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances

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

#exam transactions are not refreshed here because sim_authent.cgi has special refresh 
#for punishing expired abandoned exams
if (($linesplit[2] > 3) && ($linesplit[2] < 8)) {@livelist=(@livelist, $i);}#if this is an exam transaction, don't touch it

# next 'if' is changed into 'elsif'
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8])) {} #if timestamp expired do nothing = transaction will not refresh
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
my $expired=1;  #flag which checks if posted transaction id is found in transaction file
                #flag init to 'not found'

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{  
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $post_trid) {
   				    $expired=0;
				    $trid_login=$linesplit[1]; #extract trid_login
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

if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);		#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR07",1,\"err07-1");

#now we should check why received transaction was not found in sim_transaction file
#case 0: it's an illegal transaction if md5 check fails
#        must be recorded in cheat_file
#case 1: md5 correct but transaction timestamp expired, file was refreshed and wiped this transaction
#        must be announced to user
#case 2: md5 ok, timestamp ok, it must have been used up already
#        must be announced to user

#check case 0
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ'
{ #local block start
my @pairs; #local
my $string_trid; # we compose the incoming transaction to recalculate mac
my $heximac;


@pairs=split(/_/,$post_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ERR05",1,\$post_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("ERR01",1,\$post_trid);}

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])) { 
                                             dienice("ERR02",0,\"null"); }

#else is really case 2
else { dienice("ERR03",0,\"null");  }

} #end of local block


#exit(); #still needed? is this exit() ever active?

} #.end expired
				
} #.END extraction BLOCK

#### sim_register.cgi specific logic

#BLOCK: Verify the POST data
{
#Action: Verify validity of login if it's an append form
if($post_login =~ / /) { $f_valid_login=1; } #login has multiple words!
elsif($post_login =~ /\+/) { $f_valid_login=1; } #login has nasty character!
elsif($post_login =~ /%/) { $f_valid_login=1; } #login has nasty character!
elsif((length $post_login < 4) or (length $post_login > 25)) {$f_valid_login=1}
else { $f_valid_login=0;}

#Action: Verify passwords
if    ($post_passwd1 =~ / /){ $f_pass_eq=1; }  #if there are multiple words
elsif ($post_passwd2 =~ / /){ $f_pass_eq=1; }  #if there are multiple words
elsif ((length $post_passwd1 < 8) or (length $post_passwd1 > 25)) {$f_pass_eq=1;}
elsif ((length $post_passwd2 < 8) or (length $post_passwd2 > 25)) {$f_pass_eq=1;}
elsif ($post_passwd1 eq $post_passwd2) {$f_pass_eq=0;}
else {$f_pass_eq=1;}

#Action: Verify validity of tipcont. 0,1,2,3,4 only
if(($post_tipcont eq "0") || ($post_tipcont eq "1") || ($post_tipcont eq "2") || ($post_tipcont eq "3") || ($post_tipcont eq "4")) { $f_valid_tipcont=0;} #the condition is not accurate
else {$f_valid_tipcont=1;}
#$f_valid_tipcont=1;#debug only


$f_xuser=0;    #initializare


#ACTION: Verify for append only if login is unique in user database
#ACTION: open user account file

open(userFILE,"< sim_users") or dienice("ERR06",1,\"err06-2");	#open user file for writing
#flock(userFILE,2);		#LOCK_EX the file from other CGI instances
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
#Action: generate new transaction
$trid=$tridfile[0];
chomp $trid;						#eliminate \n

$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF


#ACTION: generate a new transaction for anonymous

my $exp_sec=$utc_time[0];
my $exp_min=$utc_time[1];
my $exp_hour=$utc_time[2];
my $exp_day=$utc_time[3];
my $exp_month=$utc_time[4];
my $exp_year=$utc_time[5];
my $carry1=0;
my $carry2=0;
my %month_days=(
    0 => 31,	#january
    1 => 28,	#february
    2 => 31,	#march
    3 => 30,	#april
    4 => 31,	#may
    5 => 30,    #june
    6 => 31,	#july
    7 => 31,	#august
    8 => 30,	#september
    9 => 31,	#october
   10 => 30, 	#november
   11 => 31     #december
);
my %month_bis_days=(
    0 => 31,	#january
    1 => 29,	#february, bisect
    2 => 31,	#march
    3 => 30,	#april
    4 => 31,	#may
    5 => 30,    #june
    6 => 31,	#july
    7 => 31,	#august
    8 => 30,	#september
    9 => 31,	#october
   10 => 30, 	#november
   11 => 31     #december
);


#CHANGE THIS for customizing
my $expire=15;		#15 minutes in this situation

#increment expiry time

#minute increment
$carry1= int(($exp_min+$expire)/60);		#check if minutes overflow
$exp_min=($exp_min+$expire)%60;			#increase minutes

#hour increment
$carry2= int(($exp_hour+$carry1)/24);		#check if hours overflow
$exp_hour=($exp_hour+$carry1)%24;		#increase hours

#day increment
if($exp_year%4) {
$carry1=int(($exp_day+$carry2)/($month_days{$exp_month}+1));  #check if day overflows
$exp_day=($exp_day+$carry2)%($month_days{$exp_month}+1); #increase day if so
	        }
else		{
$carry1=int(($exp_day+$carry2)/($month_bis_days{$exp_month}+1));  #check if day overflows
$exp_day=($exp_day+$carry2)%($month_bis_days{$exp_month}+1); #increase day if so
		}
if($carry1) {$exp_day=1;}	#day starts with 1-anomaly solution

#month increment
$carry2=int(($exp_month+$carry1)/12);
$exp_month=($exp_month+$carry1)%12;
#year increment
$exp_year += $carry2;

#generate transaction id and its md5 MAC

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

close (transactionFILE) or dienice("ERR07",1,\"err07-2");
#ACTION: Generate the form, again
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.1\n!; #version print for easy upload check
print qq!<h1 align="center"><font color="yellow">Eroare de completare formular</font></h1>\n!;
print "<br>\n";
#Action: Error descriptions in table
#print qq!<font color="yellow">Erori:</font><br>\n!;
print qq!<table border="0" width="80%" align="center"><tr><td>!;
if($f_valid_login) {print qq!<font color="yellow">-nume utilizator formatat incorect(vezi mai jos)</font><br>\n!;}
if($f_xuser){print qq!<font color="yellow">-numele de utilizator ales exista deja. Alege-ti un alt login.</font><br>\n!;}
if($f_valid_tipcont) {print qq!<font color="red">-$post_tipcont nu este o valoare acceptata</font><br>\n!;} #should be written in cheat_log, but it's an anonymous
if($f_pass_eq){print qq!<font color="yellow">-cele doua parole nu sunt identice sau parola nu respecta normele de securitate(vezi mai jos)</font><br>\n!;}
print qq!</td></tr></table>!;

print qq!<form action="http://localhost/cgi-bin/sim_register.cgi" method="get">\n!;
print qq!<p><center><b>Formular de inregistrare (valabil 15 minute)</b></center></p>\n!;

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
print qq!<font size="-1">Trebuie sa aiba intre 4 si 25 caractere. Nu se accepta caractere speciale: %, space; login-ul trebuie sa fie unic si sa nu fie folosit deja.</font>!;
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
print qq!<font size="-1">Parola trebuie sa aiba intre 8 si 25 caractere; nu poate contine caracterele %, space</font>!; 
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
print qq!<font size="-1">Trebuie sa fie identica cu parola introdusa mai sus</font>!; 
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
print qq!>Examen simulat clasa III-R</option>\n!;

print qq!</select>\n!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<font size="-1">Contul de antrenament permite sa dai oricate examene, examenul simulat este unic.</font>!;
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
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR07",1,\"err07-3");

#BLOCK: re/write new user record
{
my $new_expiry; #generat

#ACTION: open user account file
open(userFILE,"+< sim_users") or dienice("ERR06",1,\"err06-3");	#open user file for writing
#flock(userFILE,2);		#LOCK_EX the file from other CGI instances
seek(userFILE,0,0);		#go to the beginning
@slurp_userfile = <userFILE>;		#slurp file into array

#ACTION: generate account expiry time = +7 days from now
my $exp_sec=$utc_time[0];
my $exp_min=$utc_time[1];
my $exp_hour=$utc_time[2];
my $exp_day=$utc_time[3];
my $exp_month=$utc_time[4];
my $exp_year=$utc_time[5];
my $carry1=0;
my $carry2=0;
my %month_days=(
    0 => 31,	#january
    1 => 28,	#february
    2 => 31,	#march
    3 => 30,	#april
    4 => 31,	#may
    5 => 30,    #june
    6 => 31,	#july
    7 => 31,	#august
    8 => 30,	#september
    9 => 31,	#october
   10 => 30, 	#november
   11 => 31     #december
);
my %month_bis_days=(
    0 => 31,	#january
    1 => 29,	#february, bisect
    2 => 31,	#march
    3 => 30,	#april
    4 => 31,	#may
    5 => 30,    #june
    6 => 31,	#july
    7 => 31,	#august
    8 => 30,	#september
    9 => 31,	#october
   10 => 30, 	#november
   11 => 31     #december
);

#CHANGE THIS if you want to customize
#$carry1=1; #1 month from now until the account expires

#CHANGE THIS if you want to customize
$carry2=7;  #account lives 7 days


#day increment
if($exp_year%4) {
$carry1=int(($exp_day+$carry2)/($month_days{$exp_month}+1));  #check if day overflows
$exp_day=($exp_day+$carry2)%($month_days{$exp_month}+1); #increase day if so
	        }
else		{
$carry1=int(($exp_day+$carry2)/($month_bis_days{$exp_month}+1));  #check if day overflows
$exp_day=($exp_day+$carry2)%($month_bis_days{$exp_month}+1); #increase day if so
		}
if($carry1) {$exp_day=1;}	#day starts with 1-anomaly solution

#month increment
$carry2=int(($exp_month+$carry1)/12);
$exp_month=($exp_month+$carry1)%12;
#year increment
$exp_year += $carry2;

$new_expiry = "$exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n"; #\n is important

#ACTION: Append new record
@slurp_userfile = (@slurp_userfile,"$post_login\n"); #add login
@slurp_userfile = (@slurp_userfile,"0 0 0 0 0 0\n"); #add next allowed login time
@slurp_userfile = (@slurp_userfile,"$post_passwd1\n"); #add password
@slurp_userfile = (@slurp_userfile,"0\n"); #add unsuccessful login attempts
@slurp_userfile = (@slurp_userfile,$new_expiry); #add account expiry time
@slurp_userfile = (@slurp_userfile,"$post_tipcont\n"); #add tip cont
@slurp_userfile = (@slurp_userfile,"0\n"); #add ultima clasa obtinuta

#ACTION: hard-rewrite userfile
truncate(userFILE,0);			#
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
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.1\n!; #version print for easy upload check
print qq!<h1 align="center">Inregistrare reusita.</h1>\n!;
print "<br>\n";

print "<center>Acum puteti sa va autentificati cu noile date.</center>\n";
print qq!<center>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_authent.cgi" method="get">\n!;
print qq!<input type="hidden" name="login"  value="$post_login">!;
print qq!<input type="hidden" name="passwd" value="$post_passwd1">!;
print qq!<center><INPUT type="submit"  value="OK"> </center>!;
print qq!</form>\n!; 
print qq!</center>\n!;
print "</body>\n</html>\n";

} #.END BLOCK (OK)

#-------------------------------------
sub compute_mac {

use Digest::MD5;
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
    Digest::MD5::md5_base64($secret, Digest::MD5::md5($secret, $message));
} #end of compute_mac


#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year
#out 1-expired 0-still valid
sub timestamp_expired
{
my($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year)=@_;

my @utc_time=gmtime(time);
my $act_sec=$utc_time[0];
my $act_min=$utc_time[1];
my $act_hour=$utc_time[2];
my $act_day=$utc_time[3];
my $act_month=$utc_time[4];
my $act_year=$utc_time[5];
#my $debug="$x_year\? $act_year \| $x_month\?$act_month";
#dienice("ERR04",0,\$debug);
if($x_year > $act_year) {return(0);}  #valid until year increment
 elsif($x_year == $act_year){ 
 if($x_month > $act_month) {return(0);}  #valid
 elsif($x_month == $act_month){ 
 if($x_day > $act_day) {return(0);}  #it's alive one more day
 elsif($x_day == $act_day){
 if($x_hour > $act_hour) {return(0);}  #it's alive one more hour
 elsif($x_hour == $act_hour){ 
 if($x_min > $act_min) {return(0);}  #it's alive one more min
 elsif($x_min == $act_min){ 
 if($x_sec > $act_sec) {return(0);}  #it's alive one more sec
  
 } #.end elsif min
 } #.end elsif hour
 } #.end elsif day
 } #.end elsif month
 } #.end elsif year
return(1);  #here is the general else
 

}
#--------------------------------------
# treat the "or die" and all error cases
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
              "ERR01" => "primire de  date corupte, inregistrata in log.",
              "ERR02" => "pagina pe care ai trimis-o a expirat",
              "ERR03" => "ai mai evaluat aceasta pagina, se poate o singura data",
              "ERR04" => "primire de  date corupte, inregistrata in log.",
              "ERR05" => "primire de  date corupte, inregistrata in log.",
              "ERR06" => "server congestionat, incercati mai tarziu",
              "ERR07" => "server congestionat, incercati mai tarziu",
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
              "ERR01" => "transaction id has been tampered with, md5 mismatch",    #test ok
              "ERR02" => "timestamp was already expired",           #test ok
              "ERR03" => "good transaction but already used",             #test ok
              "ERR04" => "undef transaction id",
              "ERR05" => "unstructured transaction id",
              "ERR06" => "cannot open a file",
              "ERR07" => "cannot close a file",
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
#CUSTOM
#CUSTOM
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: sim_register.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
}

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl(); #this must exist
print qq!v 3.2.1\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
#print qq!<center>In situatiile de congestie, incercati din nou in cateva momente.<br> In situatia in care erorile persista va rugam sa ne contactati pe e-mail, pentru explicatii.</center>\n!;
print qq!</body>\n</html>\n!;

exit();

} #end sub

#-------------------------------------
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

