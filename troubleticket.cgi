#!c:\Perl\bin\perl

# Prezentul simulator de examen impreuna cu formatul bazelor de intrebari, rezolvarile problemelor, manual de utilizare,
# instalare, SRS, cod sursa si utilitarele aferente constituie un pachet software gratuit care poate fi distribuit/modificat 
# in termenii licentei libere GNU GPL, asa cum este ea publicata de Free Software Foundation in versiunea 2 sau intr-o 
# versiune ulterioara. 
# Programul, intrebarile si raspunsurile sunt distribuite gratuit, in speranta ca vor fi folositoare, dar fara nicio garantie,
# sau garantie implicita, vezi textul licentei GNU GPL pentru mai multe detalii.
# Utilizatorul programului, manualelor, codului sursa si utilitarelor are toate drepturile descrise in licenta publica GPL.
# In distributia de pe https://github.com/6oskarwN/Sim_exam_yo trebuie sa gasiti o copie a licentei GNU GPL, de asemenea si versiunea 
# in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/
# Textul intebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL, 
# modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind este permisa. Acest lucru deriva 
# din faptul ca ANCOM este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.

# This program together with question database formatting, solutions to problems, manuals, documentation, source code and
# utilities is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 of the License, or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without any implied warranty. 
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this software distribution; if not, you can
# download it for free at http://www.fsf.org/ 
# Questions marked with ANCOM makes an exception of above-written, as ANCOM is a romanian public authority(similar to FCC in USA)
# so any use of the official questions, other than in Read-Only way, is prohibited. 

# (c) YO6OWN Francisc TOTH, 2008 - 2018

#  troubleticket.cgi v 3.0.c
#  Status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  Made in Romania


# ch 3.0.d new transaction code simplified with epoch_time; timestamp_expired();
# ch 3.0.c Admin: changed to YO6OWN
# ch 3.0.b the three stage of a ticket are clearly displayed [Nou][Vazut ...][Rezolvat]
# ch 3.0.a patch in a mailer when new complaints are registered; untested since no mail account possible; hashed.
# ch 3.0.9 'ativan' added in the deny list, banned by awardspace.com
# ch 3.0.8 fixed POST that comes from special link in sim_verx.cgi in order to preserve &specials; and "overline"
# ch 3.0.7 <form> in <form> makes that blank record is saved if calculus is good but abandon is hit 
# ch 3.0.6 change window button to method="link" button  
# ch 0.1.5 GET changed to POST - devel
# ch 0.1.4 link to forumer eliminated by forumer migration to yuku.
# ch 0.1.3 link 404 catre forumer, corectat
# ch 0.1.2 linkuri aiurea catre kxp_index, corectat
# ch 0.1.1 made case-insensitive match for legal() dictionary and added 'proxy' to list of banned words - for sotw
# ch 0.1.0 older tickets not available any more as ZIP, but on the forum.
# ch 0.0.f fixed tt34-2 ANC renamed as ANCOM
# ch 0.0.e fixed tt34 ANRCTI renamed as ANC
# ch 0.0.d fixed trouble ticket 26
# ch 0.0.c solved troubleticket tt029
# ch 0.0.b troubleticket additional helping message 
# ch 0.0.a new feature added, online FR
# ch 0.0.9 new feature added without request - for internal ticket, nick == eXAM login
# ch 0.0.8 solved troubleticket20
# ch 0.0.7 links changed from white to red
# ch 0.0.6 troubleticket 19 solved
# ch 0.0.5 troubleticket 17 solved: Changed the targets of Abandon and OK - made context-sensitive
# ch 0.0.4 End of coding
# ch 0.0.3 Guestbook interface part1 implemented
# ch 0.0.2 human ID system changed to arithmetical operation
# ch 0.0.1 coding started

#$=====================================================================
use strict;
use warnings;

sub ins_gpl;                 #inserts a HTML preformatted text with the GPL license text

my $get_type; #0 (anonymous) or 1(nick and prefilled) -gen fault report form  ELSE - gen guestbook form;
my $get_nick; #nick for the guy who is writing
my $get_text; #submitted text
my $get_complaint; #the additional text inserted by user only when $get_type=1
my $get_rating; #rating for site in guestbook, 1 to 5
my $get_answer; #authentication answer
my $get_trid; #transaction ID
my $trid; #transaction ID for anonymous, similar like for an exam
my $newtrid;
#my $buffer;
my @dbtt;   #this is the slurp variable

#### mailer patch v.3.0.a #############
#my $mailprog = '/usr/local/bin/sendmail'; #this is specific to my hoster
## Change the location above to wherever sendmail is located on your server.
#my $admin_email="curierul\@examyo.scienceontheweb.net";
## Change the address above to your e-mail address. Make sure to KEEP the \
#my $target_email="yo6own\@yahoo.com";
## Change the address above to your e-mail address. Make sure to KEEP the \
#### .end of mailer patch v 3.0.c #####


