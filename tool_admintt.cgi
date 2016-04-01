#!c:\Perl\bin\perl

#  tool_admintt.cgi v.3.2.0 (c)2007 - 2016 Francisc TOTH
#  status: devel
#  This is a module of the online radioamateur examination program
#  "SimEx Radio", created for YO6KXP ham-club located in Sacele, ROMANIA
#  All rights reserved by YO6OWN Francisc TOTH
#  Made in Romania

# ch 3.2.0 implement admin authentication using an md5 token, guestbook should be alliminated
# ch 0.0.6 displaying db_tt data better after sim_ver1 and troubleticket solved &specials; "overline" problems
# ch 0.0.5 using POST 
# ch 0.0.4 expelled KXP from title, has nothing to do now
# ch 0.0.3 added >>if (defined $ENV{'QUERY_STRING'})<<
# ch 0.0.2 solved troubleticket19


use strict;
use warnings;

#-hash table for response retrieving
my %answer=();    #hash used for depositing the answers
my $post_token;   #token from input data

my $get_buffer; #intrarea originala

my $call_switch=0; #1 - correct first call,only token, shows the listing
            #2 - correct 2nd call, token+reflow text, will modify
            #0 - bogus call - not even token received
            
my @pairs;
my $fline; #linia de fisier
my @dbtt;  #for slurp
my @newdbtt; #for writeback

###########################################
#BLOCK: Process inputs ###
###########################################
{
my $buffer;
my $pair;
my $kee;
my $name;
my $value;

# Read input text, POST or GET
  $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;   #facem totul uper-case 
  if($ENV{'REQUEST_METHOD'} eq "POST") 
    { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); #POST data
    }
  else { $buffer = $ENV{'QUERY_STRING'}; #GET data
       }
@pairs=split(/&/, $buffer); #split into name - value pairs
                      
#print qq!input: $buffer <br><br>\n!; #debug

foreach $pair(@pairs) 
		{
($name,$value) = split(/=/,$pair);

#transformarea asta e pentru textele reflow, dar trateaza si + si / al token-ului

$value=~ s/\+/ /g; 
$value=~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$value=~ s/\r\l\n$//g;
$value=~ s/\r\l\n/<br>/g;

 %answer = (%answer,$name,$value); #hash filled in with key+value

		} #end foreach

#hash it is filled in now

$post_token= $answer{'token'}; #extract token from input data
#md MAC has + = %2B and / = %2F characters, must be reconverted
#already converted in foreach
#$post_token =~ s/%2B/\+/g;
#$post_token =~ s/%2F/\//g;

#print qq!token received: $post_token<br>\n!; #debug
#transaction pattern: 
# admin_33_19_0_12_2_116_Trl5zxcXkaO5YcsWr4UYfg

#now we should check received transaction
#case 0: check md5 if correct
#        if not, must be recorded in cheat_file
#case 1: check if timestamp expired; if expired, no log in cheat
#case 2: check if it's an admin transaction
#        if not, record in cheat_file

my $string_token; # we compose the incoming transaction to recalculate mac
my $heximac;

unless(defined($post_token)) {dienice ("ERR01",1,\"undef token"); } # no token or with void value
@pairs=split(/_/,$post_token); #reusing @pairs variable for spliting results
# $pairs[7] is the mac
unless(defined($pairs[7])) {dienice ("ERR01",1,\$post_token); } # unstructured token
$string_token="$pairs[0]\_$pairs[1]\_$pairs[2]\_$pairs[3]\_$pairs[4]\_$pairs[5]\_$pairs[6]\_";
$heximac=compute_mac($string_token);

unless($heximac eq $pairs[7]) { dienice("ERR01",5,\$post_token);} #case of tampering

#check case 1
elsif (timestamp_expired($pairs[1],$pairs[2],$pairs[3],$pairs[4],$pairs[5],$pairs[6])) { 
                                             dienice("ERR02",0,\"null"); }

#check case 2
 elsif ($pairs[0] ne 'admin') {dienice("ERR03",2,\$post_token);}

#we determine here if is display order (=1) or writing order(=2)

if( exists($answer{'admintxt0'}) and exists($answer{'token'})) { $call_switch = 2;}
elsif(exists($answer{'token'})) {$call_switch = 1;}

#print qq!call_switch: $call_switch<br>\n!;#debug

} #.end block process inputs
#-----------

