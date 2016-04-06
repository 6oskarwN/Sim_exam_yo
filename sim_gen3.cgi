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

#  sim_gen3.cgi v 3.2.1
#  Status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.1 deploy latest dienice() and possibly fix git://Sim_exam_yo/issues/4
# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3
# ch 3.1.0 logging more error info in cheat_log
# ch 3.0.f html button window-based changed to <form method="link" action="http:///
# ch 3.0.e infostudy/exam/exam7_yo.html sourced to index.html
# ch 3.0.d allow filename with funky chars /- at beginning
# ch 3.0.c hamxam/ eliminated
# ch 3.0.b make it slim: all dienice made as call to sub dienice()
#          +dienice made with 2 explanation list for errorcodes, internal and for public 
# ch 3.0.a bugfixfix: no errorcode to write in cheat_log when congestion reported by dienice() 
#          + localtime written in cheat_log
# ch 3.0.9 rucksack method(pocket) pentru scrambling-ul a)-d)
# ch 3.0.8 algoritmul RND se schimba in "decreasing rucksack" - devel;
#          + rezolvata problema de blocarem la afisarea formularului cu date corupte 
#          + daca se detecteaza greseala la afisare, nu se mai genereaza transaction = protectie
# ch 3.0.7 la fallback se da purge doar la reject list,  se imbunatateste acoperirea ultimelor intrebari din programa.
# ch 3.0.6 schimbat modul de afisare al imaginii de intrebare
# ch 3.0.5 correction and debugs removed
# ch 3.0.4 conditia 5 testata ca slow-convergence
# ch 3.0.3 partially debugged
# ch 3.0.2 attempts to generate the new-style exam
# ch 3.0.1 creates hlr record as in 3.0.0 but overwrites the other classes, implementing selfdelete
# ch 3.0.0 creates /hlr file if user is type0 and has no /hlr record
# ch 2.0.2 fixed trouble ticket 26
# ch 2.0.1 implemented Feature Request 2
# ch 2.0.0 coding Feature Change trouble ticket 12

use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

my $get_trid;                   #transaction ID from GET data
my $trid_login;			#login extracted from transaction file
my $trid_login_hlrname;         #$trid_login with escape chars where needed
my $trid_pagecode;		#pagecode from transaction file

my $tipcont;			#tipcont extracted from user file
my $ultimaclasa;                #ultima clasa obtinuta: 0=init, 1/2/3/4=clase 5=failed

my @tridfile;		        #slurped transaction file
my $trid;	                #the Transaction-ID of the generated page
my $hexi;                       #the trid+timestamp_MD5
my @utc_time=gmtime(time);     	#the 'present' time, generated only once
my @slurp_userfile;            	#RAM-userfile

my $attempt_counter;	        #attempts in opening or closing files; 5 attempts allowed
my $server_ok;			#flag; 1-server free; 0-server congested

my $hlrclass="blabla123";	#clasa1,2,3,clasa4(=3r) defined by first line in hlrfile  
				#hlrclass init=7 is just not to have undefined

$server_ok=1;                   #we suppose at the beginning a free server


#BLOCK: Input:transaction ID
{
my $buffer=();
my @pairs;
my $pair;
my $stdin_name;
my $stdin_value;

read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST-technology

@pairs=split(/&/, $buffer); #POST-technology

#@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology normally not ok, permits browser multiple requests

foreach $pair(@pairs) {
($stdin_name,$stdin_value) = split(/=/,$pair); #se presupune cateodata gresit ca avem abele parti ale perechii

if(defined($stdin_value)){
#transformarea asta e pentru textele reflow, dar trateaza si + si / al token-ului
$stdin_value=~ s/\+/ /g;  #GET an POST send + but + is also character of transaction. Check for possible bug from this
$stdin_value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$stdin_value=~ s/<*>*<*>//g;
            }
if($stdin_name eq 'transaction') {if(defined($stdin_value)){$get_trid=$stdin_value;}
                                    else{$get_trid=undef;}

}

} #.end foreach
} #.end block
#.END BLOCK

#md MAC has + = %2B and / = %2F characters, must be reconverted - already done
if(!defined($get_trid)) {dienice ("ERR17",1,\"undef trid"); } # no transaction or with void value
#else {
#	$get_trid =~ s/%2B/\+/g;
#	$get_trid =~ s/%2F/\//g;
#      }
#        else {dienice ("ERR17",1,\"undef trid"); } # no transaction or with void value


