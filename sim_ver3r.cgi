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

#  sim_ver3r.cgi v 3.2.2
#  Status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.2 implemented silent discard Status 204
# ch 3.2.1 deploy latest dienice() and possibly fix git://Sim_exam_yo/issues/4
# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3
# ch 3.0.d ANRCTI replaced by ANCOM
# ch 3.0.c text change - nu ai intrunit baremul la toate capitolele
# ch 3.0.b better fixing reportig of troubles with &specials; and "overline" quotes - only (incorect) branch now, (propun) branch still buggy
# ch 3.0.a modify window button to method="link" button
# ch 3.0.9 fixing tickets with <sub> <sup> <span> in trouble reporting; &radic; &Omega; and other spec char still corrupted. "overline" quotes still corrupted
# ch 3.0.8 introduced @slash@ permitting / in training usernames 
# ch 3.0.7 hamxam/ eliminated
# ch 3.0.6 bug kill: $v3code tried to be evaluated when undef 
# ch 3.0.5 <img> displayed with new method, more checks done
# ch 3.0.4 $buffertext debugged
# ch 3.0.3 schimbat regular expression pt v3code
# ch 3.0.2 recunoaste codurile unde sunt, si stocheaza evaluarile
# ch 3.0.1 citeste din hlr, slurp, baga in hash, baga in slurp si rescrie noul hlr
# ch 3.0.0 try to write test results into hlr file - in prima faza 
#	   doar print valorile cu rosu in outputul html
# ch 2.0.6 fixed trouble ticket 26
# ch 2.0.5 feature request nr 3 implemented
# ch 2.0.4 feature added without request: eXAM login is transmitted to troubleticket.cgi for internal ticket
# ch 2.0.3 workaround solution for troubleticket 15
# ch 2.0.2 adding the answers to autocompletion
# ch 2.0.1 introduce auto-completion of form for trouble-ticketing
# ch 2.0.0 coding Feature Request = tt12

use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

#-hash table for response retrieving
my %answer=();		#hash used for depositing the answers
my %hlrline=();		#hash used for rewriting test results in hlr

my $get_trid;                   #transaction ID from GET data

my $trid_login;       		#login extracted from transaction file
my $trid_pagecode;		#pagecode extracted from transaction file 
my $user_tipcont;		#user's account type: training/exam I-IIIRextracted from sim_users database
my $user_lastresult;            #user's last achievement: 0/1-4/5

my $user_account;		#user account number(an index), can be localised

my @tridfile;					          #slurped transaction file
my $trid;						            #the Transaction-ID of the generated page
my @utc_time=gmtime(time);     	#the 'present' time, generated only once
my @slurp_userfile;            	#RAM-userfile
my @slurp_hlrfile;		#RAM-hlr userfile
my @splitter;
#my $debugline;	#debug
my $v3code;			#v3 code of the question
my $trid_login_hlrname;

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
  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case 
  if($ENV{'REQUEST_METHOD'} eq "GET") 
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

unless($name eq 'transaction')
{
$value =~ tr/0/a/;
$value =~ tr/1/b/;
$value =~ tr/2/c/;
$value =~ tr/3/d/;
$value=~ s/<*>*<*>//g;
}

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


$get_trid= $answer{'transaction'}; #if exists, extract GET_trid from GET data
#md MAC has + = %2B and / = %2F characters, must be reconverted

if(defined($get_trid)) {
			$get_trid =~ s/%2B/\+/g;
			$get_trid =~ s/%2F/\//g;
                         }
else {dienice ("ERR20",0,\"undef trid"); } # no transaction or with void value - silent discard


#ACTION: open transaction ID file
open(transactionFILE,"+< sim_transaction") or dienice("ERR06",1,\"can't open transaction file");		#open transaction file for writing
#flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

my $expired=0;  #flag which checks if posted transaction has expired. Set to 'not expired'

