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

#  tool_checker2.cgi v.3.3.0 (c)2007-2017 Francisc TOTH
#  Status: working
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania

#ch 3.3.0 junk input whitelist updated
#ch 3.0.5 curricula coverage sourced from strip.pl
#ch 3.0.4 minor comments changed
#ch 3.0.3 minor hardening for deregulated db
#ch 3.0.2 eliminate hamxam
#ch 3.0.1 hiding the v3code for good
#ch 3.0.0 (wrongly)hiding the v3code
#ch 0.0.f displaying deregulated databases
#ch 0.0.e s-a insensibilizat la  continutul URL-ului; Sa faca drop fara raspuns inca nu am reusit
#ch 0.0.d <title> changed to 'Probleme si Rezolvari' 
#ch 0.0.c solve tt39  colors changed so eyes can rest
#ch 0.0.b solve tt34-2, ANC renamed to ANCOM
#ch 0.0.a solve tt34, ANRCTI renamed to ANC
#ch 0.0.9 solve tt29, the part related to databases


use strict;
use warnings;


my $get_buffer; #intrarea
my $get_filename; #hamquest database filename
my $curricula; #associated curricula file from 1st line of database file
my $counter; #counterul 0..n al liniei unei inregistrari
my $reg; #numarul inregistrarii curente
my $rasp; #raspunsul corect al intrebarii
my $fline; #linia de fisier
my @splitter; #taietorul de v3code
my %progcodes=(); #hash of codes from curricula(keys); list of v3 codes for each chapter key
my $v3code;
my $array_size; #used to store coverage of curricula
sub dienice;


$get_buffer=$ENV{'QUERY_STRING'};

