#!c:\Perl\bin\perl

# Prezentul simulator de examen impreuna cu formatul bazelor de 
# intrebari, rezolvarile problemelor, manual de utilizare, instalare, 
# SRS, cod sursa si utilitarele aferente constituie un pachet software 
# gratuit care poate fi distribuit/modificat in termenii licentei libere 
# GNU GPL, asa cum este ea publicata de Free Software Foundation in 
# versiunea 2 sau intr-o versiune ulterioara. Programul, intrebarile si 
# raspunsurile sunt distribuite gratuit, in speranta ca vor fi 
# folositoare, dar fara nicio garantie, sau garantie implicita, vezi 
# textul licentei GNU GPL pentru mai multe detalii. Utilizatorul 
# programului, manualelor, codului sursa si utilitarelor are toate 
# drepturile descrise in licenta publica GPL. In distributia care se 
# gaseste la cerere de la autor sau eventual download pe examyo. 
# scienceontheweb.net trebuie sa gasiti o copie a licentei GNU GPL, de 
# asemenea si versiunea in limba romana, iar daca nu, ea poate fi 
# descarcata gratuit de pe pagina http://www.fsf.org/ Textul intebarilor 
# oficiale publicate de ANCOM face exceptie de la cele de mai sus, 
# nefacand obiectul licentierii GNU GPL, modificarea lor si/sau 
# folosirea lor in afara Romaniei in alt mod decat read-only nefiind 
# este permisa. Acest lucru deriva din faptul ca ANCOM este o 
# institutie publica romana, iar intrebarile publicate au caracter de 
# document oficial. Site-ul de unde se poate descarca distributia 
# oficiala a simulatorului este http://examyo.scienceontheweb.net

# This program together with question database formatting, solutions to 
# problems, manuals, documentation, sourcecode and utilitiesis is a free 
# software; you can redistribute it and/or modify it under the terms of 
# the GNU General Public License as published by the Free Software 
# Foundation; either version 2 of the License, or any later version. 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without any implied warranty. See the GNU 
# General Public License for more details. You should have received a 
# copy of the GNU General Public License along with this software 
# distribution; if not, you can download it for free at 
# http://www.fsf.org/ Questions marked with ANCOM makes an exception of 
# above-written, as ANCOM is a romanian public authority(similar to FCC 
# in USA) so any use of the official questions, other than in Read-Only 
# way, is prohibited.

# (c)YO6OWN Francisc TOTH, 2008 - 2013

#  sim_gen0.cgi v 3.2.0
#  Status: devel
#  This is a module of the online radioamateur examination program
#  Made in Romania

# ch 3.2.0 fix the https://github.com/6oskarwN/Sim_exam_yo/issues/3 
# ch 0.0.9 window button "OK" changed to method="link" button
# ch 0.0.8 infostudy/exam/exam7_yo.html sourced to index.html
# ch 0.0.7 hamxam/ eliminated
# ch 0.0.6 rucksack and pocket and watchdog implemented
# ch 0.0.5 fixed trouble ticket 26
# ch 0.0.4 forestgreen and aquamarine colors changed to hex values
# ch 0.0.3 W3C audit passed
# ch 0.0.2 solved trouble ticket nr. 6
# ch 0.0.1 generated from gen0.cgi, Ham-Exam platform


use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

#- for refreshing transaction list
my @tridfile;
my $trid;		#the Transaction-ID counter of the generated page
my $hexi;   #the trid+timestamp_MD5
my $entry;		#it's a bit of TRID

my $attempt_counter;			#attempts in opening or closing files; 5 attempts allowed
my $server_ok;					#flag; 1-server free; 0-server congested
$server_ok=1; #we suppose at the beginning a free server


#### open transaction file ####
$attempt_counter=1;
while ($server_ok and $attempt_counter > 0)
{ 
  if(open(transactionFILE,"+< sim_transaction")) {
          #flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
		  $attempt_counter=-1; #file was opened, no more attempt needed
			                                 } 
  else{ $server_ok = dienice("$!",$attempt_counter);
        $attempt_counter++;
	  }
} #end unless server congested

unless($server_ok) #if server is congested, exit;
{ exit();} 

####open db_human file
$attempt_counter=1;
while ($server_ok and $attempt_counter > 0)
{ 
  if(open(INFILE,"<","db_human")) {
          #flock(INFILE,1);		#LOCK_EX the file from other CGI instances
		  $attempt_counter=-1; #file was opened, no more attempt needed
			                                 } 
  else{ $server_ok = dienice("$!",$attempt_counter);
        $attempt_counter++;
	  }
} #end unless server congested

