#!c:\Perl\bin\perl

#  tool_admintt.cgi v.0.0.6 (c)2007 - 2013 Francisc TOTH
#  status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  All rights reserved by YO6OWN Francisc TOTH
#  Made in Romania

# ch 0.0.6 displaying db_tt data better after sim_ver1 and troubleticket solved &specials; "overline" problems
# ch 0.0.5 using POST 
# ch 0.0.4 expelled KXP from title, has nothing to do now
# ch 0.0.3 added >>if (defined $ENV{'QUERY_STRING'})<<
# ch 0.0.2 solved troubleticket19


use strict;
use warnings;

#-hash table for response retrieving
my %answer=();    #hash used for depositing the answers

my $get_buffer; #intrarea
my $get_filename; #hamquest database filename

my @sw_k;   #array for analysing keys
my $call_switch=0; #1 - correct first call, shows the listing
            #2 - correct 2nd call, will modify
            #0 - bogus call
            
#$get_filename='db_tt';
my @pairs;
my $fline; #linia de fisier
my @dbtt;  #for slurp
my @newdbtt; #for writeback
sub dienice($);

###########################################
#BLOCK: Process inputs ###
###########################################
{
my $buffer;
my $pair;
my $kee;
my $name;
my $value;

# Read input text, POST od GET
  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case
  if($ENV{'REQUEST_METHOD'} eq "POST") 
    { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
    }
  else { $buffer = $ENV{'QUERY_STRING'}; #GET data
       }
@pairs=split(/&/, $buffer); #split into name - value pairs
                      


foreach $pair(@pairs) 
		{

($name,$value) = split(/=/,$pair);
$value=~ tr/+/ /;
$value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$value=~ s/\r\l\n$//g;
$value=~ s/\r\l\n/<br>/g;

 %answer = (%answer,$name,$value);        #hash filled in
		} 

# --------------- verify inputs
@sw_k = keys %answer;
foreach $kee(@sw_k) 
{
if(($kee eq 'admintxt0') and($call_switch == 0)) {$call_switch = 2; }
elsif(($kee eq 'filename') and ($call_switch == 0) and ($answer{'filename'} eq 'db_tt')) {$call_switch = 1; }
else {}
}

} #.end process inputs
#-----------
#$get_buffer=$ENV{'QUERY_STRING'};

