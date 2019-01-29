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

#  sim_gen3.cgi v 3.3.3
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.3.3 solving https://github.com/6oskarwN/Sim_exam_yo/issues/14 - set a max size to db_tt
# ch 3.3.2 compute_mac() changed from MD5 to SHA1
# ch 3.3.1 bug fix at rucksack algorithm, introduced epoch() instead of gmtime()
# ch 3.3.0 implemented the mods given by law update Decizia 245/2017
# ch 3.2.3 implemented use_time in recorded transaction_id;timestamp_expired()
# ch 3.2.2 implemented silent discard Status 204
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
#          + rezolvata problema de blocare la afisarea formularului cu date corupte 
#          + daca se detecteaza greseala la afisare, nu se mai genereaza transaction = protectie
# ch 3.0.7 la fallback se da purge doar la reject list,  se imbunatateste acoperirea ultimelor intrebari din programa.
# ch 3.0.6 schimbat modul de afisare al imaginii de intrebare
# ch 3.0.5 correction and debugs removed
# ch 3.0.4 conditia 5 testata ca slow-convergence
# ch 3.0.3 partially debugged
# ch 3.0.2 attempts to generate the new-style exam
# ch 3.0.1 creates hlr record as in 3.0.0 but overwrites the other classes, implementing selfdelete
# ch 3.0.0 creates /hlr file if user is training user and has no /hlr record
# ch 2.0.2 fixed trouble ticket 26
# ch 2.0.1 implemented Feature Request 2
# ch 2.0.0 coding Feature Change trouble ticket 12

use strict;
use warnings;

use lib '.';
use My::ExamLib qw(ins_gpl timestamp_expired compute_mac dienice random_int);


my $get_trid;                   #transaction ID from GET data
my $trid_id;                    #transaction ID extracted from transaction file
my $trid_login;			#login extracted from transaction file
my $trid_login_hlrname;         #$trid_login with escape chars where needed
my $trid_pagecode;		#pagecode from transaction file

my $tipcont;			#tipcont extracted from user file
my $ultimaclasa;                #ultima clasa obtinuta: 0=init, 1/2/3/4=clase 5=failed

my @tridfile;		        #slurped transaction file
my $trid;	                #the Transaction-ID of the generated page
my $hexi;                       #the trid+timestamp_SHA1
my @slurp_userfile;            	#RAM-userfile

my $attempt_counter;	        #attempts in opening or closing files; 5 attempts allowed
my $server_ok;			#flag; 1-server free; 0-server congested

my $hlrclass="blabla123";	#clasa1,2,3,clasa4 defined by first line in hlrfile  
				#hlrclass init=7 is just not to have undefined

$server_ok=1;                   #we suppose at the beginning a free server


#BLOCK: Input:transaction ID
{
my $buffer=();
my @pairs;
my $pair;
my $stdin_name;
my $stdin_value;

# Read input text, POST or GET
# GET-technology for us not ok, permits multiple requests made by browser.

  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case 
  if($ENV{'REQUEST_METHOD'} eq "GET") 
       { 
	dienice ("ERR20",0,\"unexpected GET");  #silently discard
       }
## end of GET

 
else {
read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST-technology
     }

#inainte de split, $buffer citit ar trebui confruntat cu un regexp pt sintaxa

@pairs=split(/&/, $buffer); #POST-technology


foreach $pair(@pairs) {
($stdin_name,$stdin_value) = split(/=/,$pair); #se presupune cateodata gresit ca avem abele parti ale perechii

if(defined($stdin_value)){
#transformarea asta e pentru textele reflow, dar trateaza si + si / al token-ului
$stdin_value=~ s/\+/ /g;  #GET an POST send + but + is also character of transaction. Check for possible bug from this
$stdin_value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$stdin_value=~ s/<*>*<*>//g; #clears html,xml tag injection
                         }

if($stdin_name eq 'transaction') {if(defined($stdin_value)){$get_trid=$stdin_value;}
                                    else{$get_trid=undef;}

#am presupus ca daca cheia e 'transaction' atunci 'value' e neaparat transaction. S-ar putea sa nu fie adevarat 

}

} #.end foreach
} #.end process inputs

