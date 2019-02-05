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

#  sim_ver4.cgi v 3.2.7
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.7 functions moved to ExamLib.pm
# ch 3.2.6 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.2.5 compute_mac() changed from MD5 to SHA1 and user password is saved as hash
# ch 3.2.4 changed config for the new Decizia db_legis4 and db_ntsm4
# ch 3.2.3 implemented use_time in recorded transaction_id; timestamp_expired() changed
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

use lib '.';
use My::ExamLib qw(ins_gpl timestamp_expired compute_mac dienice);

#-hash table for response retrieving
my %answer=();		#hash used for depositing the answers
my %hlrline=();		#hash used for rewriting test results in hlr

my $get_trid;                   #transaction ID from GET data; it never has an "used" timestamp

my $trid_id;                    #transaction ID extracted from transaction file
my $trid_login;       		#login extracted from transaction file
my $trid_pagecode;		#pagecode extracted from transaction file 
my $user_tipcont;		#user's account type: training/exam I-IIIRextracted from sim_users database
my $user_lastresult;            #user's last achievement: 0/1-4/5

my $user_account;		#user account number(an index), can be localised

my @tridfile;					          #slurped transaction file
my $trid;						            #the Transaction-ID of the generated page
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
#next 4 transforms are specific to sim_verX
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
open(transactionFILE,"+< sim_transaction") or dienice("verERR06",1,\"$! $^E $?");		#open transaction file for writing
flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

my $expired=0;  #flag which checks if posted transaction has expired. Set to 'not expired'

#BLOCK: Refresh transaction file to cancel expired transactions (ch 3.2.3 check OK)
{
my @livelist=();
my @linesplit;

# transaction pattern in file: 
#unused: B000C1_59_49_10_14_2_116_Ljxx+XY1v+S2QR0GHT/3ng owene 4 59 49 10 14 2 116 0 6 7 11 22 52 69 92 119 128 134 150 155 160 194 215 223 228 239 277 1 3 5 9 17 34 39 45 47 50 24 25 27 39 43 47 57 66 8 31 33 43 53 65 66 74 82 86 87 89 95 104 105 109 112 121 126 127 135 138 139 142 147 K 
#used:   B000C1_59_49_10_14_2_116_Ljxx+XY1v+S2QR0GHT/3ng_*_00_00_10_14_2_116 owene 4 59 49 10 14 2 116 0 6 7 11 22 52 69 92 119 128 134 150 155 160 194 215 223 228 239 277 1 3 5 9 17 34 39 45 47 50 24 25 27 39 43 47 57 66 8 31 33 43 53 65 66 74 82 86 87 89 95 104 105 109 112 121 126 127 135 138 139 142 147 K 

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]); #space is the splitter
   chomp $linesplit[8]; #\n is deleted $linesplit[8] is eventually the last portion if the transaction is a short one

if ($linesplit[2] =~ /[4-7]/) {@livelist=(@livelist, $i);} #if this is an exam transaction, do not refresh it even it's expired, is the job of sim_authent.cgi
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8])>0)  
                       { } # expired, do not keep it in livelist
  else { @livelist=(@livelist, $i); } # not expired, keep it

 
  } #.end for


my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

} #.end unless

} #.END BLOCK

#BLOCK: extract data from actual transaction but read-only
#ch 3.2.3 - modified
{
my @linesplit;

#my $expired=1;  #DEBUG  - flag which checks if transaction has expired 1=expired
  my $branch=1; #verifies if branch was taken
unless(($#tridfile == 0) || ($expired)) 		#unless transaction list is empty (but transaction exists on first line) or posted transaction has expired
{  

  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);

#ch 3.2.3 aici linesplit[0] poate sa aiba sau nu bucata de "used_timestamp" si atunci eq nu mai e eq
  if($linesplit[0] =~ /^\Q$get_trid\E/) { 
			$trid_login=$linesplit[1]; #extract login
			$trid_id   =$linesplit[0]; #extract transaction
			$trid_pagecode=$linesplit[2]; #extract pagecode
			$branch=0;
				  }
  } #.end for

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
close (transactionFILE) or dienice("verERR07",1,\"cant close transaction file");


#now we should check why received transaction was not found in sim_transaction file
#case 0: it's an illegal transaction if md5 check fails
#        must be recorded in cheat_file
#case 1: md5 correct but transaction timestamp expired, file was refreshed and wiped this transaction
#        must be announced to user
#case 2: md5 ok, timestamp ok, it must (ch 3.2.3) be some sort of weird error that must be logged
#        unexpired transactions that are used or not should be in sim_transaction

#check case 0
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ'
{ #local block start
my @pairs; #local
my $string_trid; # we compose the incoming transaction to recalculate mac
my $heximac;


@pairs=split(/_/,$get_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("verERR05",1,\$get_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("verERR01",1,\$get_trid);}

#check case 1

elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) 
                                 { 
                                  dienice("verERR02",0,\"null"); 
                                 }

#else is really case 2
else { dienice("verERR09",5,\$get_trid);  }

} #end of local block
} #.end expired

#if we arrive here, the get_trid exists in the tridfile
#we have $trid_id, $trid_login, $trid_pagecode
#if transaction was used more than 5s ago: "exam already used"
#if transaction was used less than 5s ago: return Status 204
#if transaction is unused - proceed further with evaluation
#use timestamp_expired() (returns seconds since evaluated time)
#===============.begin ch 3.2.3======================
my @pairs=split(/_/,$trid_id); #reusing @pairs variable for spliting results
if ($trid_id =~ m/\*/) { #if it has the used mark then $used_time >= 0 
  my $usedTime = timestamp_expired($pairs[9],$pairs[10],$pairs[11],$pairs[12],$pairs[13],$pairs[14]);
  if ($usedTime < 10) { #if request comes faster than 10s, might be some browser parallel request
                           dienice ("ERR20",0,\"null");  #silent discard, Status 204 No Content
                        }
   else { 
         #dienice ("verERR03",1,\$trid_id); #debug - symptom catch 
         dienice ("verERR03",0,\"null"); 
        }                          
                       }
#===============.end ch 3.2.3========================

} #.END extraction BLOCK
#we have here the "logins" and the pagecode of the guy