#($fline,$get_filename)=split(/=/,$get_buffer);
####open hamquest file
if($call_switch == 1) #it's first call
{
$get_filename=$answer{'filename'};
if(defined($get_filename))
{
if(open(INFILE,"<","$get_filename")) #open read-only the question file
{

#flock(INFILE,1);		        #LOCK_SH, file can be read

seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>; #slurp

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v.0.0.6</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="#228b22" text="black" link="white" alink="white" vlink="white">\n!;

print qq!<center>\n!;
print qq![ex-Guestbook & ]Troubleticket administration v.0.0.6 for examYO &copy; YO6OWN, 2007-2013<br>\n!;
print qq!<form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;

print qq!<table border="1" width="90%">\n!;


#se parcurge fisierul de-andoaselea si se afiseaza toate inregistrarile de guestbook
for(my $i=0;$i<($#dbtt+1)/4;$i++)
{
print qq!<tr>\n!;
if($dbtt[$i*4+1] < 6){
print qq!<td bgcolor="lightblue">\n!;
}
else {print qq!<td bgcolor="lightgreen">\n!;
}
chomp $dbtt[$i*4+1];

print qq!<font color="black"><b>$dbtt[$i*4]</b></font>&nbsp;!;  #print nick

if($dbtt[$i*4+1] < 6)     #if it's a guestbook record
{

for (my $istar=0; $istar < $dbtt[$i*4+1]; $istar++)
{print qq!<IMG src="http://localhost/img/star.gif" WIDTH="15">\n!;
}
} #.end it's a guestbook record
else {
print qq!<select size="1" name="rating$i">\n!;

if($dbtt[$i*4+1] eq 6) {print qq!<option value="6" selected="y">nou</option>\n!;}
         else          {print qq!<option value="6">nou</option>\n!;}
if($dbtt[$i*4+1] eq 7) {print qq!<option value="7" selected="y">citit de admin</option>\n!;}
         else          {print qq!<option value="7">citit de admin</option>\n!;}
if($dbtt[$i*4+1] eq 8) {print qq!<option value="8" selected="y">rezolvat</option>\n!;}
         else          {print qq!<option value="8">rezolvat</option>\n!;}

print qq!</select>\n!;
print qq!\n!;
}

my $toprint=$dbtt[$i*4+2];
$toprint=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

print qq!<font color="black" size="-1">$toprint</font><br>\n!;
#print qq!<font color="black" size="-1">$dbtt[$i*4+2]</font><br>\n!;

unless ($dbtt[$i*4+3] eq "\n") {
print qq!<textarea name="admintxt$i" rows="3" cols="60" wrap="soft">$dbtt[$i*4+3]</textarea>\n!;
                               }
                               else {
                               print qq!<textarea name="admintxt$i" rows="2" cols="60" wrap="soft"></textarea>\n!;
                                    }
                   print qq!>>> Delete record: <input type="checkbox" value="on" name="delete$i">!;
print qq!</td>\n!;
print qq!</tr>\n!;                              

} #.end for/4
#----------------------

print qq!</table>\n!;
print qq!<center><INPUT type="submit"  value="Modify">\n!;
print qq!<INPUT type="reset"  value="Reset"> </center>\n!;
print qq!</form>\n!;
print qq!</center>!;
}

print qq!</body>\n!;
print qq!</html>\n!;

close (INFILE) || die("cannot close, $!\n");
} #.end if(defined($get_filename))
else  {dienice($get_filename);}
} #.end first call of admintt.cgi
elsif ($call_switch == 2)    #it's 2nd call if  'admintxt0=' exists - should be imlpemented
{

open(INFILE,"+<","db_tt"); #am fixat la db_tt, ca un hacker sa poata corupe doar pe asta.
seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>;

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v.0.0.6</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="gray" text="black" link="white" alink="white" vlink="white">\n!;

for(my $ki=0;$ki<($#dbtt+1)/4;$ki++)
{

if(exists $answer{"delete$ki"}) #daca exista vreo modificare de hash pt aceast ainregistrare
                              {} #do nothing, do not copy it over
 else #make replacements    
 {
@newdbtt=(@newdbtt,$dbtt[$ki*4]); #nick unchanged
if(exists $answer{"rating$ki"}) {@newdbtt=(@newdbtt,$answer{"rating$ki"});
                                 @newdbtt=(@newdbtt,"\n"); 
                                }
else {@newdbtt=(@newdbtt,$dbtt[$ki*4+1]);}
 
@newdbtt=(@newdbtt,$dbtt[$ki*4+2]); #text unchanged

if(exists $answer{"admintxt$ki"}) {@newdbtt=(@newdbtt,$answer{"admintxt$ki"});
                                   @newdbtt=(@newdbtt,"\n"); 
                                   }
else {@newdbtt=(@newdbtt,$dbtt[$ki*4+1]);}

 }                       
}

print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi?filename=db_tt" method="post">\n!;
print qq!<input type="submit" name="filename" value="db_tt">\n!;
print qq!</form></center>\n!; 

print qq!</body></html>!;

truncate(INFILE,0);			#
seek(INFILE,0,0);				#go to beginning of transactionfile
for(my $j=0;$j <= $#newdbtt;$j++)
{
printf INFILE "%s",$newdbtt[$j]; #we have \n at the end of each element
}
close(INFILE);
} #.end 2nd call
else #bogus calls, do no offer them any chance to guess the right form of calling
{
dienice('bogus!');
}
#-----------------
sub dienice($)
{
my $string=@_;
print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing error</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="#228b22" text="white">\n!;
print qq!<h1 align="center">Access denied / Accesul interzis</h1>\n!;
print qq!</body>\n!;
print qq!</html>!;
return 0;
}
