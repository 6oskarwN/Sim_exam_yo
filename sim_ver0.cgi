#!c:\Perl\bin\perl

# Prezentul simulator de examen impreuna cu formatul bazelor de intrebari, rezolvarile problemelor, manual de utilizare,
# instalare, SRS, cod sursa si utilitarele aferente constituie un pachet software gratuit care poate fi distribuit/modificat 
# in termenii licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in versiunea 2 sau intr-o 
# versiune ulterioara. 
# Programul, intrebarile si raspunsurile sunt distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio garantie,
# sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii.
# Utilizatorul programului, manualelor, codului sursa si utilitarelor are toate drepturile descrise in licenta publica GPL.
# In distributia pe CD sau download pe www.yo6kxp.org trebuie sa gasiti o copie a licentei GNU GPL, de asemenea si versiunea 
# in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/
# Textul intebarilor oficiale publicate de ANRCTI face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL, 
# modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind este permisa. Acest lucru deriva 
# din faptul ca ANRCTI este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.
# Site-ul de unde se poate descarca distributia oficiala a simulatorului este http://www.yo6kxp.org

# This program together with question database formatting, solutions to problems, manuals, documentation, sourcecode and
# utilitiesis is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 of the License, or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without any implied warranty. 
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this software distribution; if not, you can
# download it for free at http://www.fsf.org/ 
# Questions marked with ANRCTI makes an exception of above-written, as ANRCTI is a romanian public authority(similar to FCC in USA)
# so any use of the official questions, other than in Read-Only way, is prohibited. 

# YO6OWN Francisc TOTH, February 2008

#  sim_ver0.cgi v.0.0.6
#  Status: Released
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 0.0.6 fixed rebel link from window type to method="link" button
# ch 0.0.5 fixed trouble ticket 26
# ch 0.0.4 forestgreen and aquamarine colors changed to hex value
# ch 0.0.3 W3C audit passed
# ch 0.0.2 solved trouble ticket nr. 1
# ch 0.0.1 generated from ver0.cgi of HAMEXAM

use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

my $debug_buffer; #debugging I/O

#-for response retrieving
my %answer=();
my $post_trid;                  #transaction ID from POST data
#- for refreshing transaction list
my @tridfile;
my $trid;		#the Transaction-ID of the generated page

# - for search transaction in transaction list
my $expired;		#0 - expired/nonexisting transaction, n - existing transaction, n=pos. in the transaction list
my $correct;		#how many correct answers you gave



#### open transaction ID file ####
open(transactionFILE,"+< sim_transaction") or die("can't open transaction file: $!\n");					#open transaction file for writing
#flock(transactionFILE,2);		#lock the file from other CGI instances


###########################################
### Process inputs, generate hash table ###
###########################################
{
my $buffer=();
my @pairs;
my $pair;
my $name;
my $value;

#read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST-technology
$debug_buffer=$ENV{'QUERY_STRING'};
#@pairs=split(/&/, $buffer); #POST-technology
@pairs=split(/&/, $ENV{'QUERY_STRING'}); #GET-technology
foreach $pair(@pairs) 
		{

($name,$value) = split(/=/,$pair);

unless($name eq 'transaction'){
$value =~ tr/0/a/;
$value =~ tr/1/b/;
$value =~ tr/2/c/;
$value =~ tr/3/d/;
$value=~ s/<*>*<*>//g;
}
unless($name eq 'answer') { 
                 %answer = (%answer,$name,$value);		#add answers, except the submit button
			  } 
		} #.end foreach

} #.end process inputs

$post_trid= $answer{'transaction'}; #extract POST_trid from POST data

#now we have the hash table, debug
#my @temp1 = keys %answer;				#debug
#foreach (@temp1) {					#debug
#		print qq!K: $_  A: $answer{$_}<br>\n!;	#debug	
#                 }					#debug

