
#Version v 3.3.2


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
print qq!Săcele, Brașov, România (YO) then released to the whole radio amateur community.\n!;
print qq!\n!;
print qq!Prezentul simulator de examen împreună cu formatul bazelor de întrebări, rezolvările problemelor, manual de utilizare,\n!; 
print qq!instalare, SRS, cod sursă și utilitarele aferente constituie un pachet software gratuit care poate fi distribuit/modificat în \n!;
print qq!termenii licenței libere GNU GPL, așa cum este ea publicată de Free Software Foundation în versiunea 2 sau într-o versiune \n!;
print qq!ulterioară. Programul, întrebările și răspunsurile sunt distribuite gratuit, în speranța că vor fi folositoare, dar fără nicio \n!;
print qq!garanție, sau garanție implicită, vezi textul licenței GNU GPL pentru mai multe detalii. Utilizatorul programului, \n!;
print qq!manualelor, codului sursă și utilitarelor are toate drepturile descrise în licența publica GPL.\n!;
print qq!În distribuția de pe https://github.com/6oskarwN/Sim_exam_yo trebuie să găsiți o copie a licenței GNU GPL, de asemenea \n!;
print qq!și versiunea în limba română, iar dacă nu, ea poate fi descărcată gratuit de pe pagina http://www.fsf.org/\n!;
print qq!Textul întrebărilor oficiale publicate de ANCOM face excepție de la cele de mai sus, nefăcând obiectul licențierii GNU GPL, \n!;
print qq!copyrightul fiind al statului român, dar fiind folosibil în virtutea legii 544/2001 privind liberul acces la informațiile \n!;
print qq!de interes public precum al legii 109/2007 privind reutilizarea informațiilor din instituțiile publice.\n!;
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
#sub compute_mac {

#use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
#  my ($message) = @_;
#  my $secret = '80b3581f9e43242f96a6309e5432ce8b'; #development secret
#  hmac_sha1_hex($message,$secret);
#} #end of compute_mac