#BLOCK: Refresh transaction file - remains unchanged in sim_ver3r.cgi
{
my @livelist=();
my @linesplit;

# transaction pattern in file: 
# B000C1_59_49_10_14_2_116_Ljxx+XY1v+S2QR0GHT/3ng owene 4 59 49 10 14 2 116 0 6 7 11 22 52 69 92 119 128 134 150 155 160 194 215 223 228 239 277 1 3 5 9 17 34 39 45 47 50 24 25 27 39 43 47 57 66 8 31 33 43 53 65 66 74 82 86 87 89 95 104 105 109 112 121 126 127 135 138 139 142 147 K 

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   chomp $linesplit[8]; #\n is deleted

if ($linesplit[2] =~ /[4-7]/) {@livelist=(@livelist, $i);} #if this is an exam transaction, do not refresh it even it's expired, is the job of sim_authent.cgi

# next 'if' is changed into 'elsif'
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8])) {} #if timestamp expired do nothing = transaction will not refresh
else {@livelist=(@livelist, $i);} #not expired, refresh it

 
  } #.end for


my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

} #.end unless

} #.END BLOCK

#BLOCK: extract data from actual transaction and do not delete it
{
my @livelist=();
my @linesplit;

#my $expired=1;  #flag which checks if transaction has expired
  my $branch=1; #verifies if branch was taken
unless(($#tridfile == 0) || ($expired)) 		#unless transaction list is empty (but transaction exists on first line) or posted transaction has expired
{  

  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $get_trid) {
									$trid_login=$linesplit[1]; #extract data
									$trid_pagecode=$linesplit[2]; #extract data
									$branch=0;
									}
   @livelist=(@livelist, $i); #all  transactions remain, including actual(elim. else)
  } #.end for

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
 


} #.end unless
if($branch) {$expired=1;} #the case of unknown transaction id
#$expired=1;

if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or dienice("ERR07",1,\"cant close transaction file");


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


@pairs=split(/_/,$get_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ERR05",1,\$get_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("ERR01",1,\$get_trid);}

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])) { 
                                             dienice("ERR02",0,\"null"); }

#else is really case 2
else { dienice("ERR03",1,\$get_trid);  }

} #end of local block
				} #.end expired

} #.END extraction BLOCK
#we have here the "logins" and the pagecode of the guy

#ACTION: extract account type and last achievement of user from user database
#open user account file
open(userFILE,"< sim_users") or dienice("ERR06",1,\"can't open user file");	#open user file for writing
#flock(userFILE,2);		#LOCK_EX the file from other CGI instances
seek(userFILE,0,0);		#go to the beginning
@slurp_userfile = <userFILE>;		#slurp file into array