#ACTION: open transaction ID file

open(transactionFILE,"+< sim_transaction") || dienice("ERR03",1,\"null");
#flock(transactionFILE,2);

#ACTION: refresh transaction file
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

#BLOCK: Refresh transaction file
{
my @livelist=();
my @linesplit;

# transaction pattern in file: 
#B000B1_14_6_18_13_2_116_OaexlS%2FtUwS%2BKKJMA3x1Gw owene 4 7 52 19 13 2 116 12 32 33 40 74 82 85 86 96 113 118 151 164 180 190 220 234 255 257 263 3 10 18 20 28 30 33 40 44 52 3 4 9 13 30 47 48 52 2 13 17 23 32 33 34 44 53 67 68 73 75 76 77 87 88 92 108 120 122 132 142 150 153 K 

#TIME-EXPIRY based refresh
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
#we have now the list of the live transactions


my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

} #.end unless

} #.END time-based refresh BLOCK


#BLOCK: extract data from actual transaction and then delete it
{
my @livelist=();
my @linesplit;
my $expired=1;  #flag which checks if transaction exists

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{  
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions.  
  {
   @linesplit=split(/ /,$tridfile[$i]);
   if($linesplit[0] eq $get_trid) {
					$expired=0; #found
					$trid_login=$linesplit[1];     #extract data
					$trid_pagecode=$linesplit[2];  #extract data
				  }
	else {
		@livelist=(@livelist, $i);
             }
  } #.end for

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
  
} #.end unless

if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close(transactionFILE) || dienice("ERR04",1,\"null");

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
unless(defined($pairs[7])) {dienice ("ERR18",1,\$get_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("ERR01",1,\$get_trid);}

#check case 1, timestamp
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])) { 
                                             dienice("ERR02",0,\"null"); }

#else is really case 2 so transaction already used
else { dienice("ERR15",1,\$get_trid);  }

} #end of local block

			} #.end expired

} #.END extraction BLOCK


#we have here the login and pagecode of the guy from transaction data.
#-----------------------------------------------------
#ACTION: open user account file

open(userFILE,"< sim_users") || dienice("ERR05",1,\"null");
#flock(userFILE,2);		#LOCK_EX the file from other CGI instances

seek(userFILE,0,0);		#go to the beginning
@slurp_userfile = <userFILE>;		#slurp file into array