#-------------------------------------
sub compute_mac {
use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
my $secret='80b3581f9e43242f96a6309e5432ce8b'; #development secret.
# the name of trusted connection must be string that does not resemble a 6-digit hex code
my %trusted_connection = (
                          'yo6own' => '80b3581f9e43242f96a6309e5432aaaa', #sha1 secret trusted key for yo6own
                          'testry' => '80b3581f9e43242f96a6309e5432aaaa' #sha1 secret trusted key for testry
                          );
  my ($message) = @_;
  my @splitter = split(/_/,$message);
  if(defined($trusted_connection{$splitter[0]})) {$secret = $trusted_connection{$splitter[0]}};
  hmac_sha1_hex($message,$secret);
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

my $errorText = $$err_reference; #still XSS possible, unsecure content, process later
my $timestring=gmtime(time);

my($package,$filename,$line)=caller;

#textul pentru public
my %pub_errors= (

              "ERR00" => "error: unknown/unspecified",
#astea cu cannot open file, toate
              "ERR01_op" => "Server congestionat, încearcă în câteva momente",
#astea cu cannot close file, toate
              "ERR02_cl"  => "Server congestionat, încearcă în câteva momente",

#unprocessed


              "admERR03" => "identity failed.",
              "tugERR03" => "authentication fail",
              "authERR03" => "Autentificare imposibilă cu credențialele furnizate.<br><br><small>ATENȚIE: Dacă ai avut un cont mai demult și nu te-ai mai logat de peste 14 zile, contul tău s-a șters automat</small>", #CUSTOM nr zile
              "authERR04" => "Autentificare imposibilă cu credențialele furnizate.<br><br><small>ATENȚIE: Dacă ai avut un cont mai demult și nu te-ai mai logat de peste 14 zile, contul tău s-a șters automat</small>", #CUSTOM nr zile
              "authERR05" => "Autentificare imposibilă cu credențialele furnizate.<br><br><small>ATENȚIE: Dacă ai avut un cont mai demult și nu te-ai mai logat de peste 14 zile, contul tău s-a șters automat</small>",  #CUSTOM nr zile

              "ERR01"  =>  "primire de  date nepermise. E important de exemplu sa nu includeti tag-uri html <...> .", #this should remain

              "ver0ERR05" => "primire de  date corupte",
              "verERR05" => "primire de  date corupte",
              "regERR05" => "primire de  date corupte",
              "verERR08" => "trimitere de date corupte",

              "ERR02" => "timpul alocat paginii a expirat", #this should remain

              "ERR03" => "Această pagină a fost deja evaluată, s-a consumat.",
              "ver0ERR03" => "ai mai evaluat această pagină, se poate o singură dată",
              "verERR03" => "Acest formular de examen a fost deja evaluat",
              "regERR03" => "ai mai evaluat această pagină, se poate o singură dată",
              "genERR15" => "formularul a fost deja folosit o dată",

              "admERR04" => "funny state",

              "ttERR04" => "test depistare boți",
 


              "admERR05" => "admin token revoke request executed",
  

              "authERR06" => "Autentificarea blocată pentru o perioadă de 5 minute pentru încercări repetate cu credențiale incorecte. Încercați din nou după expirarea perioadei de penalizare.",




              "admERR06" => "token used or revoked",
              "tugERR06" => "admin token revoked.",

              "ttERR06" => "Nu ai completat nickname și/sau textul, poți da înapoi cu Back să completezi",

              "authERR07" => "examyo system error",

              "genERR07" => "server congestionat",






              "genERR09" => "Această cerere nu este recunoscută de sistem",
              "verERR09" => "Această cerere nu este recunoscută de sistem",


              "genERR10" => "acțiune ilegală",
              "genERR12" => "acțiune ilegală",
              "genERR17" => "acțiune ilegală",
              "genERR18" => "acțiune ilegală",

#special treatment
              "ERR19" => "error not displayed",
              "ERR20" => "silent discard"	
                );
#textul de turnat in logfile, interne
my %int_errors= (
  

              "ERR00" => "unknown/unspecified",
#astea cu cannot open file, toate
              "ERR01_op" => "cannot open file",
#astea cu cannot close file, toate
              "ERR02_cl"  => "cannot close file",
              "genERR07" => "fail create new hlrfile",


              "ERR01" => "messy input",

              "ERR02" => "transaction or token timestamp expired",
 
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


              "ttERR04" => "humanity test failed",

              "authERR05" => "wrong passwd, normally not logged",
              "authERR04" => "auth blocked 5 min, normally not logged",


              "ver0ERR05" => "unstructured transaction id",
              "verERR05" => "unstructured transaction id",
              "regERR05" => "unstructured transaction id",
              "ttERR08" => "unstructured transaction",
              "genERR17" => "received trid is undef",
              "genERR18" => "received trid is destruct",


              "admERR05" => "admin token revoke request ok",



              "admERR06" => "admin token revoked",
              "tugERR06" => "admin token revoked",

              "ttERR06" => "no payload",






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
#elliminate XSS threat from $errorText
 $errorText =~ s/(<|\%3C)/\&lt\;/g; #replace before write
 $errorText =~ s/(>|\%3E)/\&gt\;/g; #replace before write

#CUSTOM
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: %s\<br\>  %s: %s \<br\> UTC Time: %s\<br\>  Logged:%s\n\n",$filename,$error_code,$int_errors{$error_code},$timestring,$errorText; #write error info in logfile
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
print qq!<meta charset=utf-8>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
ins_gpl(); #this must exist
print qq!v 3.3.2\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;
                              }
}

unless($error_code eq 'ERR19') #ERR19 is silent logging, no display, no exit()
         {
           exit(); #exiting for all errors except ERR19
         }

} #end sub

#----100%------subrutina generare random number
# intoarce numar intre 0 si $max-1
sub random_int($)
	{
	
	my ($max)=@_;

       return int(rand($max));
	}

#----- don't know what is this 1; for, but it should return something probably 
1;