#now we have the hash table with answers. error: they can be less answers than needed
#or they can be less answers than all, but this is not error. answers for questions are not
#Mandatory, but Optional parameters. User can answer all or less questions.
#Occam check  -not implemented yet
#this should silently discard if not all mandatory parameters are received




#md MAC has + = %2B and / = %2F characters, must be reconverted - already done
if(!defined($get_trid)) {dienice ("ERR20",0,\"undef trid"); } # no transaction or with void value


#ACTION: open transaction ID file and clear expired transactions

open(transactionFILE,"+< sim_transaction") || dienice("genERR03",1,\"null");
#flock(transactionFILE,2);

#ACTION: refresh transaction file
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

my $expired=0;  #flag which checks if posted transaction has expired. Set to 'not expired'

#BLOCK: Refresh transaction file to delete expired transactions
{
my @livelist=();
my @linesplit;

#unused: B000C1_59_49_10_14_2_116_Ljxx+XY1v+S2QR0GHT/3ng owene 4 59 49 10 14 2 116 
#used:   B000C1_59_49_10_14_2_116_Ljxx+XY1v+S2QR0GHT/3ng_*_00_00_10_14_2_116 owene 4 59 49 10 14 2 116 

#TIME-EXPIRY based refresh
unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   chomp $linesplit[8]; #\n is deleted

if ($linesplit[2] =~ /[4-7]/) {@livelist=(@livelist, $i);} #if this is an exam transaction, do not refresh it even it's expired, is the job of sim_authent.cgi
elsif (timestamp_expired($linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7],$linesplit[8])>0) {} #if timestamp expired do nothing = transaction will not refresh
      else {@livelist=(@livelist, $i);} #not expired, keep it
  } #.end for
#we have now the list of the live transactions + exams


my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

} #.end unless

} #.END time-based refresh BLOCK


#BLOCK: extract data from actual transaction but read-only
#ch 3.2.3 - modified
{
my @linesplit;
#my $expired=1;  #debug
my $branch=1;#verifies if branch was taken
unless(($#tridfile == 0) || ($expired)) #unless transaction list is empty (but transaction exists on first line) or posted transaction has expired
{  
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions.  
  {
  @linesplit=split(/ /,$tridfile[$i]);

#ch 3.2.3 aici linesplit[0] poate sa aiba sau nu bucata de "used_timestamp" si atunci eq nu mai e eq
  if($linesplit[0] =~ /^\Q$get_trid\E/) { 
					$trid_login=$linesplit[1];     #extract data
			                $trid_id   =$linesplit[0]; #extract transaction
					$trid_pagecode=$linesplit[2];  #extract data
					$branch=0; #found, so not expired
				        }
  } #.end for

} #.end unless
if($branch) {$expired=1;} #the case of unknown transaction id
if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close(transactionFILE) || dienice("genERR04",1,\"null");

#now we should check why received transaction was not found in sim_transaction file
#case 0: it's an illegal transaction if sha1 check fails
#        must be recorded in cheat_file
#case 1: sha1 correct but transaction timestamp expired, file was refreshed and wiped this transaction
#        must be announced to user
#case 2: sha1 ok, timestamp ok, it must (ch 3.2.3) be some sort of weird error that must be logged
#        unexpired transactions that are used or not should be in sim_transaction

#check case 0
#incoming is like 'B00053_25_8_23_11_2_116_4N9RcV572jWzLG+bW8vumQ'
{ #local block start
my @pairs; #local
my $string_trid; # we compose the incoming transaction to recalculate mac
my $heximac;


@pairs=split(/_/,$get_trid); #reusing @pairs variable for spliting results

# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("genERR18",1,\$get_trid); } # unstructured trid

$string_trid="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_trid);

unless($heximac eq $pairs[7]) { dienice("genERR01",1,\$get_trid);}

#check case 1, timestamp
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])>0) { 
                                             dienice("genERR02",0,\"null"); }

#else is really case 2 so transaction already used
else { dienice("genERR09",5,\$get_trid);  }

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
if ($trid_id =~ m/\*/) { #if it has the used mark 
  my $usedTime = timestamp_expired($pairs[9],$pairs[10],$pairs[11],$pairs[12],$pairs[13],$pairs[14]);
  if ($usedTime < 10) { #if request comes faster than 10s, might be some browser parallel request
                           #dienice ("ERR20",1,\"debug fast request $usedTime seconds \, $trid_id");  #debug symptom catch
                            dienice ("ERR20",0,\"null");  #silent discard, Status 204 No Content
                        }
   else { 
         #dienice ("genERR15",1,\$trid_id); #debug - symptom catch 
         dienice ("genERR15",0,\"null"); 
        }                          
                       }
#===============.end ch 3.2.3========================

} #.END extraction BLOCK


