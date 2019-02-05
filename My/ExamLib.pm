package My::ExamLib;
use strict;
use warnings;

use Exporter qw(import);
our @EXPORT_OK = qw(ins_gpl timestamp_expired compute_mac dienice random_int);

#-----------------------------------
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

#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year UTC
#out: seconds since expired MAX 99999, 0 = not expired.
#UTC time and epoch are used

sub timestamp_expired
{
use Time::Local;

my($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year)=@_;

my $timediff;
my $actualTime = time(); #epoch since UTC0000
my $dateTime= timegm($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year);
$timediff=$actualTime-$dateTime;

return($timediff);  #here is the general return

} #.end sub timestamp

#--------------------------------------
sub compute_mac {

use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b'; #development secret
  hmac_sha1_hex($secret,$message);
} #end of compute_mac

#-------------------------------------
# treat the "or die" and all error cases
#how to use it
#$error_code is a string, you see it, this is the text selector
#$counter: if it is 0, error is not logged. If 1..5 = threat factor
#reference is the reference to string that is passed to be logged.
#ERR19 and ERR20 have special handling regarding the browser error display

sub dienice
{
my ($error_code,$counter,$err_reference)=@_; #in vers. urmatoare counter e modificat in referinta la array/string

my $timestring=gmtime(time);

my($package,$filename,$line)=caller;

#textul pentru public
my %pub_errors= (

              "ERR00" => "error: unknown/unspecified",
#astea cu cannot open file, toate
              "gen0ERR02" => "Server congestionat, incearca in cateva momente",
              "gen0ERR01" => "Server congestionat, incearca in cateva momente",
              "authERR10" => "Server congestionat, incearca in cateva momente",
              "ver0ERR07" => "Server congestionat, incearca in cateva momente",
              "chkERR06" => "Server congestionat, incearca in cateva momente",
              "genERR06" => "Server congestionat, incearca in cateva momente",
              "genERR13" => "Server congestionat, incearca in cateva momente",
              "genERR14" => "Server congestionat, incearca in cateva momente",
              "genERR03" => "Server congestionat, incearca in cateva momente",
              "genERR05" => "Server congestionat, incearca in cateva momente",
              "ver0ERR06" => "Server congestionat, incearca in cateva momente",
              "verERR06" => "Server congestionat, incearca in cateva momente",
              "regERR06" => "Server congestionat, incearca in cateva momente",
              "tugERR04" => "Server congestionat, incearca in cateva momente",
              "authERR08" => "Server congestionat, incearca in cateva momente",

#astea cu cannot close file, toate
              "genERR08" => "Server congestionat, incearca in cateva momente",
              "genERR16" => "Server congestionat, incearca in cateva momente",
              "genERR11" => "Server congestionat, incearca in cateva momente",
              "authERR09" => "Server congestionat, incearca in cateva momente",
              "ver0ERR08" => "Server congestionat, incearca in cateva momente",
              "verERR07" => "Server congestionat, incearca in cateva momente",
              "regERR07" => "Server congestionat, incearca in cateva momente",
              "chkERR07" => "Server congestionat, incearca in cateva momente",

#unprocessed
              "authERR01" => "primire de  date corupte.",

              "genERR01" => "actiune ilegala, inregistrata in log",
              "ver0ERR01" => "primire de  date corupte, inregistrata in log.",
              "verERR01" => "primire de  date corupte, inregistrata in log.",
              "regERR01" => "primire de  date corupte, inregistrata in log.",
              "admERR01" => "admin authentication token fail, logged.",
              "chkERR01" => "primire de  date corupte, inregistrata in log.",
              "tugERR01" => "authentication fail, logged.",
              "ttERR01" => "date invalide",

              "authERR02" => "primire de date corupte",

              "genERR02" => "timpul alocat formularului a expirat",
              "ver0ERR02" => "pagina pe care ai trimis-o a expirat",
              "verERR02" => "pagina pe care ai trimis-o a expirat",
              "regERR02" => "pagina pe care ai trimis-o a expirat",
              "admERR02" => "token expired, get another token",
              "tugERR02" => "authentication token expired",
              "ttERR02" => "input lipsa",

              "authERR03" => "Credentiale incorecte.<br><br>ATENTIE: Daca ai avut un cont mai demult si nu te-ai mai logat de peste 14 zile, contul tau s-a sters automat", #CUSTOM nr zile

              "ver0ERR03" => "ai mai evaluat aceasta pagina, se poate o singura data",
              "verERR03" => "Acest formular de examen a fost deja evaluat",
              "regERR03" => "ai mai evaluat aceasta pagina, se poate o singura data",
              "admERR03" => "identity failed, logged.",
              "tugERR03" => "authentication fail, logged.",
              "ttERR03" => "cuvinte si taguri interzise",

              "authERR04" => "Autentificarea blocata pentru o perioada de 5 minute pentru incercari repetate cu credentiale incorecte. Incercati din nou dupa expirarea periodei de penalizare.",
              "genERR04" => "server congestionat",
              "ver0ERR04" => "primire de  date corupte, inregistrata in log.",
              "regERR04" => "primire de  date corupte, inregistrata in log.",
              "admERR04" => "funny state",

              "ttERR04" => "test depistare boti",
 
              "authERR05" => "Autentificare imposibila cu credentialele furnizate",

              "ver0ERR05" => "primire de  date corupte, inregistrata in log.",
              "verERR05" => "primire de  date corupte, inregistrata in log.",
              "regERR05" => "primire de  date corupte, inregistrata in log.",
              "admERR05" => "admin token revoke request executed",
              "ttERR05" => "Formularul a expirat",

              "authERR06" => "Autentificarea blocata pentru o perioada de 5 minute pentru incercari repetate cu credentiale incorecte. Incercati din nou dupa expirarea periodei de penalizare.",




              "admERR06" => "admin token revoked.",

              "tugERR06" => "admin token revoked.",
              "ttERR06" => "Nu ai completat nickname si/sau textul, da inapoi si completeaza",

              "authERR07" => "examyo system error, logged for admin",

              "genERR07" => "server congestionat",



              "ttERR07" => "hmm",




              "verERR08" => "tentativa de frauda, inregistrata in log",



              "genERR09" => "Aceasta cerere nu este recunoscuta de sistem, cererea a fost logata",
              "verERR09" => "Aceasta cerere nu este recunoscuta de sistem, cererea a fost logata",


              "genERR10" => "actiune ilegala, inregistrata in log",


              "genERR12" => "actiune ilegala, inregistrata in log",


              "genERR15" => "formularul a fost deja folosit odata",

              "genERR17" => "actiune ilegala, inregistrata in log",
              "genERR18" => "actiune ilegala, inregistrata in log",

#special treatment
              "ERR19" => "error not displayed",
              "ERR20" => "silent discard"	
                );
#textul de turnat in logfile, interne
my %int_errors= (
  

              "ERR00" => "unknown/unspecified",

              "authERR01" => "not exactly 2 pairs received",            #test ok
              "chkERR01" => "junk input", 
              "ttERR01" => "illegal get_type, not 0/1",    #test ok


              "genERR01" => "transaction sha1 authenticity failed",   #untested
              "ver0ERR01" => "transaction id has been tampered with, sha1 mismatch",    #test ok
              "verERR01" => "transaction id has been tampered with, sha1 mismatch", #test ok
              "regERR01" => "transaction id has been tampered with, sha1 mismatch",    #test ok
              "admERR01" => "token has been tampered with, sha1 mismatch",    #test ok
              "tugERR01" => "token has been tampered with, sha1 mismatch",    #test ok
              "ttERR07" => "submitted transaction has tampered MAC",




              "authERR02" => "2 pairs but not login and passwd",        #test ok

              "genERR02" => "transaction timestamp expired, normally not logged",            
              "ver0ERR02" => "timestamp was already expired, normally not logged",     #test ok
              "verERR02" => "timestamp was already expired", #test ok
              "regERR02" => "timestamp was already expired",           #test ok
              "admERR02" => "token timestamp expired",           #test ok
              "tugERR02" => "untampered but timestamp expired",           #test ok

              "ttERR02" => "trid_type nu e 0 sau 1, ciudat",           #test ok
              "admERR04" => "funny state",
              "authERR07" => "examyo system error, should never occur, weird hlr_class:",


              "authERR03" => "cont inexistent sau expirat",             #test ok
              "authERR06" => "3xfailed authentication for existing user",


              "ver0ERR03" => "good transaction but already used",             #test ok
              "regERR03"  => "good transaction but already used",             #test ok
              "verERR03" => "exam already used", #normally not logged
              "ttERR05" => "form expired",
              "genERR15" => "transaction id already used, normally not logged",

              "admERR03" => "token is sha1, live, but not admin token",             #test ok
              "tugERR03" => "good transaction but not an admin token",             #test ok

              "ttERR03" => "cuvinte ilegale",             #test ok


              "ver0ERR04" => "undef transaction id",
              "regERR04"  => "undef transaction id",



              "ttERR04" => "humanity test failed",

              "authERR05" => "normally not logged, we should just count them somewhere",
              "authERR04" => "normally not logged",


              "ver0ERR05" => "unstructured transaction id",
              "verERR05" => "unstructured transaction id",
              "regERR05" => "unstructured transaction id",
              "ttERR08" => "unstructured transaction",
              "ttERR08" => "unstructured transaction",
              "genERR17" => "received trid is undef",
              "genERR18" => "received trid is destruct",


              "admERR05" => "admin token revoke request ok",



              "admERR06" => "admin token revoked",
              "tugERR06" => "admin token revoked",

              "ttERR06" => "no payload",




#dienice("authERR10",2,\"$! $^E $?");
# err when opening file
              "gen0ERR02" => "cannot open file",
              "gen0ERR01" => "cannot open file",   
              "authERR10" => "cannot open file",
              "ver0ERR07" => "cannot open file",
              "chkERR06"  => "cannot open file",
              "genERR06"  => "cannot open file",
              "genERR13"  => "cannot open file",
              "genERR14"  => "cannot open file",
              "genERR03"  => "cannot open file",
              "genERR05"  => "cannot open file",
              "ver0ERR06" => "cannot open file",
	      "verERR06"  => "cannot open file",
              "regERR06"  => "cannot open file",
              "tugERR04"  => "cannot open file",
              "authERR08" => "cannot open file",

#err when closing file
              "genERR08"  => "cannot close file",
              "genERR16"  => "cannot close file",
              "genERR11"  => "cannot close file",
	      "authERR09" => "cannot close file",
              "ver0ERR08" => "cannot close file",
              "verERR07"  => "cannot close file",
              "regERR07"  => "cannot close file",
              "chkERR07"  => "cannot close file",
              "genERR04"  => "cannot close file",

#err when creating file
              "genERR07" => "fail create new hlrfile",

 #altceva
              "verERR08" => "cheating attempt",


              "genERR09" => "good and unexpired received trid but not in tridfile. Under attack?",
              "verERR09" => "good and unexpired received trid but not in tridfile. Under attack?",


              "genERR10" => "from wrong pagecode invoked generation of exam",


              "genERR12" => "wrong clearance level to request this exam",





#special treatment
              "ERR19" => "silent logging(if $counter>0), not displayed",
	      "ERR20" => "silent discard,(logged only if $counter>0)"
                );


#if commanded, write errorcode in cheat_file
if($counter > 0)
{
# write errorcode in cheat_file

# count the number of lines in the db_tt by counting the '\n'
# open read-only the db_tt
my $CountLines = 0;
my $filebuffer;
#TBD - flock to be analysed if needed or not on the read-only count
           open(DBFILE,"< db_tt") or die "Can't open db_tt";
           while (sysread DBFILE, $filebuffer, 4096) {
               $CountLines += ($filebuffer =~ tr/\n//);
           }
           close DBFILE;

#CUSTOM limit db_tt writing to max number of lines (4 lines per record) 
if($CountLines < 200) #CUSTOM max number of db_tt lines (200/4=50 records)
{
#ACTION: append cheat symptoms in cheat file
open(cheatFILE,"+< db_tt"); #open logfile for appending;
flock(cheatFILE,2);		#LOCK_EX the file from other CGI instances
seek(cheatFILE,0,2);		#go to the end
#CUSTOM
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: %s\<br\>  %s: %s \<br\> UTC Time: %s\<br\>  Logged:%s\n\n",$filename,$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
} #.end max number of lines
} #.end $counter>0

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
print qq!v 3.2.7\n!; #version print for easy upload check
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

#----100%------subrutina generare random number
# intoarce numar intre 0 si $max-1
sub random_int($)
	{
	
	my ($max)=@_;

       return int(rand($max));
	}

#----- don't know what for, but it should return something probably
1;