###############################
### combined refresh-search ###    
###############################
{
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

#ACTION:read transaction ID
#-----------------------------------------------
#chomp($tridfile[0]);			#eliminate \n
#$tridfile[0]=hex($tridfile[0]);		#transform in numeral


#-----------------------------------
#-----------------------------------
my @utc_time=gmtime(time);
my $act_sec=$utc_time[0];
my $act_min=$utc_time[1];
my $act_hour=$utc_time[2];
my $act_day=$utc_time[3];
my $act_month=$utc_time[4];
my $act_year=$utc_time[5];
my @livelist=();
my @linesplit;


#print 'combo-refreh&search in transactionlist <br>',"\n"; #debug


unless($#tridfile == 0) 		#unless transaction list is empty
 {
  for(my $i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
   chomp $linesplit[8]; #\n is deleted

if (($linesplit[2] > 3) && ($linesplit[2] < 8)) {@livelist=(@livelist, $i);}#if this is an exam transaction, don't touch it
# next 'if' is changed into 'elsif'
elsif($linesplit[8] > $act_year) {@livelist=(@livelist, $i);}  #it's alive one more year, keep it in the list
 elsif($linesplit[8] == $act_year){
 if($linesplit[7] > $act_month) {@livelist=(@livelist, $i);}  #it's alive one more month, keep it in the list
 elsif($linesplit[7] == $act_month){
 if($linesplit[6] > $act_day) {@livelist=(@livelist, $i);}  #it's alive one more day, keep it in the list
 elsif($linesplit[6] == $act_day){
 if($linesplit[5] > $act_hour) {@livelist=(@livelist, $i);}  #it's alive one more day, keep it in the list
 elsif($linesplit[5] == $act_hour){
 if($linesplit[4] > $act_min) {@livelist=(@livelist, $i);}  #it's alive one more day, keep it in the list
 elsif($linesplit[4] == $act_min){
 if($linesplit[3] > $act_sec) {@livelist=(@livelist, $i);}  #it's alive one more day, keep it in the list
 
 } #.end elsif min
 } #.end elsif hour
 } #.end elsif day
 } #.end elsif month
 } #.end elsif year
    
 } #.end for
#we have now the list of the live transactions

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

 } #.end unless
} #.end refresh


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
   if($linesplit[0] eq $post_trid) {$expired=0;}
	else {@livelist=(@livelist, $i);}
  } #.end for

my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive

my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;
  
} #.end unless

##**********************************************************************************
if($expired) {
#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile

for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}
close (transactionFILE) or die("cant close transaction file\n");

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v.0.0.6\n!; #version print for easy upload check
#print qq![$debug_buffer]\n!; #debug
print qq!<br>\n!;
print qq!<h2 align="center">Formularul de examen a fost folosit deja sau a expirat</h2>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;

exit();
				} #.end expired
				
} #.END extraction BLOCK

####open db_human file
open(INFILE,"<", "db_human") || die("cant open db_human file $!\n"); #open the question file
#flock(INFILE,1);		        #shared lock, file can be read


	
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

close( INFILE ) || die("cannot close db_human file, $!\n");