#we have here the login and pagecode of the guy from transaction data.
#-----------------------------------------------------
#ACTION: open user account file

open(userFILE,"< sim_users") || dienice("genERR05",1,\"null");
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
open(HLRread,"< hlr/$trid_login_hlrname") || dienice("genERR06",1,\"null"); #open for reading only
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
open(HLRfile,"> hlr/$trid_login_hlrname") || dienice("genERR07",1,\"null");

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
close(userFILE) || dienice("genERR08",1,\"null");


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
close(transactionFILE) || dienice("genERR04",1,\"null");

#ACTION: append cheat symptoms in cheat file
my $err_harvester="pagecode\: $trid_pagecode login\: $trid_login";
dienice("genERR10",1,\$err_harvester);
} #.end unless $trid_pagecode

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

close(transactionFILE) || dienice("genERR11",1,\"null");


#ACTION: append cheat symptoms in cheat file
my $err_harvester="\$trid_login\: $trid_login \$tipcont\: $tipcont";
dienice("genERR12",1,\$err_harvester);
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

#print qq!generate new transaction<br>\n!;
my $epochTime = time();
#CHANGE THIS for customizing
my $epochExpire = $epochTime + 7200;		#3 min = 2 * 60 * 60 sec = 180 sec 
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];

#generate transaction id and its sha1 MAC

$hexi= sprintf("%+06X",$trid); #the transaction counter
#assemble the trid+timestamp
$hexi= "$hexi\_$exp_sec\_$exp_min\_$exp_hour\_$exp_day\_$exp_month\_$exp_year\_"; #adds the expiry timestamp and sha1
#compute mac for trid+timestamp
my $heximac = compute_mac($hexi); #compute SHA1 MessageAuthentication Code
$hexi= "$hexi$heximac"; #the full transaction id

#CUSTOM: pagecode=6 pentru exam cl III
my $entry = "$hexi $trid_login 6 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year";

#} #.END BLOCK

#BLOCK: generate the questions of the exam
#e implementat cu 3 liste: lista fisierelor , lista cu nr de intrebari/fisier, lista capitolelor
#bagat intr-o bucla for sau foreach
#