#intermediate variables
my $get_aucpair;    #$question_auc:$answer_auc
my $question_auc;
my $answer_auc;

my $fline; #var used to read a file line by line
my $fline2;
#functii
sub legal; #intoarce 0 daca e text obscen,ilegal si 1 daca e legal
sub aucenter(); #intoarce un string de tipul "text operatie:result"
#BUG: there is an overlap for the actions of 2 functions below:
sub new_transaction; #face transactionlist refresh; adauga o tranzactie si intoarce transaction ID;
sub get_transaction($); #daca tranzactia nu exista intoarce string vid; daca exista, sterge linia din fisier si intoarce un string care e chiar linia de tranzactie din fisier;
sub trid_refresh; #cleans expired transactions
sub defeat; #prints a defeat page > will be replaced by dienice()
sub dienice; 
sub addrec; #adauga o inregistrare in db_troubleticket
#BLOCK: Input
{
my $buffer;
my @pairs;
my $pair;
my $stdin_name;
my $stdin_value;


# Read input, POST or GET
  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/; #facem totul upper-case
  if($ENV{'REQUEST_METHOD'} eq "POST")
         { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data 
         }
  else  { $buffer = $ENV{'QUERY_STRING'}; #GET data for backwards-compatibility
   
        }

@pairs=split(/&/,$buffer ); #split the pairs in input

foreach $pair(@pairs) {
($stdin_name,$stdin_value) = split(/=/,$pair);

$stdin_value=~ tr/+/ /; #ideea e de a inlocui la loc + cu space
$stdin_value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char 

#temporarily out
# DEBUG DEBUG
# 
#$stdin_value=~ s/<*>*<*>//g; #regexp de rafinat: taie toate html 
#tagurile din orice input field #asta ne afecteaza la raportarea 
#erorilor cu formule </span> <sub> <sup> 

#$stdin_value=~ s/<(\s*\/?[^span]*[^>]*\s*)>//g; #nu ma intereseaza sa  elimin html taguri ? <bold, etc...>
#$stdin_value=~ s/<\s*\/?[^b]*>//g; 

##end of DEBUG DEBUG 

if($stdin_name eq 'type') { $get_type=$stdin_value;}
elsif($stdin_name eq 'nick'){$get_nick=$stdin_value;}
elsif($stdin_name eq 'subtxt'){$get_text=$stdin_value;}
elsif($stdin_name eq 'complaint'){$get_complaint=$stdin_value;}
elsif($stdin_name eq 'rating'){$get_rating=$stdin_value;}
elsif($stdin_name eq 'answer'){$get_answer=$stdin_value;}
elsif($stdin_name eq 'transaction'){$get_trid=$stdin_value;}

                        } #end foreach pair

} #end input block

####
##DEVEL PRINT only DEBUG DEBUG
#  print qq!Content-type: text/html\n\n!; #DEBUG, should not exist
#  print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; #debug, normally not exist
#print qq!<html>\n!; #debug only
#print qq!<head>\n<title>debug title</title>\n</head>\n!; #debug only
#print qq!<body>\n!; #debug only
#print qq!$buffer\n!; #debug only
#print qq!$get_type\n!; #debug only
#print qq!$get_complaint\n!; #debug only

#print qq!ce avem dupa primul hex-to-char : $get_text\n!; #debug only

#print qq!</body>\n!;
#print qq!</html>\n!;






#########end of devel