unless($server_ok) #if server is congested, exit;
{ exit();} 



print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.0\n!; #version print for easy upload check
print qq!<center><font size="+1" color="yellow">Rezolva 3 din 4 intrebari si poti sa te inregistrezi in examen</font></center><br>\n!;
print qq!<center><font size="+1" color="yellow">Pagina expira peste 3 minute.</font></center><br>\n!;
print qq!<center><font size="+1" color="yellow">O singura varianta de raspuns este corecta. Dupa alegerea raspunsurilor, apasa butonul "Evaluare".</font></center><br><br>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_ver0.cgi" method="get">\n!;


############################
### Generate transaction ###    
############################
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array


#ACTION: refresh transaction list, delete expired transactions,
# except exam transactions(code: 4,5,6,7)
{
my @utc_time=gmtime(time);
my $act_sec=$utc_time[0];
my $act_min=$utc_time[1];
my $act_hour=$utc_time[2];
my $act_day=$utc_time[3];
my $act_month=$utc_time[4];
my $act_year=$utc_time[5];

my @livelist=();
my @linesplit;

unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
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
#else {print qq!file has only $#tridfile lines!;}
#we have now the list of the live transactions
#print "@livelist[0..$#livelist]\n";   
my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive
#print "extra[0]: $extra[0]<br>\n";#debug
my $j;

foreach $j (@livelist) {@extra=(@extra,$tridfile[$j]);}
@tridfile=@extra;

#print "trid from extra: $tridfile[0]<br>\n";#debug

} #.end unless

#else {print qq!file has only $#tridfile lines<br>\n!;}
} #.end refresh

#print qq!after refresh: @tridfile[0..$#tridfile]\n!;

#ACTION: generate a new transaction for anonymous
{
#Action: generate new transaction
$trid=$tridfile[0];
chomp $trid;						#eliminate \n
$trid=hex($trid);		#convert string to numeric

if($trid == 0xFFFFFF) {$tridfile[0] = sprintf("%+06X\n",0);}
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}  #cyclical increment 000000 to 0xFFFFFF then convert back to string with sprintf()

#print qq!generate new transaction<br>\n!;
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
my $expire=3;   #3 minutes in this situation

#increment expiry time
#for this "sim_gen0.cgi" which generates the dummy exam,
#the expiry time increments with max. 5 minutes

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

$entry = "$hexi anonymous 0 $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year\n";
#print qq!mio entry: $entry <br>\n!; #debug
}
#.end of generating & writing of new transaction

###########################
###  Generate 4 questions ###
###########################

#subroutine declaration
sub random_int($);

my $fline;		#line read from file
my $rndom;              #used to store random integers
my @rucksack;	#we extract the questions from here
my $rindex;	#rucksack index
my @pool=();
my $watchdog;
my $item;


seek(INFILE,0,0);			#goto begin of file
$fline = <INFILE>;			 #skip the versioning string
$fline = <INFILE>;			 #read nr of questions
chomp($fline);				 #cut <CR> from end
@rucksack=(0..($fline-1));	#init rucksack
#print qq!rucksack content: @rucksack<br>\n!; #debug 