if (defined($get_buffer)) {   #eliminate possibility of void input

if($get_buffer =~ m/((db_{1}(op|legis){1}(1|2|3|4){1}$){1}|(db_{1}(ntsm){1}[4]{0,1}$){1}|(db_{1}tech{1}(1|2|3){1}$){1})/)
       {$get_filename = $1;}
       else {$get_filename = "";}

####open hamquest file
if($get_filename ne "") { #eliminate the possibility of input without filename

if(open(INFILE,"<", $get_filename)) { #open the question file


#flock(INFILE,1);		        #LOCK_SH, file can be read

seek(INFILE,0,0);			#goto begin of db file

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>Probleme si Rezolvari: $get_filename</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="#E6E6FA" text="black" link="blue" alink="blue" vlink="blue">\n!;

print qq!<font color="blue">v.3.3.0</font>\n<br>\n!;

print qq!<i>Aceasta este o afisare a bazelor de date folosite de programul SimEx, un simulator de examen de radioamatori<br>Acest program este un software gratuit, poate fi distribuit/modificat in termenii licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in versiunea 2 sau intr-o veriune ulterioara.<br>Programul, intrebarile si raspunsurile sunt distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio garantie, sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii.<br>In distributia programului SimEx trebuie sa gasiti o copie a licentei GNU GPL, iar daca nu, ea poate fi descarcata gratuit de pe pagina <a href="http://www.fsf.org" target="_new">http://www.fsf.org</a><br>Textul intrebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL, modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind permisa. Acest lucru deriva din faptul ca ANCOM este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.</i><br>\n!;

#first line read
$fline=<INFILE>;
chomp($fline);
@splitter= split(/<\/{0,1}curricula>/,$fline);
$curricula=$splitter[1]; #we determined curricula filename


print qq!<font color="blue">$fline</font>\n<br>\n!; #print file version

#establish the v3 hash
open(PRFILE,"<", "$curricula") || print "can't open $curricula \n";
seek(PRFILE,0,0);
while($fline=<PRFILE>)
{
    if($fline =~ /^[0-9]{2,}[a-z]{0,}&/) #v3 code
     {
       @splitter = split(/&/,$fline);
       #print qq!<b>$splitter[0] </b>!; #debug
       %progcodes = (%progcodes,$splitter[0],[]); #each v3 chapter key gets reference to an array  
     }
}

#$fline=<INFILE>;       #we DO NOT read the number of records, don't fit to patterns, so it's not displayed
$counter = 15;
print qq!<hr>\n!;

#parcurgi fisierul
while ($fline = <INFILE>)
{
chomp($fline);				 #cut <CR> from end

if ($fline =~ m/^##[0-9]+#$/)
                        {
                        print qq!$fline\n<br>\n!;
                        $counter = 0;
			$rasp = 'f';
			}

elsif ($counter == 0)
       {
         if($fline =~ m/^[a-d]$/ )
           {
          
	   $rasp=$fline;
	   $counter = 1;
	   }

      else {$counter = 16; }
       }
    
elsif( $counter == 1)
{

if($fline =~ m/^[0-9]{2,3}[A-Z]{1}[0-9]{2,}[a-z]?~&/) #v3 code
   {

   @splitter = split(/~&/,$fline);
   print qq!$splitter[1]<br>\n!; #tiparim linia intrebarii cu v3 "pierdut"
   #putem refolosi @splitter la nevoie

   #codul v3 il bagam in hash-list daca se poate, pentru coverage
   $v3code = $splitter[0];
   @splitter = split(/[A-Z]{1}/,$v3code);
  if(defined($progcodes{$splitter[1]})) #daca exista subcapitol pt acest v3code
   {
   push(@{$progcodes{$splitter[1]}},$v3code); #add v3 to array
   #print qq!array $splitter[1]: @{$progcodes{$splitter[1]}}<br>!; #debug
   } #if defined
  } #if fline has v3 code

else {print qq!$fline<br>\n!;} #has no v3 code, print full question

$counter = 2;
 }

elsif (( $counter == 2) || ($counter == 8))
{
 if($fline =~ m/(jpg|JPG|gif|GIF|png|PNG|null){1}/)
          {      
	my @linesplit;
	@linesplit=split(/ /,$fline);
        if(defined($linesplit[1])) 
	 	{
	 	print qq!<br><center><img src="http://localhost/shelf/$linesplit[0]", width="$linesplit[1]"></center><br>\n!;
                }                     
     	  if ($counter < 3) {$counter = 3;}
       	  else {$counter = 9;}
	 }
 else {$counter = 17; }

}


elsif( $counter == 3) 
 {
     print qq!<form action="#">\n!;
if ($rasp eq 'a' ) {print qq!<dd><input type="checkbox" value="x" name="y" checked="y" >$fline\n!;}
              else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline\n!;}
        
    $counter = 4;


 if ($rasp eq 'f') { $counter =18;}

  }


elsif( $counter == 4) 
{
if ($rasp eq 'b' ) {print qq!<dd><input type="checkbox" value="x" name="y" checked="y" >$fline\n!;}
              else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline\n!;}
       $counter = 5;
}

elsif( $counter == 5) 
{
	if ($rasp eq 'c' ) {print qq!<dd><input type="checkbox" value="x" name="y" checked="y" >$fline\n!;}
        else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline\n!;}

       	$counter = 6;
}


elsif( $counter == 6) 
{
if ($rasp eq 'd' ) {print qq!<dd><input type="checkbox" value="x" name="y" checked="y" >$fline\n!;}
              else {print qq!<dd><input type="checkbox" value="x" name="y" disabled="y">$fline\n!;}
print qq!</form>\n<br>\n!;
       $counter = 7;
                      }


elsif($counter == 7) 
{
  print qq!<font size="-1"><i>(Contributor: $fline)</i></font><br>\n!;
  $counter = 8;
			 }


elsif($counter ==  9) 
 {
	unless ($fline eq "") {  print qq!<br>\n$fline<br>\n!;} 
	$counter = 10; 
        if ($fline =~ /^[a-d]$/) { $counter = 19; }
 }


elsif($counter ==  10) 
 {
	unless ($fline eq "") 
          { print qq!<font size="-1"><i>(rezolvare: $fline)</i></font><br>\n!;} 
            print qq!<hr>\n!;
	    $counter = 11; 

       if ($fline =~ /^[a-d]$/) { $counter = 20; }
 }

if($counter > 15) 
{
print qq!<font color="red">EROARE in baza de date, ar trebui sa anuntati adminul cod eroare: $counter</font><br><hr>\n!;
$counter = 15;
}


}

#here we intend to print curricula coverage
print qq!<font color="blue">NOU: Afisarea acoperirii programei, pe subcapitole, cu intrebari din baza de date.</font><br><br>\n!;
print qq!<font color="blue">Valorile sunt calculate, nu completate de mana, deci fara trucuri depasite cu productivitatea la hectar.<br><br>Tineti cont ca in unele cazuri, de ex. radiotehnica pentru clasa I si II la subcapitolul Legea lui Ohm si altele similare e normal sa nu fie intrebari, ANCOM specifica intrebari de dificultate sporita. In alte cazuri nu sunt intrebari inca, ele nu cresc singure, trebuie facute, asa ca accept propuneri cu placere.</font><br>\n<br>\n!;

seek(PRFILE,0,0); #rewind curricula, we intend to print now
while($fline=<PRFILE>)
{
   if($fline =~ /^[0-9]{2,}[a-z]{0,}&/) #sub-v3 code
    {
    @splitter = split(/&/,$fline);
    $array_size = @{$progcodes{$splitter[0]}};
    print qq!<b><font color="blue">$array_size</font></b>$splitter[1]<br>!; #only counting
    }
    else  #line without sub-v3 code
    {
    print qq!$fline<br>!;
    }
}
close (PRFILE) || dienice("ERR07",1,\"null");


print qq!</body>\n!;
print qq!</html>\n!;

close (INFILE) || dienice("ERR07",1,\"null");

} #close file
else  {dienice("ERR06",1,\$get_filename);} #else the case when correct filename could not be opened

}
else {dienice("ERR01",1,\"junk input");} #else the case when input was not void, but some junk

}
else {dienice("ERR01",1,\"void URL");} #else the case when URL input was void

#-------------------------------------
# treat the "or die" and all error cases
#how to use it
#$error_code is a string, you see it, this is the text selector
#$counter: if it is 0, error is not logged. If 1..5 = threat factor
#reference is the reference to string that is passed to be logged.
#ERR19 and ERR20 have special handling

sub dienice
{
my ($error_code,$counter,$err_reference)=@_; #in vers. urmatoare counter e modificat in referinta la array/string

my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "primire de  date corupte, inregistrata in log.",
              "ERR02" => "reserved",
              "ERR03" => "reserved",
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "server congestion",
              "ERR07" => "server congestion",
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
              "ERR01" => "junk input",   
              "ERR02" => "reserved",      
              "ERR03" => "reserved",   
              "ERR04" => "reserved",
              "ERR05" => "reserved",
              "ERR06" => "cannot open file",
              "ERR07" => "cannot close file",
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
printf cheatFILE "\<br\>reported by: tool_checker2.cgi\<br\>  %s: %s \<br\> UTC Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
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