{
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
my $chosenOne;	#the extracted question is chosen = 1, or not = 0
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

#ACTION: Generate HTML header of the exam
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.3.3\n!; #version print for easy upload check

print qq!<center><font size="+2">Examen clasa III</font></center>\n!;   #CUSTOM
print qq!<center><font size="+2">O singura varianta de raspuns corecta din 4 posibile.</font></center>\n!;
print qq!<center><font size="+1">Timpul alocat examenului este de 2 ore.</font></center><br>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_ver3.cgi" method="post">\n!; #CUSTOM

#==========================v3==
# if hlrfile (-e) usertype==0(antrenament) and hlr class='clasa3') openfile and skip first line #CUSTOM
if($tipcont == 0) #for sure hlr file exists, was created just lines above
{
open(HLRread,"<hlr/$trid_login_hlrname") || dienice("genERR13",1,\"null"); #open for reading only
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
open(INFILE,"< $database[$iter]") || dienice("genERR14",1,\"null");   
#flock(INFILE,1);		#LOCK_SH the file from other CGI instances



#====== V3 ======
#for each database the hash is loaded
%hlrline=(); #init
# if hlrfile (-e) and  usertype==0(antrenament))
if($tipcont == 0) #but hlr file exists for taining account
{
#fetch hlr line corresponding to $database[$iter]
$hlrclass = <HLRread>; #variable reused to fetch the corresponding line from HLR
chomp $hlrclass;

#print qq!DEBUG:in hlr avem:$hlrclass<br>\n!; #debug

#load the hash TBD
@splitter= split(/,/,$hlrclass);

for (my $split_iter=0; $split_iter<($#splitter/2);$split_iter++) #or ($#splitter+1)/2 - same effect
 {
 %hlrline = (%hlrline,$splitter[$split_iter*2],$splitter[$split_iter*2+1]); #daca linia e stocata direct sub forma de string de hash; 
  } #.end for split iter

#print Dumper(\%hlrline);  #debug only

} # .end if(-e, antrenament)

#open,load and close the appropriate stripfile
#stripfiles are used by all user types
#stripfiles REALLY needed.
open(stripFILE, "<$strips[$iter]") || dienice("genERR14",1,\"null");
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
seek(INFILE,0,0);			#goto begin of questions database file
$fline = <INFILE>;			#read away dummy version string from first line
$fline = <INFILE>;			#read nr of questions
chomp($fline);				#cut <CR> from end

#QUESTION POOL GENERATION


#init the rucksack(fill it in)
#print qq!db_counter: $fline<br>\n!; #debug 
@rucksack=(0..($fline-1)); 
#print qq!rucksack content: @rucksack<br>\n!; #debug 
#print Dumper(\@rucksack); #same debug


@pool=();       #init pool of chosen questions
$fallback=0;    #for training users generate with all conditions(fallback=1 is one-shot exam-like conditions)

#conditia de while trebuie imbunatatita si   cu conditia V3 de iesire
while($#pool < (($qcount[$iter])-1))	#do until number of questions is reached; - asta nu da voie la never reached or fallback condition?
{

#take out a $rndom out of rucksack
$rindex= random_int($#rucksack+1); #intoarce intre 0 .. $#rucksack 
#print qq!rindex = $rindex !; #debug
$rndom=$rucksack[$rindex]; #rndom extracted from what remains in rucksack
#print qq!debug: new question $rndom<br>\n!; #debug 


$chosenOne=0;   #$rndom is not chosen yet, that we shall see
#===== V3 =====
#conditions applicable in all modes, both non-hlr or 'training'


#conditie eliminatoare din rucksack: pentru training daca intrebarea e in hlr cu 'y'
#cond 3:daca intrebarea exista in hlr cu y, skip.

if(($tipcont == 0) && ($fallback == 0) && ($chosenOne == 0)) #applicable only for usertype=0 when no fallback is ordered
{

#Intrebarea: $slurp_strip[$rndom]
#print qq!COND 3: daca nu vezi variabila, o sa vezi in error_log: $slurp_strip[$rndom]<br>\n!; #debug 
unless($slurp_strip[$rndom] =~ m/^$/) #conditia are sens doar pentru intrebarile cu cod v3
 {
  my $stripper=$slurp_strip[$rndom]; 
  chomp $stripper;
  #print qq!pentru \#$rndom cod v3 e \;$slurp_strip[$rndom]\; cu $hlrline{$stripper}<br>\n!; #debug 
  if(defined($hlrline{$stripper})) #nu stii daca exista cheia!!!
      {
  if($hlrline{$stripper} eq 'y') 
    {
     $chosenOne=1; #chosen for removal from rucksack without adding in pool
 #    print qq!COND 3: \#$rndom e cu y in hlr, $slurp_strip[$rndom]; <br>\n!; #debug 
    }
      }#.if defined

 }#.if unless v3 code exists


} #.end if tipcont(disabled with 0==1)

#---------------------------------------
#conditie de test, bagatoare in pool
if($chosenOne == 0) #fallback or not, exam or training, if not elliminated yet
{
@pool = (@pool,$rndom); #insert to pool
$chosenOne =1; #mark it as chosen for pool
#print qq!new pool: @pool<br>\n!; #debug 

}

#--------------------------------------
     	#we extract it from din rucksack

if($chosenOne)
   { 	
	if($rindex == 0) {@rucksack = @rucksack[1..$#rucksack];}
	elsif ($rindex == $#rucksack) {@rucksack = @rucksack[0..($rindex-1)];}
	else {@rucksack=(@rucksack[0..($rindex-1)],@rucksack[($rindex+1)..$#rucksack]);}
#	print qq!$rndom removed <br>new rucksack: @rucksack<br>\n!; #debug 
  
   } #removed from rucksack



#==indiferent de tipul de cont, daca fallback=0, dupa fiecare generare random se verifica
#==  conditia de fallback, adica rucksack gol;

#se poate inlocui cu conditia rapida #rucksack + #pool < desired size
if(($fallback == 0) && ($#rucksack + $#pool < $qcount[$iter])) #sunt pre putine ramase in rucsac
	{
	$fallback=1;
	@rucksack=(0..($fline-1));	#se reumple rucksacul
	@pool=();			#se initializeaza lista de alese 
#	print qq!FALLBACK to normal exam generating for this chapter<br>\n!; #debug 
	#dienice("ERR19",5,\"null");     #debug only
	}

#=======================.V3====



}#.end while random generator
# all the proposed questions are in the question pool now


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

print qq!<font color="red">Formular corupt si incomplet, va rog generati altul</font><br>\n!;

last DIRTY;
} #.end else

} #.end foreach $item
#------------------------------
#close database
close(INFILE) || dienice("genERR16",1,\"null");

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
#print qq!</body>\n</html>\n!; #aici a fost locul normal


#$entry="$entry\n"; #adaugam fortat un \n
#append transaction
unless($watchdog == 1) #daca a crapat watchdogul, atunci aceeasi intrebare crapata sa nu intre in tranzactie, dam drop la tranzactie 
     {
@tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array
     }


#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

{ #begin final transaction miniblock
my $epochTime = time();
my ($act_sec, $act_min, $act_hour, $act_day,$act_month,$act_year) = (gmtime($epochTime))[0,1,2,3,4,5];
my @linesplit;


#print "Tridfile length before write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{

#ch 3.2.3 - we must add to our transaction the "used" timestamp
#========ch 3.2.3========
@linesplit=split(/ /,$tridfile[$i]);

  if($linesplit[0] =~ /^\Q$trid_id\E/)  
 {
   ## print qq!$linesplit[0]<br>!; #debug
   my $usedTimestamp = $linesplit[0].'_'.'*_'."$act_sec\_$act_min\_$act_hour\_$act_day\_$act_month\_$act_year"; #adds the used timestamp
   ##print qq!$usedTimestamp<br>!; #debug
   $tridfile[$i] =~ s/\Q$linesplit[0]\E/$usedTimestamp/g;
   ##print qq!$tridfile[$i]!; #debug
#=========.ch 3.2.3==========
 }


printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
} #.end for

close(transactionFILE) or dienice("genERR04",1,\"cant close transaction file");
} #.end miniblock

print qq!</body>\n</html>\n!; #debug place

} #.END BLOCK