#BLOCK: search user record
{
#search record
unless($#slurp_userfile < 0) 		#unless  userlist is empty
{#.begin unless

  for(my $account=0; $account < (($#slurp_userfile+1)/7); $account++)	#check userlist, account by account
  {
if($slurp_userfile[$account*7+0] eq "$trid_login\n") #this is the user record we are interested
{
#begin interested
 $user_tipcont=$slurp_userfile[$account*7+5];
 chomp $user_tipcont;
  $user_lastresult=$slurp_userfile[$account*7+6];
 chomp $user_lastresult;

 $user_account=$account;
 $account = ($#slurp_userfile+1)/7; #sfarsitul fortat al ciclului for
} #.end interested
  } #.end for

  } #.end unless empty userlist 

} #.END BLOCK: search user record

#close user file; will reopen it if needed
close(userFILE) or dienice("ERR07",1,\"can't close user database"); 

#ACTION: check request clearances pagecode == 7 and tip cont == 0/4&&notused)
unless($trid_pagecode == 7 && ($user_tipcont == 0 || $user_tipcont == 4 && $user_lastresult == 0)) #CUSTOM: invoked from examIIIR page
{
#ACTION: close all resources
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close (transactionFILE) or dienice("ERR07",1,\"cant close transaction file");

#ACTION: append cheat symptoms in cheat file
#CUSTOM
my $cheatmsg="$trid_login (study level: $user_tipcont) from pagecode $trid_pagecode invoked evaluation of exam III-R";
dienice("ERR08",3,\$cheatmsg);
}

#All clearances ok, prep to evaluate results

#CUSTOM 
my @database=("db_ntsm","db_op3r","db_legis3r");       #set the name of used databases and their order
my @qcount=(10,8,20); #number of questions generated on each chapter
my @mincount=(7,6,15); #minimum number of good answers per chapter
my @chapter=("Norme Tehnice pentru Securitatea Muncii","Proceduri de Operare","Reglementari Interne si Internationale"); #chapter names
my $masked_index=0;   #index of the question in <form>; init with 0 if appropriate
my $f_failed=0;         #flag, start assuming that exam is taken
my @linesplit;
my $correct;					#stores the number of correct results in a chapter

my $temp;
my $item;
my $fline;
my @livelist=();

#print the evaluated exam header
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.2\n!; #version print for easy upload check
print qq!<br>\n!;
#CUSTOM
print qq!<h2 align="center">Rezultate Examen clasa III-R</h2>\n!;
#print qq!<h2 align="center">evaluare</font></h2>\n!;
print qq!<h4 align="center">rezultatul final se afla in partea de jos a a paginii.</h4>\n!;
#===================V3============
$trid_login_hlrname = $trid_login;
$trid_login_hlrname =~ s/\//\@slash\@/; #substitute /
if(-e "hlr/$trid_login_hlrname"){ #doar userii de antrenament  au hlrfile, one-shooters nu.

open(HLRfile,"+< hlr/$trid_login_hlrname") or dienice("ERR07",1,\"cant open hlr file"); #open
#flock(HLRfile,2); #flock exclusive
seek(HLRfile,0,0);		# rewind
@slurp_hlrfile = <HLRfile>;	# slurp into a @variable
			 } #.end if(-e)
#===========.V3===

#find our exam - transaction
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {

   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $get_trid) 
   { #our transaction, which exists and is ok
     #will be eliminated by evaluation, doesn't enter in livelist
   
#foreach database
for (my $iter=0; $iter< ($#database+1); $iter++)   #generate sets of questions from each database
{#foreach database
#===================V3============
%hlrline=(); #empty the hash, also for non-hlr users, just it wont be used finally

 if(-e "hlr/$trid_login_hlrname"){
my $tempvar=$slurp_hlrfile[$iter+1];
chomp $tempvar;
@splitter= split(/,/,$tempvar);
for (my $split_iter=0; $split_iter<($#splitter/2);$split_iter++)
 {
%hlrline = (%hlrline,$splitter[$split_iter*2],$splitter[$split_iter*2+1]); #daca linia e stocata direct sub forma de string de hash; 
  } #.end for split iter

 			 }
#===========.V3===
# open database

	open(INFILE,"< $database[$iter]");
          #flock(INFILE,1);		#LOCK_SH the file from other CGI instances
#------------------------

#print chapter name
print qq!<font color="white"><big>$chapter[$iter]</big></font><br>\n!;

#>>>>>>>>>>>>>>>>>
#BLOCK: Evaluare rezultate intr-un capitol
$correct=0; #init correct answers counter

seek(INFILE,0,0);	#rewind question database
$fline = <INFILE>;	#jump over first line=version string
$fline = <INFILE>;	#jump over first line=number of questions in database


for(my $m=1;$m<($qcount[$iter]+1);$m++) #all questions in a chapter 
  {
  my $right_answer; #this is used only for feedback printing
  $masked_index++; #masked index of the current question 
  #linesplit[$masked_index+8] is the index in the database

chomp ($linesplit[$masked_index+8]); #be sure that it's an integer
$item="##$linesplit[$masked_index+8]#"; 

#se cauta intrebarea in baza de date pana se gaseste  
do {
$fline = <INFILE>;
chomp($fline);
} #.end do-while
while (!($fline =~ /$item/));
##s-a gasit intrebarea
$fline = <INFILE>;				#this is the correct answer
chomp($fline);
$right_answer=$fline; #used only for feedback printing

$temp= sprintf("question%s",$masked_index); #question name from hash

#print qq!<font color="blue">raspuns: $answer{$temp}</font> !; #debug only

print qq!<form action="#">\n!;
print qq!<dl>\n!;
if(defined $answer{$temp} && ($fline eq $answer{$temp})) 
{#good sollution feedback

$correct++;

my $buffertext;
$fline = <INFILE>;				#se citeste intrebarea
chomp($fline);
#
#============V3===
#cauti codul tip v.3 al problemei la inceputul enuntului(continut acum de $fline)
if($fline =~ /^\d+\w{1}[0-9]{2,}[a-z]?~&/) #daca linia incepe cu v3-code 
   { 
@splitter = split(/~&/,$fline);
$v3code=$splitter[0];
$fline=$splitter[1];		#se ascunde codul v3
$buffertext=$splitter[1];	#buffertext e fara v3-code
#chiar daca userul nu are hlrfile, se baga in hash, el oricum nu se va 
#rescrie decat pentru userii cu hlr-file 
%hlrline = (%hlrline,$v3code,'y'); #sper ca face si overwrite
			
    }
else {
$v3code="null"; #initializam cu ceva, totusi
$buffertext=$fline;}  #va fi folosit pentru auto-complete
#===========.V3===

print qq!<dt><b><font color="blue">$m)</font> $fline</b><br><font color="blue" size="-2">Raspuns corect</font><br>\n!;


#Daca exista, se insereaza imaginea cu WIDTH
$fline = <INFILE>;				#se citeste figura
chomp($fline);
#new method for <img>
 if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/) {      
				my @pic_split;
                       @pic_split=split(/ /,$fline);
                   if(defined($pic_split[1])) {
print qq!<br><center><img src="http://localhost/shelf/$pic_split[0]", width="$pic_split[1]"></center><br>\n!;
                                              }
						    }
#afisare intrebari a)-d) in ordine din database
$fline = <INFILE>;				#se citeste raspunsul a
chomp($fline);
$buffertext="$buffertext a) $fline";
if( $answer{$temp} eq "a") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;}
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}
       
$fline = <INFILE>;				#se citeste raspunsul b
chomp($fline);
$buffertext="$buffertext b) $fline";
if( $answer{$temp} eq "b") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;}
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

$fline = <INFILE>;				#se citeste raspunsul c
chomp($fline);
$buffertext="$buffertext c) $fline";
if( $answer{$temp} eq "c") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;}
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

$fline = <INFILE>;				#se citeste raspunsul d
chomp($fline);
$buffertext="$buffertext d) $fline";

####cleanse string 
# space replaced to + automatically
# = replaced to char automatically
# + replaced autom to char because there are + in the text
# & and " replaced because they are component of special chars and <span

$buffertext =~ s/"/%22/g;
$buffertext =~ s/&/%26/g;


if( $answer{$temp} eq "d") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;}
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

$fline=<INFILE>; #contributor problema
 chomp($fline);
print qq!<font size="-1"><i>(Contributor: $fline)</i></font><br>\n!; 
print qq!</dl>\n</form>\n!;

#in caz ca nu exista rezolvare, bagat invitatie pentru a propune o rezolvare
#use embedded fault reporting system         

$fline=<INFILE>; #skip null/picture, omul a rezolvat-o, excludem poza rezolvarii
$fline=<INFILE>; #read to see if solution exists
if($fline eq "\n"){

## butonul de complaining ##
print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi" method="post">\n!;
print qq!<input type="hidden" name="type" value="1">\n!;
print qq!<input type="hidden" name="nick" value="$trid_login">\n!;
print qq!<input type="hidden" name="subtxt" value=\"(propun) $buffertext\">\n!;

print qq!<font color="black" size="-2">Puteti propune rezolvarea acestei intrebari pentru a-i ajuta si pe altii, apasand </font> !;
print qq!<input type="submit" value="aici">\n!;

print qq!</form>\n!;


                 }
}#.end good solution feedback
else { #wrong solution feedback

my $buffertext;
$fline = <INFILE>;				#se citeste intrebarea
chomp($fline);
$buffertext=$fline;
#============V3===
#cauti codul tip v.3 al problemei la inceputul enuntului(continut acum de $fline)
if($fline =~ /^\d+\w{1}[0-9]{2,}[a-z]?~&/) #if v3-code at he beginning
  {
@splitter = split(/~&/,$fline);
$v3code=$splitter[0];
$fline=$splitter[1];
$buffertext=$fline; #in cazul cu v3code, buffertext il pierde
  }
else {
 $v3code="null"; #initializam totusi cu ceva, sa nu ramana undefined
 $buffertext=$fline; } #cazul fara v3code

#print qq!<font color="red">codul v3 se gaseste la inceputul:<br>$fline</font><br>\n!; #debug
#===========.V3===

print qq!<dt><b><font color="red">$m)</font> $fline</b><br><font color="red" size="-2">Raspuns gresit</font><br>\n!;
#Daca exista, se insereaza imaginea cu WIDTH
$fline = <INFILE>;				#se citeste figura
chomp($fline);
#new method for <img>
 if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/) {      
				my @pic_split;
                       @pic_split=split(/ /,$fline);
                   if(defined($pic_split[1])) {
print qq!<br><center><img src="http://localhost/shelf/$pic_split[0]", width="$pic_split[1]"></center><br>\n!;
                                              }
						    }
#afisare intrebari a)-d) in ordine din database
$fline = <INFILE>;				#se citeste raspunsul a
chomp($fline);
$buffertext="$buffertext a) $fline";
if( defined $answer{$temp} && $answer{$temp} eq "a") {print qq!<dd><img src="http://localhost/shelf/answer_bad.gif" align="middle" alt="[x]">$fline<br>\n!;} 
elsif(defined $answer{$temp} && $right_answer eq "a") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;} 
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}
#print qq!$fline<br>\n!;
       
$fline = <INFILE>;				#se citeste raspunsul b
chomp($fline);
$buffertext="$buffertext b) $fline";
if( defined $answer{$temp} && $answer{$temp} eq "b") {print qq!<dd><img src="http://localhost/shelf/answer_bad.gif" align="middle" alt="[x]">$fline<br>\n!;}
elsif(defined $answer{$temp} && $right_answer eq "b") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;} 
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

$fline = <INFILE>;				#se citeste raspunsul c
chomp($fline);
$buffertext="$buffertext c) $fline";
if(defined $answer{$temp} &&  $answer{$temp} eq "c") {print qq!<dd><img src="http://localhost/shelf/answer_bad.gif" align="middle" alt="[x]">$fline<br>\n!;}
elsif(defined $answer{$temp} && $right_answer eq "c") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;} 
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