#generate the form, if $get_type is 0 or 1 or else
if (defined $get_type) #it means we have a first call
 {
  if($get_type eq 0) #external trouble ticket call
  {
#call aucenter() that will generate human question and answer
 my $get_aucpair=aucenter();

 #se splituieste rezultatul lui AUC in intrebare si raspuns
($question_auc,$answer_auc)=split (/:/, $get_aucpair);

 #se apeleaza new_transaction=add_transaction(type=1,AUC_result)
 $newtrid=new_transaction(0,$answer_auc);
# printf "new transaction: +%s+\n",$newtrid; #debug only

  print qq!Content-type: text/html\n\n!;
  print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
  print qq!<html>\n!;
  print qq!<head>\n<title>colectare erori si sugestii</title>\n</head>\n!;
  print qq!<body bgcolor="#228b22" text="#7fffd4" link="blue" alink="blue" vlink="red">\n!;
  ins_gpl();
  print qq!<font size="-1">v 3.0.c</font>\n!; #version print for easy upload check
  print qq!<br>\n!;
 #se genereaza formularul integrand $newtrid si $question_auc
  print qq!<center>\n<b>sistem de colectie erori</b>\n!;
  print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi" method="post">\n!;
  print qq!<table width="90%" border="0">\n!;  #debug, border="0" originally

#ACTION: inserare transaction ID in pagina HTML
{
  #my $extra=sprintf("%+06X",$trid); 
  print qq!<tr>\n!;
  print qq!<td colspan="3">\n!;
  print qq!<input type="hidden" name="transaction" value="$newtrid">\n!;
  print qq!</td>\n!;
  print qq!</tr>\n!;
  }

  print qq!<tr>\n!;
  print qq!<td colspan="3" align="left">\n!;
  print qq!Daca umbli cu ganduri curate, stii ca <font color="yellow">$question_auc</font>  egal !;
  print qq!<input type="text" name="answer" size="8"> (in cifre)<br><br>\n!;
  print qq!</td>\n!;
  print qq!</tr>\n!;

  print qq!<tr>\n!;
  print qq!<td align="left" valign="middle">\n!;
  print qq!<font color="yellow">nickname:</font>!;
  print qq!</td>\n!;
  print qq!<td align="left" colspan="2">\n!;
  print qq!<input type="text" name="nick" size="25">!;
  print qq!</td>\n!;
  print qq!</tr>\n!;

  print qq!<tr>\n!;
  print qq!<td valign="middle" align="left">\n!;
  print qq!<font color="yellow">Mesaj:</font>!;
  print qq!</td>\n!;

  print qq!<td align="left" colspan="2">\n!;
  print qq!<textarea name="subtxt" rows="5" cols="50" wrap="soft"></textarea>!;
  print qq!</td>\n!;
  print qq!</tr>\n!;

  print qq!<tr>\n!;
  print qq!<td valign="top">\n!;
  print qq!<center><INPUT type="submit"  value="Trimite"> </center>\n!;
  print qq!</td>\n!;
  print qq!<td valign="top">\n!;
  print qq!<center><INPUT type="reset"  value="Reset"> </center>\n!;
  print qq!</form>\n!;
  print qq!</td>\n!;

  print qq!<td valign="top">\n!;
  print qq!<form method="link" action="http://localhost/index.html">\n!;
  print qq!<center><INPUT TYPE="submit" value="Abandon"></center>\n!; 
  print qq!</form>\n!;
  print qq!</td>\n!;

  print qq!</tr>\n!;
  print qq!</table>\n!;

#se deschide fisierul cu inregistrari, read-only 
#se parcurge fisierul si se afiseaza toate inregistrarile de tickets
open(ttFILE,"<","db_tt");
seek(ttFILE,0,0);
@dbtt=<ttFILE>;   #we slurp the whole file into an array

print qq!<table border="1" width="90%">\n!;


my $backgnd;
$backgnd="\#d3d3d3";

#se parcurge fisierul de-andoaselea si se afiseaza toate inregistrarile de guestbook
for(my $i=($#dbtt+1)/4;$i>0;$i--)
{
chomp $dbtt[$i*4-3];
if($dbtt[$i*4-3] > 5)     #if it's a troubleticket record
{
if($backgnd eq "\#d3d3d3") {$backgnd="\#ADD8E6";}
else {$backgnd="\#d3d3d3";}
print qq!<tr>\n!;
print qq!<td bgcolor="$backgnd" align="left">\n!;

print qq!<font color="black"><b>$dbtt[$i*4-4]</b></font>&nbsp;!;  #print nick


   if ($dbtt[$i*4-3] eq 6) {print qq!<font color="red">[Nou]</font><font color="grey">=&gt;[Citit de admin]=&gt;[Rezolvat]</font>!;}
elsif ($dbtt[$i*4-3] eq 7) {print qq!<font color="blue">[Citit de admin]</font><font color="grey">=&gt;[Rezolvat]</font>!;}
elsif ($dbtt[$i*4-3] eq 8) {print qq!<font color="green">[Rezolvat]</font>!;}

##doubled
my $toprint = $dbtt[$i*4-2];
$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char #poate aici afecta inainte pe &radic, nu mai e cazul;
$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char #poate aici afecta inainte pe &radic, nu mai e cazul;
#$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char #poate aici afecta inainte pe &radic, nu mai e cazul;

#print qq!<font color="black" size="-1">$dbtt[$i*4-2]</font><br>\n!; #debug: black is orange
print qq!<font color="black" size="-1">$toprint</font><br>\n!; #debug: black is orange

unless ($dbtt[$i*4-1] eq "\n") {
print qq!<font color="blue" size="-1">YO6OWN: $dbtt[$i*4-1]</font><br>!;
                               }
print qq!</td>\n!;
print qq!</tr>\n!;                              
} #.end it's a guestbook record
} #.end for/4
#----------------------

print qq!</table>\n!;

print qq!</center>\n!;

 print qq!</body>\n</html>\n!;
 #se inchide fisierul cu inregistrari
close(ttFILE);
 
  
  }
#end of case when $type=0, new ticket, anonymous.
#start the case of prefilled ticket
  elsif($get_type eq 1) #internal trouble ticket first call
  {
#call humanity check precalculate, ,the AUC
 my $get_aucpair=aucenter();

 #se splituieste rezultatul lui AUC in intrebare si raspuns
($question_auc,$answer_auc)=split (/:/, $get_aucpair);

 #se apeleaza new_transaction=add_transaction(type=1,AUC_result)
 $newtrid=new_transaction(1,$answer_auc);
# printf "new transaction: +%s+\n",$newtrid; #debug only

 #se scrie header html
  print qq!Content-type: text/html\n\n!;
  print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
  print qq!<html>\n!;
  print qq!<head>\n<title>colectare erori si sugestii</title>\n</head>\n!;
  print qq!<body bgcolor="#228b22" text="#7fffd4" link="blue" alink="blue" vlink="red">\n!;
  ins_gpl();
  print qq!<font size="-1">v 3.0.c</font>\n!; #version print for easy upload check
  print qq!<br>\n!;
 #se genereaza formularul integrand $newtrid si $question_auc
print qq!<center>\n<b>sistem de colectie erori</b>\n!;
print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi" method="post">\n!;
print qq!<table width="90%" border="0">\n!;

#ACTION: inserare transaction ID in pagina HTML
{
#my $extra=sprintf("%+06X",$trid);
print qq!<tr>\n!;
print qq!<td colspan="2">\n!;
print qq!<input type="hidden" name="transaction" value="$newtrid">\n!;
print qq!</td>\n!;
print qq!</tr>\n!;
}

print qq!<tr>\n!;
print qq!<td colspan="3" align="left">\n!;
print qq!Daca umbli cu ganduri curate, stii ca <font color="yellow">$question_auc</font>  egal !;
print qq!<input type="text" name="answer" size="8"> (in cifre)<br><br>\n!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td align="left" valign="middle">\n!;
print qq!<font color="yellow">nickname:</font>!;
print qq!</td>\n!;
print qq!<td align="left" colspan="2">\n!;
print qq!$get_nick <input type="hidden" name="nick" value="$get_nick">!; #nick = eXAM login
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td valign="middle" align="left">\n!;
print qq!<font color="yellow">Mesaj:</font>!;
print qq!</td>\n!;


print qq!<td align="left" colspan="2">\n!;

#print qq!$get_text<br>\n!; #debug
print qq!<input type="hidden" name="subtxt" value=\"$get_text\">\n!;
my $toprint=$get_text;
$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char #poate aici afecta inainte pe &radic, nu mai e cazul;
#$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; #transforma %22 in =, %hex to char #poate aici afecta inainte pe &radic, nu mai e cazul;
print qq!$toprint<br>\n!; #debug

print qq!<textarea name="complaint" rows="5" cols="50" wrap="soft">explicatia ta aici</textarea>!;
#print qq!<textarea name="subtxt" rows="5" cols="50" wrap="soft">$get_text</textarea>!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td valign="top">\n!;
print qq!<center><INPUT type="submit"  value="Trimite"> </center>\n!;
print qq!</td>\n!;
print qq!<td valign="top">\n!;
print qq!<center><INPUT type="reset"  value="Reset"> </center>\n!;
print qq!</form>\n!;
print qq!</td>\n!;

print qq!<td valign="top">\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="Abandon"></center>\n!; 
print qq!</form>\n!;
print qq!</td>\n!;

print qq!</tr>\n!;

print qq!</table>\n!;

print qq!</center>\n!;
 #se inchide html
  print qq!</body>\n</html>\n!;
 
  }
# end of type=1, prefilled ticket
#  else #guestbook first call
elsif($get_type eq 2) #guestbook first call
  {
 #se apeleaza AUC
 my $get_aucpair=aucenter();

 #se splituieste rezultatul lui AUC in intrebare si raspuns
($question_auc,$answer_auc)=split (/:/, $get_aucpair);

 #se apeleaza new_transaction=add_transaction(type=2=guestbook,AUC_result)
 $newtrid=new_transaction(2,$answer_auc);
# printf "new transaction: +%s+\n",$newtrid; #debug only


  print qq!Content-type: text/html\n\n!;
  print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
  print qq!<html>\n!;
  print qq!<head>\n<title>colectare erori si sugestii</title>\n</head>\n!;
  print qq!<body bgcolor="#228b22" text="#7fffd4" link="blue" alink="blue" vlink="red">\n!;
  ins_gpl();
  print qq!<font size="-1">v 3.0.c</font>\n!; #version print for easy upload check
  print qq!<br>\n!;
 #se genereaza formularul integrand $newtrid si $question_auc
 print qq!<center>\n<b>Adauga in cartea de oaspeti, toate campurile sunt obligatorii (ai 15 minute)</b>\n!;

 print qq!<form action="http://localhost/cgi-bin/troubleticket.cgi" method="post">\n!;
print qq!<table width="90%" border="0">\n!;
#ACTION: inserare transaction ID in pagina HTML
{
#my $extra=sprintf("%+06X",$trid);
print qq!<tr>\n!;
print qq!<td colspan="2">\n!;
print qq!<input type="hidden" name="transaction" value="$newtrid">\n!;
print qq!</td>\n!;
print qq!</tr>\n!;
}

print qq!<tr>\n!;
print qq!<td colspan="3" align="left">\n!;
print qq!Daca umbli cu ganduri curate, stii ca <font color="yellow">$question_auc</font>  egal !;
print qq!<input type="text" name="answer" size="8"> (in cifre)<br><br>\n!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td align="left" valign="middle">\n!;
print qq!<font color="yellow">nickname:</font>!;
print qq!</td>\n!;
print qq!<td align="left" colspan="2">\n!;
print qq!<input type="text" name="nick" size="25">!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td valign="middle" align="left">\n!;
print qq!<font color="yellow">Comentariu:</font>!;
print qq!</td>\n!;

print qq!<td align="left" colspan="2">\n!;
print qq!<textarea name="subtxt" rows="5" cols="50" wrap="soft"></textarea>!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td colspan="3" align="left">\n!;
#CUSTOM
print qq!Cum vedeti valoarea site-ului:!; #unique and hardcoded question, ugly choice
print qq!<select size="1" name="rating">\n!;

print qq!<option value="0" selected="y">NO COMMENT</option>\n!;
print qq!<option value="1"> o stea(site jalnic)</option>\n!;
print qq!<option value="2"> 2 stele(site mediocru)</option>\n!;
print qq!<option value="3"> 3 stele(nu iese din rand)</option>\n!;
print qq!<option value="4"> 4 stele (cu ceva peste medie)</option>\n!;
print qq!<option value="5"> 5 stele(imi place, mai trec pe aici)</option>\n!;

print qq!</select>\n!;
print qq!</td>\n!;
print qq!</tr>\n!;

print qq!<tr>\n!;
print qq!<td valign="top">\n!;
print qq!<center><INPUT type="submit"  value="Trimite"> </center>\n!;
print qq!</td>\n!;
print qq!<td valign="top">\n!;
print qq!<center><INPUT type="reset"  value="Reset"> </center>\n!;
print qq!</form>\n!;
print qq!</td>\n!;

print qq!<td valign="top">\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="Abandon"></center>\n!; 
print qq!</form>\n!;
print qq!</td>\n!;

print qq!</tr>\n!;
print qq!</table>\n!;


 #se deschide fisierul cu inregistrari, read-only 
open(ttFILE,"<","db_tt");
seek(ttFILE,0,0);
@dbtt=<ttFILE>;   #we slurp the whole file into an array

print qq!<table border="1" width="90%">\n!;


my $backgnd;
$backgnd="\#d3d3d3";

#se parcurge fisierul de-andoaselea si se afiseaza toate inregistrarile de guestbook
for(my $i=($#dbtt+1)/4;$i>0;$i--)
{
chomp $dbtt[$i*4-3];
if($dbtt[$i*4-3] < 6)     #if it's a guestbook record
{
if($backgnd eq "\#d3d3d3") {$backgnd="\#ADD8E6";}
else {$backgnd="\#d3d3d3";}
print qq!<tr>\n!;
print qq!<td bgcolor="$backgnd" align="left">\n!;

print qq!<font color="black"><b>$dbtt[$i*4-4]</b></font>&nbsp;!;  #print nick


for (my $istar=0; $istar < $dbtt[$i*4-3]; $istar++)
{print qq!<IMG src="http://localhost/img/star.gif" WIDTH="15">\n!;
}

print qq!<font color="black" size="-1">$dbtt[$i*4-2]</font><br>\n!;
unless ($dbtt[$i*4-1] eq "\n") {
print qq!<font color="blue" size="-1">YO6OWN: $dbtt[$i*4-1]</font><br>!;
                               }
print qq!</td>\n!;
print qq!</tr>\n!;                              
} #.end it's a guestbook record
} #.end for/4
#----------------------

print qq!</table>\n!;
print qq!</center>\n!;


 #se inchide html
  print qq!</body>\n</html>\n!;
 #se inchide fisierul cu inregistrari
close(ttFILE);
 
  
  } #.end guestbook first call
#to be changed new style logging
  else {dienice("ERR01",1,\"null");} #hacker attack, legal types are 0,1,2
 } #.end first call solve
else #it's not a first call, it must have a transaction-based handling
{
my $errmsg;
if ((defined $get_trid) && (defined $get_nick) && (defined $get_text))
{
my $tridstring;
my $trid_type;
my $trid_answer;

#daca exista, adaugam complaint la text problema
if(defined $get_complaint ) {$get_text = "$get_text (varianta) $get_complaint";}
$get_text=~ s/\r\l\n/<br>/g; #workaround de sfarsit de inlocuire enter cu <br>

$tridstring=get_transaction($get_trid);
if(defined $tridstring) #exista tranzactia
{
($trid_type,$trid_answer)= split (/:/,$tridstring);

if($trid_answer eq $get_answer) 
{
if((legal($get_text) eq 1) and (legal($get_nick)))
{
 my$stringtime=localtime;
 $get_text="<font color=green> ($stringtime) </font><br>$get_text";

if(($trid_type eq 0) or ($trid_type eq 1)) #general troubleticket form 
                    {addrec($get_nick,6,$get_text);
                    print qq!<center>\n!;
                    print qq!<INPUT TYPE="submit" value="OK"><br>\n!;
                    print qq!Hint: Poti sa revii de aici in pagina cu examenul evaluat, pentru a propune o noua modificare, apasand de doua ori butonul de revenire la pagina anterioara <== , al browserului web. \n!;
                    print qq!</center>\n!;
                    print qq!</form>\n!; 
                    print qq!</body>\n</html>\n!;
                    }
elsif(($trid_type eq 2) and (defined $get_rating) )#guestbook
                    {
                    addrec($get_nick,$get_rating,$get_text);
                    print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
                    print qq!</form>\n!; 
                    print qq!</body>\n</html>\n!;
                    } 
    else {$errmsg='input lipsa';
    defeat($errmsg);
    }                  
}
else {
      $errmsg='Va rugam nu folositi cuvinte interzise sau tag-uri HTML';
     defeat($errmsg);
      }
                                                      
}
else {$errmsg="humanity test failed";
      defeat($errmsg);
      }


}
else {$errmsg="form expired";
      defeat($errmsg);
     }


}
else {
      $errmsg="input lipsa access_log";
      defeat($errmsg);
      }
} 
 
 
 
#----100%------subrutina generare random number
sub random_int($)
	{
	
	my ($max)=@_;

       return int rand($max);
	}
#---legalitatea unui string---
#--intoarce 1 daca legal
#--intoarce 0 daca e ilegal
sub legal
{
#lower-case dictionary, enough
my @dictionary=(
              'regexp',  #regular expression allowed
              'sex',
              'porn',    #denied by awardspace.com
              'proxy',   #denied by awardspace.com
              'ativan',    #denied by awardspace.com
              '<\s*[a|A]\s+(href|HREF)'  #good idea not to give link-spammers chances

            );
my $inputstring;
($inputstring)=@_;
my $iter;
my $legall;
$legall=1;#init to legal

foreach $iter (@dictionary)
{
if(lc($inputstring) =~ /$iter/) #forces lower-case comparison lc()
{ $legall=0; #should be the exit from loop, not from if
}

}#.end foreach

 return($legall);

}#.end sub


#------------------------
#Authentication center function
#exemple: dupa 1,2,3 si 4 urmeaza:5
#---TEST IMPLEMENTATION --------
sub aucenter()
{
my $operand1=random_int(20);
my $operand2=random_int(20);
my $suma=$operand1+$operand2;
return("$operand1 adunat cu $operand2:$suma");
}
#================================================================
#================================================================
#--------------------
sub trid_refresh
{
my @tridfile;
my @livelist=();
my @linesplit;
my $i;
#my $j;

open(transactionFILE,"+< tt_transaction");
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array

#ACTION: refresh transaction list, delete expired transactions,
# transaction pattern in file:
# A000D6 0 10 10 23 3 9 118 16 #first 0 is type of trouble 0 = ticket, 16 is result of humanity check


unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
   for($i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
#   chomp $linesplit[8]; #\n is deleted
  if (timestamp_expired($linesplit[2],$linesplit[3],$linesplit[4],$linesplit[5],$linesplit[6],$linesplit[7]) > 0 ) {} #if timestamp expired do nothi$
  else {@livelist=(@livelist, $i);} #not expired, refresh it
  } #.end for

} #.end unless

#else {print qq!file has only $#tridfile lines<br>\n!;}
my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive
#print "extra[0]: $extra[0]<br>\n";#debug

foreach $i (@livelist) {@extra=(@extra,$tridfile[$i]);}
@tridfile=@extra;

#print "trid from extra: $tridfile[0]<br>\n";#debug

#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction file
#print "Tridfile length befor write: $#tridfile \n";
for($i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

close(transactionFILE);


} #.end sub trid_refresh



#---------------------
sub new_transaction
{
my ($type_code,$aucresult)=@_;
my @tridfile;


my @livelist=();
my @linesplit;
my $i;
my $j;
my $hexi;

#open transaction file
open(transactionFILE,"+< tt_transaction");

############################
### Generate transaction ###    
############################
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array


# transaction pattern in file:
# A000D6 0 10 10 23 3 9 118 16 #first 0 is type of trouble 0 = ticket, 16 is result of humanity check

{
unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
{ #.begin unless
   for($i=1; $i<= $#tridfile; $i++)	#check all transactions 
  {
   @linesplit=split(/ /,$tridfile[$i]);
  } #.end for

#else {print qq!file has only $#tridfile lines!;}
#we have now the list of the live transactions
#print "@livelist[0..$#livelist]\n";   
my @extra=();
@extra=(@extra,$tridfile[0]);		#transactionID it's always alive
#print "extra[0]: $extra[0]<br>\n";#debug
#my $j;

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
else { $tridfile[0]=sprintf("%+06X\n",$trid+1);}                #cyclical increment 000000 to 0xFFFFFF

#print qq!generate new transaction<br>\n!;
my $epochTime = time();
#CHANGE THIS for customizing
my $epochExpire = $epochTime + 900; #15 minutes lifetime = 900 sec
my ($exp_sec, $exp_min, $exp_hour, $exp_day,$exp_month,$exp_year) = (gmtime($epochExpire))[0,1,2,3,4,5];

#assemble the trid+timestamp
#my $hexi= "admin_$exp_sec\_$exp_min\_$exp_hour\_$exp_day\_$exp_month\_$exp_year\_"; #adds the expiry timestamp
#compute mac for timestamp 
#my $heximac = compute_mac($hexi); #compute sha1 MessageAuthentication Code
#$hexi= "$hexi$heximac"; #the full transaction id


#print to screen the entry in the transaction list
$hexi= sprintf("%+06X",$trid);
my $entry = "$hexi $type_code $exp_sec $exp_min $exp_hour $exp_day $exp_month $exp_year $aucresult\n";
#print qq!mio entry: $entry <br>\n!; #debug
@tridfile=(@tridfile,$entry); 				#se adauga tranzactia in array
#print "Trid-array after adding new-trid: @tridfile[0..$#tridfile]<br>\n"; #debug
}
#.end of generation of new transaction

#Action: rewrite transaction file
truncate(transactionFILE,0);
seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction file
#print "Tridfile length befor write: $#tridfile \n";
for($i=0;$i <= $#tridfile;$i++)
{
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
}

#close transactionfile
close(transactionFILE);
#return new trid
return($hexi);
}#.end sub add_transaction
#================================================================
#================================================================
#------------------------------------------------
#daca tranzactia nu exista intoarce string vid; daca exista, sterge linia din fisier si intoarce un string care e chiar linia de tranzactie din fisier;
sub get_transaction($) #what does this do?
{
my ($sub_trid)=@_;       #input data
my $entry;  #output data
my @tridfile;
my @linesplit;
my $i;

#open transaction file
open(transactionFILE,"+< tt_transaction");
seek(transactionFILE,0,0);		#go to the beginning
@tridfile = <transactionFILE>;		#slurp file into array


#Action: rewrite transaction file
#truncate(transactionFILE,0);
#seek(transactionFILE,0,0);				#go to beginning of transactionfile
#rewrite transaction number
#printf transactionFILE "%s",$tridfile[0]; #always alive
#rewrite transaction file

#unless($#tridfile == 0) 		#unless transaction list is empty (but transaction exists on first line)
#{ #.begin unless

for($i=1;$i <= $#tridfile;$i++)
{
   @linesplit=split(/ /,$tridfile[$i]);
chomp $linesplit[8];
if($linesplit[0] eq $sub_trid) {$entry = "$linesplit[1]:$linesplit[8]";}
else {
printf transactionFILE "%s",$tridfile[$i]; #we have \n at the end of each element
     }
}

#close transactionfile
close(transactionFILE);
#return transaction core

return($entry);

#} #.end unless
}#.end sub
#----------------------
sub defeat
{
my $message;
($message)=@_;
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>sistem colectie erori examYO</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="blue" alink="blue" vlink="red">\n!;
ins_gpl();
print qq!v 3.0.c\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h2 align="center">Actiune ilegala.</h2>\n!;
print qq!<h4 align="center">$message</h4>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
#---------it should continue here, but HTML code will continue after returning from function so that it prints different targets
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
print qq!</body>\n</html>\n!;
}
#-------------

sub addrec
{
my $sub_nick;
my $sub_code;
my $sub_text;
($sub_nick,$sub_code,$sub_text)=@_;

#### patch for mailer implementation from v 3.0.c ######
#open (MAIL, "|$mailprog -t") || die "Can't open $mailprog!\n";
#print MAIL "From: $admin_email\n";
#print MAIL "To: $target_email\n";
#print MAIL "Subject: new complaint filed\n\n";
#print MAIL <<to_the_end;
#new complaint was filed in
#to_the_end
#close (MAIL);
############ patch end #########

open(recFILE,"+< db_tt");
#goto end for append
seek(recFILE,0,2); #should be end of file
#append new record
printf recFILE "%s\n%s\n%s\n\n",$sub_nick,$sub_code,$sub_text; 

close(recFILE);
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>colectare erori si sugestii</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="blue" alink="blue" vlink="red">\n!;
ins_gpl();
print qq!v 3.0.c\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">Adaugare reusita.</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
#---------html page should finish here, but HTML code will continue after returning from function so that it prints different targets
}
#--------------------------------------
#primeste timestamp de forma sec_min_hour_day_month_year UTC
#out: seconds since expired MAX 99999, 0 = not expired.

sub timestamp_expired
{
use Time::Local;

my($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year)=@_;

my $timediff;
my $actualTime = time();
my $dateTime= timegm($x_sec,$x_min,$x_hour,$x_day,$x_month,$x_year);
$timediff=$actualTime-$dateTime;

return($timediff);  #here is the general return

} #.end sub timestamp

#-------------------------------------
sub compute_mac {

use Digest::HMAC_SHA1 qw(hmac_sha1_hex);
  my ($message) = @_;
  my $secret = '80b3581f9e43242f96a6309e5432ce8b';
  hmac_sha1_hex($secret,$message);
} #end of compute_mac

#--------------------------------------
#--------------------------------------
# treat the "or die" and all error cases
#how to use it
#$error_code is a string, you see it, this is the text selector
#$counter: if it is 0, error is not logged. If 1..5 = threat factor
#reference is the reference to string that is passed to be logged.

sub dienice
{
my ($error_code,$counter,$err_reference)=@_; #in vers. urmatoare counter e modificat in referinta la array/string(de ce?)
my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "err01",
              "ERR02" => "err02",
              "ERR03" => "err03",
              "ERR04" => "err04",
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
              "ERR19" => "reserved",
              "ERR20" => "silent discard, not displayed"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "token has been tampered with, sha1 mismatch",    #test ok
              "ERR02" => "token timestamp expired",           #test ok
              "ERR03" => "token is sha1, live, but not admin token",             #test ok
              "ERR04" => "funny state",
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
              "ERR19" => "reserved",
              "ERR20" => "silent discard, not logged"
                );


#if commanded, write errorcode in cheat_file
if($counter > 0)
{
# write errorcode in cheat_file
#ACTION: append cheat symptoms in cheat file
open(cheatFILE,"+< db_tt"); #open logfile for appending;
#flock(cheatFILE,2);            #LOCK_EX the file from other CGI instances
seek(cheatFILE,0,2);            #go to the end
#CUSTOM
printf cheatFILE qq!cheat logger\n$counter\n!; #de la 1 la 5, threat factor
printf cheatFILE "\<br\>reported by: troubleticket.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error in$
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
#ins_gpl(); #this must exist, but not for tool_admintt.cgi
print qq!v 3.2.2\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!;
#print qq!<center>In situatiile de congestie, incercati din nou in cateva momente.<br> In situatia in care erorile persista va rugam sa ne contactati pe e-mail, pentru explicatii.</center$
print qq!</body>\n</html>\n!;
}

exit();

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
print qq!In distributia de pe https://github.com/6oskarwN/Sim_exam_yo trebuie sa gasiti o copie a licentei GNU GPL, de asemenea si versiunea !;
print qq!in limba romana, iar daca nu, ea poate fi descarcata gratuit de pe pagina http://www.fsf.org/\n!;
print qq!Textul intebarilor oficiale publicate de ANCOM face exceptie de la cele de mai sus, nefacand obiectul licentierii GNU GPL,!; 
print qq!modificarea lor si/sau folosirea lor in afara Romaniei in alt mod decat read-only nefiind este permisa. Acest lucru deriva !;
print qq!din faptul ca ANCOM este o institutie publica romana, iar intrebarile publicate au caracter de document oficial.\n!;
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;
print qq!This program together with question database formatting, solutions to problems, manuals, documentation, sourcecode and!;
print qq!utilities is a  free software; you can redistribute it and/or modify it under the terms of the GNU General Public License !;
print qq!as published by the Free Software Foundation; either version 2 of the License, or any later version.\n!;
print qq!This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without any implied warranty.!; 
print qq!See the GNU General Public License for more details.\n!;
print qq!You should have received a copy of the GNU General Public License along with this software distribution; if not, you can!;
print qq!download it for free at http://www.fsf.org/\n!; 
print qq!Questions marked with ANCOM makes an exception of above-written, as ANCOM is a romanian public authority(similar to FCC in USA)!;
print qq!so any use of the official questions, other than in Read-Only way, is prohibited.\n!; 
print qq!YO6OWN Francisc TOTH\n!;
print qq!\n!;

print qq!Made in Romania\n!;
print qq+-->\n+;

}