#ACTION: extract account type and last achievement of user from user database
#open user account file
open(userFILE,"< sim_users") or dienice("verERR06",1,\"$! $^E $?");	#open user file for writing
flock(userFILE,2);		#LOCK_EX the file from other CGI instances
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
close(userFILE) or dienice("verERR07",1,\"can't close user database"); 

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

close (transactionFILE) or dienice("verERR07",1,\"cant close transaction file");

#ACTION: append cheat symptoms in cheat file
#CUSTOM
my $cheatmsg="$trid_login (study level: $user_tipcont) from pagecode $trid_pagecode invoked evaluation of exam I";
dienice("verERR08",3,\$cheatmsg);
}

#All clearances ok, prep to evaluate results

#CUSTOM 
my @database=("db_ntsm4","db_op4","db_legis4");       #set the name of used databases and their order
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
print qq!v 3.2.7\n!; #version print for easy upload check
print qq!<br>\n!;
#CUSTOM
print qq!<h2 align="center">Rezultate Examen clasa a IV-a</h2>\n!;
#print qq!<h2 align="center">evaluare</font></h2>\n!;
print qq!<h4 align="center">rezultatul final se afla in <a href="#endof">partea de jos a a paginii</a>.</h4>\n!;
#===================V3============
$trid_login_hlrname = $trid_login;
$trid_login_hlrname =~ s/\//\@slash\@/; #substitute /
if(-e "hlr/$trid_login_hlrname"){ #doar userii de antrenament  au hlrfile, one-shooters nu.

open(HLRfile,"+< hlr/$trid_login_hlrname") or dienice("verERR07",1,\"cant open hlr file"); #open
flock(HLRfile,2); #flock exclusive
seek(HLRfile,0,0);		# rewind
@slurp_hlrfile = <HLRfile>;	# slurp into a @variable
			 } #.end if(-e)
#===========.V3===

#find our exam - transaction
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {

   @linesplit=split(/ /,$tridfile[$i]);
#ch 3.2.3
#   if($linesplit[0] eq $get_trid) #version before ch 3.2.3
   if($linesplit[0] =~ /^\Q$get_trid\E/)  
   { #our transaction, which exists and is ok
     #ch 3.2.3 will NOT be eliminated by evaluation, just marked as used ///doesn't enter in livelist
   
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
          flock(INFILE,1);		#LOCK_SH the file from other CGI instances
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
print qq!<font color="black" size="-2">In cazul in care considerati ca ceva este incorect - raspunsul,rezolvarea, sau enuntul problemei este gresit, poti sa ne notifici </font> !;
print qq!<input type="submit" value="aici">\n!;
print qq!</form>\n!;

}  #.end show solution 
}  #.end wrong solution


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
print qq!<a name="endof"></a>\n!;
print qq!<table width="99%" bgcolor="lightblue" border="2"><tr><td>!;
print qq!<font color="black">\n<u>Rezultat final:</u><br>\n!;
if ($f_failed) { #exam is failed
    print qq!<b>Nu ai trecut examenul.</b><br>\n Nu ai intrunit baremul la toate capitolele.<br>\n!;
               }
else {
    print qq!<b>Ai trecut examenul.</b><br>\n Ai facut un scor bun la toate capitolele.<br>\n!;
     }
print qq!</font></td></tr></table>\n<br>\n!;

#ch 3.2.3 - we must add to our transaction the "used" timestamp
#========ch 3.2.3========
my @linesplit;
@linesplit=split(/ /,$tridfile[$i]);
# print qq!$linesplit[0]<br>!; #debug

my $epochTime = time();
my ($act_sec, $act_min, $act_hour, $act_day,$act_month,$act_year) = (gmtime($epochTime))[0,1,2,3,4,5];


my $usedTimestamp = $linesplit[0].'_'.'*_'."$act_sec\_$act_min\_$act_hour\_$act_day\_$act_month\_$act_year"; #adds the used timestamp

#print qq!$usedTimestamp<br>!; #debug
$tridfile[$i] =~ s/\Q$linesplit[0]\E/$usedTimestamp/g;
#print qq!$tridfile[$i]!; #debug
#=========.ch 3.2.3==========
}#.end activities done with our exam transaction

#ch 3.2.3 - tranzactia e marcata ca used sau nu, ramane in tridfile
     
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
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or dienice("verERR07",1,\"cant close transaction file");

#update user record with the result of test
if ($f_failed)
{unless($user_tipcont == 0) {$slurp_userfile[$user_account*7+6]="5\n";}}
else 
{ $slurp_userfile[$user_account*7+6]="4\n";} #custom

#open userfile for write
open(userFILE,"+< sim_users") or dienice("verERR06",1,\"$! $^E $?");	#open user file for writing
flock(userFILE,2);		#LOCK_EX the file from other CGI instances

#rewrite userfile
truncate(userFILE,0);			#
seek(userFILE,0,0);				#go to beginning of transactionfile
for(my $i=0;$i <= $#slurp_userfile;$i++)
{
printf userFILE "%s",$slurp_userfile[$i]; #we have \n at the end of each element
}
#close userfile
close(userFILE) or dienice("verERR07",1,\"can't close user database"); 


}#end finishing block
#===========================END END END==============================