$fline = <INFILE>;				#se citeste raspunsul d
chomp($fline);
$buffertext="$buffertext d) $fline";
if(defined $answer{$temp} &&  $answer{$temp} eq "d") {print qq!<dd><img src="http://localhost/shelf/answer_bad.gif" align="middle" alt="[x]">$fline<br>\n!;}
elsif(defined $answer{$temp} && $right_answer eq "d") {print qq!<dd><img src="http://localhost/shelf/answer_good.gif" align="middle" alt="[v]">$fline<br>\n!;} 
else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline<br>\n!;}

###cleanse string
# space replaced to + automatically
# = replaced to char automatically
# + replaced autom to char because there are + in the text
# & and " replaced because they are component of special chars and <span

$buffertext =~ s/"/%22/g;
$buffertext =~ s/&/%26/g;

$fline=<INFILE>; #contributor problema
 chomp($fline);
print qq!<font size="-1" ><i>(Contributor: $fline)</i></font><br>\n!; 
print qq!</dl>\n</form>\n!;

#inserat rezolvarea corecta
#0. Daca userul nu a incercat, nici noi nu-i oferim nimic
if(defined $answer{$temp}) #adica daca a incercat
{
#============V3===
## adaugam problema, daca are v3-code, in HLR, cu 'n'

if($v3code =~ /\d+\w{1}[0-9]{2,}[a-z]?/)  #v3-code e valid sau "null"(init value) 
      {
%hlrline = (%hlrline,$v3code,'n'); #sper ca face si overwrite
			}			
#===========.V3===

#1. Daca exista, se insereaza imaginea cu WIDTH
$fline = <INFILE>;				#se citeste figura
chomp($fline);
#new method for <img>
 if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/) {      
				my @pic_split;
                       @pic_split=split(/ /,$fline);
                   if(defined($pic_split[1])) {
print qq!<br><center><img src="http://localhost/shelf/$pic_split[0]", width="$pic_split[1]"></center><br>\n!;
                                              }
						    }