#BLOCK: search user record, it always exists, because transaction is unexpired.
{
#search record
unless($#slurp_userfile < 0) 		#unless  userlist is empty
{ #.begin unless

  for(my $account=0; $account < (($#slurp_userfile+1)/7); $account++)	#check userlist, account by account
  {
if($slurp_userfile[$account*7+0] eq "$trid_login\n") #this is the user record we are interested
{
#begin interested
$tipcont=$slurp_userfile[$account*7+5];	#tipul contului
chomp $tipcont;
$ultimaclasa=$slurp_userfile[$account*7+6];	#last class
chomp $ultimaclasa;
#========V3==============================================
#here is written the code for v3 where /hlr file is created
# / must be replaced in filename
$trid_login_hlrname = $trid_login;
$trid_login_hlrname =~ s/\//\@slash\@/; #replace /

#first, if exists, we check the class of hlrfile
if(-e "hlr/$trid_login_hlrname")
 {
open(HLRread,"< hlr/$trid_login_hlrname") || dienice("ERR06",1,\"null"); #open for reading only
#flock(HLRread,1); #LOCK_SH
seek(HLRread,0,0);
$hlrclass = <HLRread>;
close(HLRread);
chomp ($hlrclass);
  }

unless((-e "hlr/$trid_login_hlrname") && ($hlrclass eq "clasa3" )) #if does not exist or exists for a different class #CUSTOM
{
if($tipcont == 0) #se genereaza doar pt cont de antrenament
  {
open(HLRfile,"> hlr/$trid_login_hlrname") || dienice("ERR07",1,\"null");

#flock(HLRfile,2); #LOCK_EX the file from other CGI instances
seek(HLRfile, 0, 0);
printf HLRfile "clasa3\n"; #se inscrie examenul de clasa3  #CUSTOM
printf HLRfile "\n\n\n\n"; #bagat linii pt 4 probe	#CUSTOM
close(HLRfile);
  }
}

#code for v3 ends
#=========================================================
} #.end interested
  } #.end for
  
 } #.end unless empty userlist 

} #.END BLOCK: search user record

#ACTION: data was extracted, close user database
close(userFILE) || dienice("ERR08",1,\"null");


#ACTION: check the trid_pagecode, so exam is invoked using valid page and it's corresponding transaction
unless($trid_pagecode == 2) #invoked from central panel
{
#ACTION: close all resources
truncate(transactionFILE,0);
seek(transactionFILE,0,0);		#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close(transactionFILE) || dienice("ERR09",1,\"null");

#ACTION: append cheat symptoms in cheat file
my $err_harvester="pagecode\: $trid_pagecode login\: $trid_login";
dienice("ERR10",1,\$err_harvester);
}

#ACTION: check the clearance level: (tipcont==TRAINING && clasa==any)||(tipcont==III && ultime_clasa_promovata==0)
unless($tipcont == 0 || $tipcont == 3 && $ultimaclasa == 0) #CUSTOM
{
#ACTION: close all resources
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close(transactionFILE) || dienice("ERR11",1,\"null");


#ACTION: append cheat symptoms in cheat file
my $err_harvester="\$trid_login\: $trid_login \$tipcont\: $tipcont";
dienice("ERR12",1,\$err_harvester);
}

##BLOCK: Generate new transaction: EXAM III and close transaction file
#{
#Action: generate new transaction
$trid=$tridfile[0];
chomp $trid;						#eliminate \n

$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF
#ACTION: generate a new transaction

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


#CHANGE THIS for customizing; $timeframe is the allocated time for exam, in minutes
#my $timeframe=59;		#59 minutes for an full-exam in HAM-eXAM
my $timeframe=120;		#120 minutes=2 hours for a class III-R full-exam


#increment expiry time

#minute increment
$carry1= int(($exp_min+$timeframe)/60);		#check if minutes overflow 
$exp_min=($exp_min+$timeframe)%60;			#increase minutes

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

#CUSTOM: pagecode=6 pentru exam cl III
my $entry = "$hexi $trid_login 6 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year";

#} #.END BLOCK

#BLOCK: generate the questions of the exam
#ar merge implementat cu 3 liste: lista fisierelor , lista cu nr de intrebari/fisier, lista capitolelor
#bagat intr-o bucla for sau foreach
#

{
#subroutine declaration
sub random_int($);

my $masked_index=0;   #index of the question in <form>; init with 0 if appropriate
#my $index; #seen index in the form
my $watchdog=0;
#CUSTOM for class III
#radiotehnica 16 protectia muncii 10, operare 8, legislatie 20 #CUSTOM
my @database=("db_tech3","db_ntsm","db_op3","db_legis3");       #CUSTOM name of used databases and their order
my @qcount=(16,10,8,20); #CUSTOM number of questions generated on each chapter
my @chapter=("Electronica si Radiotehnica","Norme Tehnice pentru Securitatea Muncii","Proceduri de Operare","Reglementari Interne si Internationale"); #CUSTOM chapter names

my $fline;	#line read from file
my $rndom;	#used to store random integers
my @pool;	#pool of chosen questions
my $truth;
#======V3 variables======

my @rucksack;	#we extract the questions from here
my $rindex;	#rucksack index
my %hlrline;    #hlr-hash for the corresponding line of hlr
my @splitter;	#cu el manipulam v3code din linia intrebarii
#contains list with files containing only v3-codes
my @strips=("strip_db_tech3","strip_db_ntsm","strip_db_op3","strip_db_legis3");#CUSTOM
my @slurp_strip;  #slurped content of such a file
my $fallback;	#flag for generating exam for training users, when db is exhausted
my $found;
my $v3code;	#temporary var so chomp() can be made
#========================

#tbd: print HTML exam header
#ACTION: Generate header of the exam
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.1\n!; #version print for easy upload check
#CUSTOM
print qq!<center><font size="+2">Examen clasa III</font></center>\n!;
#print qq!<center><font size="+1">17 raspunsuri corecte din 20 aduc promovarea</font></center><br>\n!;
print qq!<center><font size="+2">O singura varianta de raspuns corecta din 4 posibile.</font></center>\n!;
print qq!<center><font size="+1">Timpul alocat examenului este de 2 ore.</font></center><br>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_ver3.cgi" method="post">\n!; #CUSTOM

#==========================v3==
# if hlrfile (-e) usertype==0(antrenament) and hlr class='clasa1') openfile and skip first line
if($tipcont == 0) #aici ai hlr, s-a creat mai sus
{
open(HLRread,"<hlr/$trid_login_hlrname") || dienice("ERR13",1,\"null"); #open for reading only
#flock(HLRread,1); #LOCK_SH
seek(HLRread,0,0);

$hlrclass = <HLRread>;#il mai aveam dar trebuie sa scapam de linia asta
#chomp ($hlrclass);		
#print qq!DEBUG: opened hlr file<br>\n!; #debug only
#print qq!DEBUG: just read hlr-clasa=$hlrclass<br>\n!; #debug only

}
#================.V3===
#tbd: foreach database
for (my $iter=0; $iter< ($#database+1); $iter++)   #generate sets of questions from each database
{
#tbd: open database
open(INFILE,"< $database[$iter]") || dienice("ERR14",1,\"null");   
#flock(INFILE,1);		#LOCK_SH the file from other CGI instances


#unless($server_ok) #if server is congested, exit;
#{ exit();} 
#====== V3 ======
#for each database the hash is loaded
%hlrline=(); #init
# if hlrfile (-e) and  usertype==0(antrenament))
if($tipcont == 0) #desi hlr exista, ca nu ajungi aici fara sa fie creat
{
#fetch hlr line
$hlrclass = <HLRread>; #variable reused to fetch the corresponding line from HLR
chomp $hlrclass;

#print qq!DEBUG:in hlr avem:$hlrclass<br>\n!; #debug

#load the hash TBD
@splitter= split(/,/,$hlrclass);
for (my $split_iter=0; $split_iter<($#splitter/2);$split_iter++)
 {
 %hlrline = (%hlrline,$splitter[$split_iter*2],$splitter[$split_iter*2+1]); #daca linia e stocata direct sub forma de string de hash; 
  } #.end for split iter
#print qq!DEBUG: hash  line is: %hlrline<br>\n!; #debug only

} # .end if(-e, antrenament)

#open,load and close the appropriate stripfile
#stripfiles are used by all user types
#stripfiles REALLY needed.
open(stripFILE, "<$strips[$iter]") || dienice("ERR015",1,\"null");
#flock(stripFILE,1);
seek(stripFILE,0,0);
@slurp_strip=<stripFILE>;
#print qq!DEBUG:in acest strip avem:@slurp_strip<br>\n!; #debug
close(stripFILE);
#================.V3===

#------------------------
#tbd: print chapter name
print qq!<table width="99%" bgcolor="lightblue" border="2"><tr><td>!;
print qq!<font color="black"><big>$chapter[$iter]</big></font>\n!; 
print qq!</td></tr></table>\n<br>\n!;

#------------------------
seek(INFILE,0,0);			#goto begin of file
$fline = <INFILE>;			#read away dummy version string from first line
$fline = <INFILE>;			#read nr of questions
chomp($fline);				#cut <CR> from end
#init the rucksack(fill it in)
#print qq!db_counter: $fline<br>\n!; #debug 
@rucksack=(0..($fline-1)); 
#print qq!rucksack content: @rucksack<br>\n!; #debug 


@pool=();       #init pool of chosen questions
$fallback=0;    #for type0 users generate with all conditions(fallback=1 is exam-like conditions)
#conditia de while trebuie imbunatatita si   cu conditia V3 de iesire
while($#pool < (($qcount[$iter])-1))	#do until number of questions is reached; 
{
$rindex= random_int($#rucksack+1); #intoarce intre 0 .. $#rucksack 
#print qq!rindex = $rindex !; #debug
$rndom=$rucksack[$rindex];
#print qq!debug: question \#$rndom generated<br>\n!; #debug 
#trebuie eliminat elementul din rucksack
if($rindex == 0) {@rucksack = @rucksack[1..$#rucksack];}
elsif ($rindex == $#rucksack) {@rucksack = @rucksack[0..($rindex-1)];}
else {@rucksack=(@rucksack[0..($rindex-1)],@rucksack[($rindex+1)..$#rucksack]);}
#print qq!rucksack content: @rucksack<br>\n!; #debug 

$truth=1;
#===== V3 =====
#conditions applicable in all modes, both non-hlr or 'training'


#==cond 4
#cond 4:daca subcapitolul exista deja in lista, skip

#cond 4 folosita doar daca e fallback sau contul nu e de antrenament 
if(($fallback==1) || ($tipcont != 0)) 
 {
unless($truth==0) #implementam un elsif ca sa mai scutim processing power 
  {  
#cod capitol este partea a 2-a din : $slurp_strip[$rndom](daca are v3 code)
$v3code=$slurp_strip[$rndom];

unless($v3code =~ m/^$/) #are sens doar pentru intrebarile cu cod v3
 {
chomp($v3code); 
@splitter = split(/[A-Z]{1}/,$v3code); #aici crapa 
#chomp($splitter[1]);
#==Cod v3 Intrebarea: $slurp_strip[$_]
foreach my $elem (@pool) {
if (!($slurp_strip[$elem] =~ m/^$/)) #aici e undefined 
 {
	if($slurp_strip[$elem] =~ m/[A-Z]{1}$splitter[1]/)  #la linia asta mai da o  eroare barosana
	{
 	$truth=0;
#print qq!COND4: \#$rndom cu cod v3=$v3code e chapter cu $slurp_strip[$elem], are acelasi cod $splitter[1]<br>\n!; #debug 
	}
 } #if not ^$
} #end foreach
} #.if defined
		} #.unless truth de la cond.  4
}#.end conditia4

#conditiile 3,5 functionale doar pentru training users
if(($tipcont == 0) && ($fallback == 0)) #applicable only for usertype=0 when no fallback is ordered
{

#cond 3:daca intrebarea exista in hlr cu y, skip.
unless($truth==0){  #implementam un elsif ca sa mai scutim processing power 
#Intrebarea: $slurp_strip[$rndom]
#print qq!COND 3: daca nu vezi variabila, o sa vezi in error_log: $slurp_strip[$rndom]<br>\n!; #debug 
unless($slurp_strip[$rndom] =~ m/^$/) #conditia are sens doar pentru intrebarile cu cod v3
 {
my $stripper=$slurp_strip[$rndom]; chomp $stripper;
#print qq!pentru \#$rndom cod v3 e \;$slurp_strip[$rndom]\; cu $hlrline{$stripper}<br>\n!; #debug 
if(defined($hlrline{$stripper})) #nu stii daca exista cheia!!!
      {
if($hlrline{$stripper} eq 'y') 
 {
 $truth=0;
#print qq!COND 3: \#$rndom e cu y in hlr, $slurp_strip[$rndom]; <br>\n!; #debug 
 }
      }#.if defined
  }#.if defined

		} #.unless de la cond.  3


#==cond. 5:daca exista in hlr intrebari din acelasi subcapitol,TOATE cu y, skip
unless($truth==0)  #implementam un elsif ca sa mai scutim processing power 
{
#if(defined($slurp_strip[$rndom])) #conditia are sens doar pentru intrebarile cu cod v3
unless($slurp_strip[$rndom] =~ m/^$/) #conditia are sens doar pentru intrebarile cu cod v3

 {
chomp $slurp_strip[$rndom];
#==cod capitol este partea a 2-a din : $slurp_strip[$rndom]
@splitter = split(/[A-Z]{1}/,$slurp_strip[$rndom]); #aici crapa daca intrebarile din db_nu au V3code

#verificam daca programa e rezolvata
$found='kz';
foreach my $k (keys %hlrline)
{

if($k =~ m/[A-Z]{1}$splitter[1]/) {
if(($hlrline{$k} eq 'y') && ($found eq 'kz')) {$found='y'; }
elsif($hlrline{$k} eq 'n'){
				$found='n';
#                   print qq!INSIST $k = $hlrline{$k}.. $splitter[0]<br>!; #debug
			  }
 } #all must be correct for chapter checked
} #.foreach key
if( $found eq 'y') #exista {1,} intrebari si toate rezolvate
 {$truth = 0; 
# print qq!COND 5: capitol inchis <br>\n!; #debug 
}
}
} #.end cond 5(truth).

#---

} #.end if tipcont(disabled with 0==1)

if($truth){ @pool = (@pool,$rndom); } #valoarea valida se baga in pool



#==indiferent de tipul de cont, daca fallback=0, dupa fiecare generare random se verifica
#==  conditia de fallback, adica rucksack gol;

if(($fallback == 0) && ($#rucksack < 1)) #mai e un singur elem in rucsac
	{

$fallback=1; 
@rucksack=(0..($fline-1));	#se reumple rucksacul
@pool=();			#se initializeaza lista de alese 

#print qq!FALLBACK to normal exam generating for this chapter<br>\n!; #debug 
	}
#== adaugarea intrebarii in @pool
#=======================.V3====
}#.end while random generator

@pool=sort{$a <=> $b} @pool;
#print qq!DEBUG final pool is @pool<br>\n!; #debug 
$entry = "$entry @pool"; #the proposed questions are entered, K \n is terminator

#tbd: print questions
#Action: Desfasuram intrebarile
my $index=0;
DIRTY: foreach my $item (@pool) #for each selected question
{
$index++; #this is the seen index of the question
$masked_index++; #masked index of question, hidden in html code 

#$watchdog=0;
do {
if (defined($fline=<INFILE>))
 {chomp($fline);}
else {$watchdog=1;}
}
while (!($fline =~ m/##$item#/) && ($watchdog == 0));   
##s-a gasit intrebarea sau s-a detectat EOF=overread attempt
if($watchdog == 0){
$fline = <INFILE>;				#se sare peste raspuns
$fline = <INFILE>;				#se citeste intrebarea
chomp($fline);
if($fline =~ m/^[0-9]{2,3}[A-Z]{1}[0-9]{2,}[a-z]?~&/) #should be m/cccc/
{
@splitter = split(/~&/,$fline);
print "<b>$index) $splitter[1]</b><br>\n";
}
else {
print "<b>$index) $fline</b><br>\n";
      }

#Daca exista, se insereaza imaginea cu WIDTH
$fline = <INFILE>;				#se citeste figura
chomp($fline);
#implementarea noua:
 if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/) {      
		my @pic_split=split(/ /,$fline);
                   if(defined($pic_split[1])) {
print qq!<br><center><img src="http://localhost/shelf/$pic_split[0]", width="$pic_split[1]"></center><br>\n!;
                        		      }
						    }
print qq!<dl>\n!;

#afisare intrebari a)-d) in ordine random
{
my @qline;
my @pool2=();
my $poolnr;

#subroutine declaration
sub random_int($);
#citeste intrebarile inainte, din cauza de random
$qline[0]=<INFILE>;
chomp($qline[0]);
$qline[1]=<INFILE>;
chomp($qline[1]);
$qline[2]=<INFILE>;
chomp($qline[2]);
$qline[3]=<INFILE>;
chomp($qline[3]);

my @pocket=(0..3);
while($#pool2 < 3) #generare cele 4 variante a)-d)
{
$poolnr = random_int($#pocket+1);
#print qq!extras: $pocket[$poolnr]<br>\n!;
@pool2=(@pool2,$pocket[$poolnr]);
#eliminam extrasul din rucksack
if($poolnr == 0) {@pocket = @pocket[1..$#pocket];}
elsif($poolnr == $#pocket) {@pocket = @pocket[0..($poolnr-1)];}
else {@pocket=(@pocket[0..($poolnr-1)],@pocket[($poolnr+1)..$#pocket]);}
}

foreach $poolnr (@pool2) {
print qq!<dd><input type="radio" value="$poolnr" name="question$masked_index">$qline[$poolnr]\n!;
                }
} #.end afisare intrebari a)-d)

print "<br><br>\n";
#insert the contributor
$fline=<INFILE>;
chomp($fline);
print qq!<font size="-1"color="yellow"><i>(Contributor: $fline)</i></font><br>\n!;

print qq!</dl><br>\n!;

} #.end no watchdog activated
else #watchdog situation detected 
{
#ACTION: append watchdog symptoms in cheat file
##asta se poate inlocui cu dienice() daca reusesti sa faci ceva cu bucla DIRTY;
##dienice("WATCHDOG",1);
open(cheatFILE,"+< cheat_log"); #or die("can't open cheat_log file: $!\n");					#open transaction file for writing
#flock(cheatFILE,2);		#LOCK_EX the file from other CGI instances

#ACTION: write in logfile
seek(cheatFILE,0,2);		#go to the end
#CUSTOM
printf cheatFILE "===========================================\n";
printf cheatFILE "sim_gen3.cgi v 3.2.1 : watchdog situation detected\n";
printf cheatFILE "file %s under work\n",$database[$iter];
printf cheatFILE "pool was: ";
foreach(@pool) { printf cheatFILE "%s ",$_; }
printf cheatFILE "crashed at question index: %i\n",$index;

close(cheatFILE);
print qq!<font color="red">Formular corupt si incomplet, va rog generati altul</font><br>\n!;

last DIRTY;
} #.end else

} #.end foreach $item
#------------------------------
#tbd: close database
#sure - logged close
close(INFILE) || dienice("ERR16",1,\"null");

} #.end foreach database

close(HLRread);

#tbd: inserare " K \n" la sfarsitul tranzactiei
$entry = "$entry K \n"; #the proposed questions are entered, K \n is terminator


#ACTION: inserare transaction ID in pagina HTML
{
print qq!<input type="hidden" name="transaction" value="$hexi">\n!;
}

print qq!<input type="submit" value="EVALUARE" name="answer">\n!;

print qq!</form>\n!;
print qq!</body>\n</html>\n!;


#$entry="$entry\n"; #adaugam fortat un \n
#append transaction
unless($watchdog == 1) #daca a crapat watchdogul, atunci aceeasi intrebare crapata sa nu intre in tranzactie, dam drop la tranzactie 
     {
@tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array
     }
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

#print "Tridfile length before write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close(transactionFILE) or dienice("ERR04",1,\"cant close transaction file");

} #.END BLOCK



#----100%------subrutina generare random number
# intoarce numar intre 0 si $max-1
sub random_int($)
	{
	
	my ($max)=@_;
        my $generated;
#     do {
         $generated = int rand($max);
#        }
#     while($generated >= $max);      
         
       return $generated;
	}
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

my $timestring=localtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "actiune ilegala, inregistrata in log",
              "ERR02" => "timpul alocat formularului a expirat",
              "ERR03" => "server congestionat",
              "ERR04" => "server congestionat",
              "ERR05" => "server congestionat",
              "ERR06" => "server congestionat",
              "ERR07" => "server congestionat",
              "ERR08" => "server congestionat",
              "ERR09" => "server congestionat",
              "ERR10" => "actiune ilegala, inregistrata in log",
              "ERR11" => "server congestionat",
              "ERR12" => "actiune ilegala, inregistrata in log",
              "ERR13" => "server congestionat",
              "ERR14" => "server congestionat",
              "ERR15" => "formularul a fost deja folosit odata",
              "ERR16" => "congestie server",
              "ERR17" => "actiune ilegala, inregistrata in log",
              "ERR18" => "actiune ilegala, inregistrata in log",
              "ERR19" => "tbd",
              "ERR20" => "tbd"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "transaction md5 authenticity failed",   #untested
              "ERR02" => "transaction timestamp expired, normally not logged",            
              "ERR03" => "fail open sim_transaction file",           #tested
              "ERR04" => "fail close sim_transaction file",
              "ERR05" => "fail open sim_users file",                 #tested
              "ERR06" => "fail open existing user's hlrfile",        #tested
              "ERR07" => "fail create new hlrfile",                  #tested
              "ERR08" => "fail close sim_users",
              "ERR09" => "fail close sim_transaction file",
              "ERR10" => "from wrong pagecode invoked generation of exam",
              "ERR11" => "fail close transaction file",
              "ERR12" => "wrong clearance level to request this exam",
              "ERR13" => "fail open user's hlrfile",
              "ERR14" => "fail open one of db_ file",
              "ERR15" => "transaction id already used, normally not logged",
              "ERR16" => "fail close one of db_file",
              "ERR17" => "received trid is undef",
              "ERR18" => "received trid is destruct",
              "ERR19" => "tbd",
              "ERR20" => "tbd"
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
printf cheatFILE "\<br\>reported by: sim_gen3.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
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
print qq!</body>\n</html>\n!;

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