if($correct>=3)
{

#ACTION: generate a new transaction for anonymous

$trid=$tridfile[0];
chomp $trid;						#eliminate \n
$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF


my @utc_time=gmtime(time);
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
#for this "sim_ver0.cgi" which generate the registration form
#the expiry time increments with max. 30minutes

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


#print to screen the entry in the transaction list
my $hexi= sprintf("%+06X",$trid);
my $entry = "$hexi anonymous 1 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n"; #anonymous 1 for 1st LUP
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
close (transactionFILE) or die("cant close transaction file\n");


###Generate the registration form ###
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v.0.0.6\n!; #version print for easy upload check
#print qq![$debug_buffer]\n!; #debug
print qq!<br>\n!;
print qq!<h1 align="center">OK, ai dat $correct raspunsuri corecte din 4 intrebari</h1>\n!;

#tiparire formular

print qq!<form action="http://localhost/cgi-bin/sim_register.cgi" method="get">\n!;

print qq!<center><b>Formular de inregistrare (valabil 15 minute)</b></center>\n!;


print qq!<table width="60%" align="center" border="1" cellpadding="4" cellspacing="2">\n!; 

print qq!<tr>\n!;
print qq!<td width="30%">!;
print qq!Login:!;
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="text" name="login" size="25">!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td width="30%">!;
print 'Parola:';
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="password" name="passwd1" size="25">!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td width="30%">!;
print 'Parola, din nou:';
print qq!</td>\n!;
print qq!<td>!;
print qq!<input type="password" name="passwd2" size="25">!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td width="30%">Tipul contului:</td>\n!;
print qq!<td><select size="1" name="tipcont">\n!;
print qq!<option value="0">Cont de antrenament</option>\n!;
print qq!<option value="1">Examen simulat clasa I</option>\n!;
print qq!<option value="2">Examen simulat clasa II</option>\n!;
print qq!<option value="3">Examen simulat clasa III</option>\n!;
print qq!<option value="4">Examen simulat clasa III-R</option>\n!;
print qq!</select>\n!;
print qq!</td>\n!;
print qq!</tr>\n!;



print qq!<tr>\n!;
print qq!<td width="33%">!;
print qq!<center><INPUT type="submit"  value="Inregistreaza"> </center>!;
print qq!</td>\n!;

print qq!<td>!;
print qq!<center><INPUT type="reset"  value="Reset"> </center>!;
print qq!</td>\n!;

print qq!</tr>\n!;

print qq!</table>\n!;


#ACTION: inserare transaction ID in pagina HTML
{
my $extra=sprintf("%+06X",$trid);
print qq!<input type="hidden" name="transaction" value="$extra">\n!;
}

print qq!</form>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="Abandon Inregistrare"></center>\n!; 
print qq!</form>\n!; 

print qq!<p>\n!;
print qq!Login trebuie sa aiba intre 4 si 25 caractere. Nu se accepta caractere speciale: %, space; login-ul trebuie sa fie unic si sa nu fie folosit deja. <br>\n!;
print qq!Parola si noua introducere a parolei trebuie sa aiba intre 8 si 25 caractere; trebuie sa fie congruente; nu pot contine caracterele %, space;<br>\n!; 
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
close (transactionFILE) or die("cant close transaction file\n");

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v.0.0.6\n!; #version print for easy upload check
#print qq![$debug_buffer]\n!; #debug
print qq!<br>\n!;
print qq!<h1 align="center">Insuficient, ai nimerit doar $correct din 4 intrebari.</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!; 

exit();
     }

} #.end transaction evaluation
#--------------------------------------
sub ins_gpl
{
print qq+<!--\n+;
print qq!SimEx Radio Release \n!;
print qq!SimEx Radio was created for YO6KXP ham-club located in Sacele, ROMANIA\n!;
print qq!\n!;
print qq!Prezentul simulator de examen impreuna cu formatul bazelor de intrebari, rezolvarile problemelor, manual de utilizare,!;
print qq!instalare, SRS, cod sursa si utilitarele aferente constituie un pachet software gratuit care poate fi distribuit/modificat!; 
print qq!in termenii licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in versiunea 2 sau intr-o !;
print qq!versiune ulterioara.\n!; 
print qq!Programul, intrebarile si raspunsurile sunt distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio garantie,!;
print qq!sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii.\n!;
print qq!Utilizatorul programului, manualelor, codului sursa si utilitarelor are toate drepturile descrise in licenta publica GPL.\n!;
print qq!In distributia pe CD sau download pe www.yo6kxp.org trebuie sa gasiti o copie a licentei GNU GPL, de asemenea si versiunea !;
print qq!in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/\n!;
print qq!Textul intebarilor oficiale publicate de ANRCTI face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL,!; 
print qq!modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind este permisa. Acest lucru deriva !;
print qq!din faptul ca ANRCTI este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.\n!;
print qq!Site-ul de unde se poate descarca distributia oficiala a simulatorului este http://www.yo6kxp.org\n!;
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;
print qq!This program together with question database formatting, solutions to problems, manuals, documentation, sourcecode and!;
print qq!utilitiesis is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License !;
print qq!as published by the Free Software Foundation; either version 2 of the License, or any later version.\n!;
print qq!This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without any implied warranty.!; 
print qq!See the GNU General Public License for more details.\n!;
print qq!You should have received a copy of the GNU General Public License along with this software distribution; if not, you can!;
print qq!download it for free at http://www.fsf.org/\n!; 
print qq!Questions marked with ANRCTI makes an exception of above-written, as ANRCTI is a romanian public authority(similar to FCC in USA)!;
print qq!so any use of the official questions, other than in Read-Only way, is prohibited.\n!; 
print qq!YO6OWN Francisc TOTH, 2008\n!;
print qq!\n!;

print qq!Made in Romania\n!;
print qq+-->\n+;

}