#2. inserat textul rezolvarii;
$fline = <INFILE>;				#se citeste raspunsul d
unless ($fline eq "\n") {#if a solution exists
print qq!<font color="white">$fline</font><br>!;

#3. inserat contributorul rezolvarii
$fline=<INFILE>; #contributor
chomp($fline);

print qq!<font size="-1" color="yellow"><i>(Rezolvare: $fline)</i></font><br>\n!; 

                      }#.end if solution exists

#print qq!wrong =$masked_index=!;               #print the relative index 1) .. 20) of wrong answer
#  	   print qq!) \n!;

## butonul de complaining ##
#print qq!<font color="red">POST: $buffertext</font><br>!; #debug
print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi" method="post">\n!;
print qq!<input type="hidden" name="type" value="1">\n!;
print qq!<input type="hidden" name="nick" value="$trid_login">\n!;
print qq!<input type="hidden" name="subtxt" value=\"(incorect) $buffertext\">\n!;

#print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi?type=1&nick=$trid_login&subtxt=(incorect)$buffertext" method="get">\n!;
print qq!<font color="black" size="-2">In cazul in care considerati ca ceva este incorect - raspunsul,rezolvarea, sau enuntul problemei este gresit, poti sa ne notifici </font> !;
print qq!<input type="submit" value="aici">\n!;