## if display was ordered
if($call_switch == 1) #it's  a display order
{
open(INFILE,"<","db_tt") or die(); #open read-only the tickets file

#flock(INFILE,1);		        #LOCK_SH, file can be read

seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>; #slurp

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v.3.2.0</title>\n!;
print qq!</head>\n!;
print qq!<body bgcolor="#228b22" text="black" link="white" alink="white" vlink="white">\n!;

print qq!<center>\n!;
print qq![ex-Guestbook & ]<font color="white">Troubleticket administration v.3.2.0 for examYO &copy; YO6OWN, 2007-2016</font><br>\n!;
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
{print qq!<IMG src="http://localhost/star.gif" WIDTH="15">\n!;
}
                     } #.end it's a guestbook record
else {   #else it is a trouble ticket
print qq!<select size="1" name="rating$i">\n!;

if($dbtt[$i*4+1] eq 6) {print qq!<option value="6" selected="y">nou</option>\n!;}
         else          {print qq!<option value="6">nou</option>\n!;}
if($dbtt[$i*4+1] eq 7) {print qq!<option value="7" selected="y">citit de admin</option>\n!;}
         else          {print qq!<option value="7">citit de admin</option>\n!;}
if($dbtt[$i*4+1] eq 8) {print qq!<option value="8" selected="y">rezolvat</option>\n!;}
         else          {print qq!<option value="8">rezolvat</option>\n!;}

print qq!</select>\n!;
print qq!\n!;
} #else trouble ticket

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

#print qq!<center><INPUT type="text" name="token" size="40" value="$post_token">\n!;
print qq!<center><INPUT type="hidden" name="token" value="$post_token">\n!;
print qq!<center><INPUT type="submit"  value="Modify">\n!;
print qq!<INPUT type="reset"  value="Reset"> </center>\n!;
print qq!</form>\n!;
print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;
#print qq!<center><INPUT type="text" name="token" size="40" value="$post_token">\n!;
print qq!<center><INPUT type="hidden" name="token" value="$post_token">\n!;
print qq!<center><INPUT type="submit"  value="Refresh"> </center>\n!;
print qq!</form>\n!;
print qq!</center>!;
#}
print qq!</body>\n!;
print qq!</html>\n!;

close (INFILE) || die("cannot close, $!\n");
#} #.end if(open(db_tt))
#else  {dienice("ERR04",0,\"null");}
} #.end first call of tool_admintt.cgi


#### if it's 2nd call

elsif ($call_switch == 2)    #it's 2nd call if  'admintxt0=' exists - should be imlpemented
{

open(INFILE,"+<","db_tt"); #am fixat la db_tt, ca un hacker sa poata corupe doar pe asta.
seek(INFILE,0,0);			#goto begin of file
@dbtt=<INFILE>;

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n!;
print qq!<title>ticket listing v.3.2.0</title>\n!;
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

print qq!<center><form action="http://localhost/cgi-bin/tool_admintt.cgi" method="post">\n!;
print qq!<input type="text" name="token" size="40" value="$post_token"><br>\n!;
print qq!<input type="submit" value="AGAIN">\n!;
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
dienice("ERR04",5,\"bogus");
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
#my $timestring=localtime(time);
my $timestring=gmtime(time);

#textul pentru public
my %pub_errors= (
              "ERR01" => "admin authentication token fail, logged.",
              "ERR02" => "token expired, get another token",
              "ERR03" => "identity failed, logged.",
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
              "ERR20" => "reserved"
                );
#textul de turnat in logfile, interne
my %int_errors= (
              "ERR01" => "token has been tampered with, md5 mismatch",    #test ok
              "ERR02" => "token timestamp expired",           #test ok
              "ERR03" => "token is md5, live, but not admin token",             #test ok
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
              "ERR20" => "reserved"
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
printf cheatFILE "\<br\>reported by: tool_admintt.cgi\<br\>  %s: %s \<br\> Time: %s\<br\>  Logged:%s\n\n",$error_code,$int_errors{$error_code},$timestring,$$err_reference; #write error info in logfile
close(cheatFILE);
}

print qq!Content-type: text/html\n\n!;
print qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
print qq!<html>\n!;
print qq!<head>\n<title>examen radioamator</title>\n</head>\n!;
print qq!<body bgcolor="#228b22" text="#7fffd4" link="white" alink="white" vlink="white">\n!;
#ins_gpl(); #this must exist
print qq!v.3.2.0\n!; #version print for easy upload check
print qq!<br>\n!;
print qq!<h1 align="center">$pub_errors{$error_code}</h1>\n!;
print qq!<form method="link" action="http://localhost/index.html">\n!;
print qq!<center><INPUT TYPE="submit" value="OK"></center>\n!;
print qq!</form>\n!; 
#print qq!<center>In situatiile de congestie, incercati din nou in cateva momente.<br> In situatia in care erorile persista va rugam sa ne contactati pe e-mail, pentru explicatii.</center>\n!;
print qq!</body>\n</html>\n!;

exit();

} #end sub

#--------------------------------