while($#pool < 3)
{
$rindex= random_int($#rucksack+1); #intoarce 0... $#rucksack
#print qq!rindex=$rindex<br>\n!; #debug
$rndom=$rucksack[$rindex];
#print qq!question \#$rndom generated<br>\n!; #debug

#trebuie eliminat elementul din rucksack
if($rindex == 0) {@rucksack = @rucksack[1..$#rucksack];}
elsif ($rindex == $#rucksack) {@rucksack = @rucksack[0..($rindex-1)];}
else {@rucksack=(@rucksack[0..($rindex-1)],@rucksack[($rindex+1)..$#rucksack]);}
#print qq!rucksack content: @rucksack<br>\n!; #debug
@pool = (@pool,$rndom);
}

@pool=sort{$a <=> $b} @pool;


DIRTY:foreach $item (@pool)
{
$watchdog=0;
do {
if(defined($fline=<INFILE>))
 {chomp($fline);}
 else {$watchdog=1;} 
   }
while (!($fline =~ m/##$item#/) && ($watchdog ==0));

##s-a gasit intrebarea sau s-a detectat EOF anormal
if ($watchdog == 0){
$fline = <INFILE>;				#se sare peste raspuns
$fline = <INFILE>;				#se citeste intrebarea
chomp($fline);
print "<b>$fline</b><br>\n";	#se tipareste intrebarea

#Daca exista, se insereaza imaginea cu WIDTH
$fline = <INFILE>;				#se citeste figura
chomp($fline);
#implementare noua:
if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/) 
         {
        my @pic_split = split(/ /,$fline);
        if(defined($pic_split[1])) { 

print qq!<br><center><img src="http://localhost/shelf/$pic_split[0]" width="$pic_split[1]"></center><br>\n!; 
                                    }
         }

print '<dl>',"\n";

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
#print qq!pool2 este @pool2 - pocket este @pocket<br>\n!;
foreach $poolnr (@pool2) {
print qq!<dd><input type="radio" value="$poolnr" name="question$item">$qline[$poolnr]\n!;
                }
} #.end afisare intrebari a)-d)
print "<br><br>\n";

#insert the contributor
$fline=<INFILE>;
chomp($fline);
print qq!<font size="-1"color="yellow"><i>(Contributor: $fline)</i></font><br>\n!;

print '</dd></dl><br>',"\n";

} #.end no watchdog activated
else #watchdog activated
 {print qq!generating stopped by watchdog, database crash, this form will not evaluate, please try another one<br>\n!;
last DIRTY;
 }

} #.end foreach $item

close( INFILE ) ||die("cannot close, $!\n");

#ACTION: inserare transaction ID in pagina HTML
{
print qq!<input type="hidden" name="transaction" value="$hexi">\n!;
}

print qq!<input type="submit" value="EVALUARE" name="answer">\n!;


print '</form>',"\n";
print '</body></html>',"\n";



#append transaction
unless($watchdog==1)
 {
 @tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array
 }

#print "Trid-array after adding new-trid: @tridfile[0..$#tridfile]<br>\n"; #debug

#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction file
#print "Tridfile length before write: $#tridfile \n";
for(my $i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

#closing transaction file, opens flock by default
close (transactionFILE) or die("cant close transaction file\n");

sub compute_mac {
# Given a message and key, returns a message authentication code
# with the following properties relevant to our example:
# - a 22-character string that may contain + / 0-9 a-z A-Z
# - any given message and key will always produce the same MAC
# - if you don't know the key, it's very hard to guess it
#   even if you have a message, its MAC, and this source code
# - if you have a message, its MAC, and even the key, it's 
#   very hard to find a different message with the same MAC
# - even a tiny change to a message, including adding on to
#   the end of it, will produce a very different MAC
use Digest::MD5;
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
    Digest::MD5::md5_base64($secret, Digest::MD5::md5($secret, $message));
} #end of compute_mac



#----100%------subrutina generare random number
sub random_int($)
	{
	
	my ($max)=@_;

       return int rand($max);
	}

#------------------------------------------
sub dienice
{
my ($error_code,$counter)=@_;

#write errorcode in cheat_file

#if number of errors is > 4, print a defeat page
if($counter > 4)
 {
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.0\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">Serverul este congestionat, incearca din nou.</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;
return (0); #return server congested
 }
else {return (1); #server not yet congested
     }
} #end sub
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
print qq!In distributia pe CD sau download pe examyo.scienceontheweb.net trebuie sa gasiti o copie a licentei GNU GPL, de asemenea si versiunea !;
print qq!in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/\n!;
print qq!Textul intebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL,!; 
print qq!modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind este permisa. Acest lucru deriva !;
print qq!din faptul ca ANCOM este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.\n!;
print qq!Site-ul de unde se poate descarca distributia oficiala a simulatorului este http://examyo.scienceontheweb.net\n!;
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;
print qq!This program together with question database formatting, solutions to problems, manuals, documentation, sourcecode and!;
print qq!utilitiesis is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License !;
print qq!as published by the Free Software Foundation; either version 2 of the License, or any later version.\n!;
print qq!This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without any implied warranty.!; 
print qq!See the GNU General Public License for more details.\n!;
print qq!You should have received a copy of the GNU General Public License along with this software distribution; if not, you can!;
print qq!download it for free at http://www.fsf.org/\n!; 
print qq!Questions marked with ANCOM makes an exception of above-written, as ANCOM is a romanian public authority(similar to FCC in USA)!;
print qq!so any use of the official questions, other than in Read-Only way, is prohibited.\n!; 
print qq!YO6OWN Francisc TOTH, 2008\n!;
print qq!\n!;

print qq!Made in Romania\n!;
print qq+-->\n+;

}
