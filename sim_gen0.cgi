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

# (c) YO6OWN Francisc TOTH, 2008 - 2018

#  sim_gen0.cgi v 3.2.4
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

# ch 3.2.4 compute_mac() changed from MD5 to SHA1
# ch 3.2.3 integrated sub timestamp_expired(); introduce epoch timestamping
# ch 3.2.2 implemented silent discard Status 204
# ch 3.2.1 deploy latest dienice()
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
sub ins_gpl;                    #inserts a HTML preformatted text with the GPL license text

# for refreshing transaction list
my @tridfile;
my $trid;		#the Transaction-ID counter of the generated page
my $hexi;   		#the trid+timestamp_MD5
my $entry;		#it's a bit of TRID

my $attempt_counter;			#attempts in opening or closing files; 5 attempts allowed
my $server_ok;		#flag; 1-server free; 0-server congested
$server_ok=1; #we suppose at the beginning a free server
#### process inputs
#BLOCK: Input:transaction ID
{
# Read input text, POST or GET
# GET-technology for us not ok, permits multiple requests made by browser.

  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case 
  if($ENV{'REQUEST_METHOD'} eq "GET") 
  { 
dienice ("ERR20",0,\"unexpected GET");  #silently discard
       }
## end of GET method
 
} #.end process inputs



#### open transaction file, try 3 times ####
$attempt_counter=0;
while ($attempt_counter < 3)
{ 
  if(open(transactionFILE,"+< sim_transaction")) {
          #flock(transactionFILE,2);		#LOCK_EX the file from other CGI instances
		  $attempt_counter=3; #file was opened, no more attempt needed
                  $server_ok=1;       #file was opened so server is ok
			                          } 
  else{ $server_ok = 0; #server still not ok
        $attempt_counter++;
	  }
} #end while

unless($server_ok) #if server is congested, die with error code;
{ dienice("ERR01",1,\$!) }

####open db_human file
$attempt_counter=1;
while ($attempt_counter < 3)
{ 
  if(open(INFILE,"<","db_human")) {
          #flock(INFILE,1);		#LOCK_EX the file from other CGI instances
		  $attempt_counter=3; #file was opened, no more attempt needed
                  $server_ok=1;       #file was opened so server is ok
			                                 } 
  else{ $server_ok = 0; #server still not ok
        $attempt_counter++;
	  }
} #end while

unless($server_ok) #if server is congested, die with error code;
{ dienice("ERR02",1,\$!) }


print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl();
print qq!v 3.2.4\n!; #version print for easy upload check
print qq!<center><font size="+1" color="yellow">Rezolva 3 din 4 intrebari si poti sa te inregistrezi in examen</font></center><br>\n!;
print qq!<center><font size="+1" color="yellow">Pagina expira peste 3 minute.</font></center><br>\n!;
print qq!<center><font size="+1" color="yellow">O singura varianta de raspuns este corecta. Dupa alegerea raspunsurilor, apasa butonul "Evaluare".</font></center><br><br>\n!;
print qq!<form action="http://localhost/cgi-bin/sim_ver0.cgi" method="post">\n!;


############################
### Generate transaction ###    
############################
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array


#ACTION: refresh transaction list, delete expired transactions,
# except exam transactions(code: 4,5,6,7)
{
my @livelist=();
my @linesplit;

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
my $epochTime = time();
#CHANGE THIS for customizing
my $epochExpire = $epochTime + 180;		#3 min = 3 * 60 sec = 180 sec 
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];

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
#--------------------
sub compute_mac {

use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
  hmac_sha1_hex($secret,$message);
} #end of compute_mac

#----100%------subrutina generare random number
# intoarce numar intre 0 si $max-1
sub random_int($)
	{
	
	my ($max)=@_;

       return int rand($max);
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

my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "Server congestionat, incearca in cateva momente",
              "ERR02" => "Server congestionat, incearca in cateva momente",
              "ERR03" => "reserved",
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "reserved",
              "ERR07" => "reserved",
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
              "ERR19" => "silent logging, not displayed",
              "ERR20" => "silent discard, not displayed"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "server cannot open sim_transaction file",    #test
              "ERR02" => "server cannot open db_human file",           #test 
              "ERR03" => "reserved",
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "reserved",
              "ERR07" => "reserved",
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
              "ERR19" => "silent logging",
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
printf cheatFILE "\<br\>reported by: sim_gen0.cgi\<br\>  %s: %s \<br\> UTC Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
}
if($error_code eq 'ERR20') #must be silently discarded with Status 204 which forces browser stay in same state
{
print qq!Status: 204 No Content\n\n!;
print qq!Content-type: text/html\n\n!;
}
else
{
unless($error_code eq 'ERR19'){ #ERR19 is silent logging, no display, no exit()
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl(); #this must exist
print qq!v 3.2.4\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;
                              }
}

exit();

} #end sub

#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year UTC
#out: seconds since expired MAX 99999, 0 = not expired.
#UTC time and epoch are used

sub timestamp_expired
{
use Time::Local; #library name

my($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year)=@_;

my $timediff;
my $actualTime = time(); #epoch since UTC0000
my $dateTime= timegm($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year);
$timediff=$actualTime-$dateTime;

#if ($timediff < 0 ) {return (0);}
#else {return($timediff);}  #here is the general return

return($timediff);  #here is the general return

} #.end sub timestamp

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