#### Link special de transmis la troubleticket(deprecated)
#print qq!<a href="http://localhost/cgi-bin/troubleticket.cgi?type=1&nick=$trid_login&subtxt=(incorect)$buffertext" target="kpage">\n!;
#print qq!<b>aici</b><br>\n!;
#print qq!</a>!;

print qq!</form>\n!;

}  #.end show solution 
}  #.end wrong solution
#print qq!</dl>\n!;  


  }#.end for $m, all questions in a chapter were seen

#inchidere baza de date cu intrebari
close(INFILE);
#============V3===
# daca exista hlrfile
if(-e "hlr/$trid_login_hlrname") {
$slurp_hlrfile[$iter+1]=""; #make it empty

#hash il scrii  in @slurp_hlrfile;
for my $key ( keys %hlrline ) {
        #my $value = $hash{$key};
#sau cu defined? "" e defined dpmdv
if($slurp_hlrfile[$iter+1] eq "") {$slurp_hlrfile[$iter+1]="$key,$hlrline{$key}";} #sa nu inceapa cu virgula
    else {$slurp_hlrfile[$iter+1]="$slurp_hlrfile[$iter+1],$key,$hlrline{$key}";} 
    			 
			       } #.end for $key

#even it is empty, finish with newline
$slurp_hlrfile[$iter+1]="$slurp_hlrfile[$iter+1]\n";

#print qq!<font color="red">linia rescrisa in slurp: $slurp_hlrfile[$iter+1].</font><br>\n!; #debug
			  } #.end (-e)
#===========.V3===

#evaluare pe capitol a nr de raspunsuri corecte
#tbd

print qq!<table width="99%" bgcolor="lightblue" border="2"><tr><td>!;
print qq!<font color="black">La acest capitol ai realizat $correct raspunsuri corecte din $qcount[$iter] intrebari, necesarul minim este de $mincount[$iter] raspunsuri corecte.</font>\n!; 
print qq!</td></tr></table>\n<br>\n!;
#chapter result is good enough?
if($correct < $mincount[$iter]) {$f_failed=1;} #there are less than mimum number of correct answers

#print qq!failed=$f_failed<br>\n!; #debug info

}#.end foreach database
#============V3===
# daca exista hlrfile
if(-e "hlr/$trid_login_hlrname") {

#@slurp_hlrfile se scrie in fisierul /hlr(rewind truncate,,write, close)
truncate(HLRfile,0);
seek(HLRfile,0,0);
for(my $i=0;$i <= $#slurp_hlrfile;$i++)
{
printf HLRfile "%s",$slurp_hlrfile[$i];#we have \n at the end of each element
}
close(HLRfile);
			 }
#===========.V3===

#just print the final result if the exam is taken or not
print qq!<table width="99%" bgcolor="lightblue" border="2"><tr><td>!;
print qq!<font color="black">\n<u>Rezultat final:</u><br>\n!;
if ($f_failed) { #exam is failed
    print qq!<b>Nu ai trecut examenul.</b><br>\n Nu ai intrunit baremul la toate capitolele.<br>\n!;
               }
else {
    print qq!<b>Ai trecut examenul.</b><br>\n Ai facut un scor bun la toate capitolele.<br>\n!;
     }
print qq!</font></td></tr></table>\n<br>\n!;

}#.end activities done with our exam trensaction

#daca tranzactia nu e a noastra, ramane live 
else {
   @livelist=(@livelist, $i); #all  transactions remain, including actual
     } 
     
} #.end for

#print the evaluated exam trailer
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;

#------------------------
#finishing block
{ #start block

#rewrite and close transaction file
my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
  
#write in the file;
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or dienice("ERR07",1,\"cant close transaction file");

#update user record with the result of test
if ($f_failed)
{unless($user_tipcont == 0) {$slurp_userfile[$user_account*7+6]="5\n";}}
else 
{ $slurp_userfile[$user_account*7+6]="4\n";} #custom

#open userfile for write
open(userFILE,"+< sim_users") or dienice("ERR06",1,\"can't open user file");	#open user file for writing
#flock(userFILE,2);		#LOCK_EX the file from other CGI instances

#rewrite userfile
truncate(userFILE,0);			#
seek(userFILE,0,0);				#go to beginning of transactionfile
for(my $i=0;$i <= $#slurp_userfile;$i++)
{
printf userFILE "%s",$slurp_userfile[$i]; #we have \n at the end of each element
}
#close userfile
close(userFILE) or dienice("ERR07",1,\"can't close user database"); 


}#end finishing block
#===========================END END END==============================
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
              "ERR06" => "server congestionat, incearca in cateva momente",
              "ERR07" => "server congestion",
              "ERR08" => "tentativa de frauda, inregistrata in log",
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
              "ERR20" => "silent discard, not displayed"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "transaction id has been tampered with, md5 mismatch",    #test ok
              "ERR02" => "timestamp was already expired",           #test ok
              "ERR03" => "good transaction but already used",             #test ok
              "ERR04" => "undef transaction id",
              "ERR05" => "unstructured transaction id",
              "ERR06" => "cannot open file",
              "ERR07" => "cannot close file",
              "ERR08" => "cheating attempt",
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
              "ERR20" => "silent discard, not logged"
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
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: sim_ver3r.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
}
if($error_code eq 'ERR20') #must be silently discarded with Status 204 which forces browser stay in same state
{
print qq!Status: 204 No Content\n\n!;
print qq!Content-type: text/html\n\n!;
}
else
{
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl(); #this must exist
print qq!v 3.2.2\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
#print qq!<center>In situatiile de congestie, incercati din nou in cateva momente.<br> In situatia in care erorile persista va rugam sa ne contactati pe e-mail, pentru explicatii.</center>\n!;
print qq!</body>\n</html>\n!;
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

