#!/usr/bin/perl

# ver. 3.0.4
# general syntax-checking and auto-numbering script for eXAM databases(except db_human)
# (c) 2007 Francisc TOTH YO6OWN
# input at commandline:db_syntax.pl db_xxxxx prog_Programa
# output db_xxxxx.out and db_xxxxx.html and strip_db_xxxx
# open with a text editor the db_xxxxx.out, and on line 2 put the number of questions(last+1, because first question is ##0#)
# sa faca toata treaba, outputul sa fie corect, in UNIX format!!!!! sau sa fie error.
# in HTML sa dea warning daca linia intrebarii nu contine v3code(nu e obligatoriu, dar doar cele cu v3 fac history)


#ch v.3.0.5 - nu detecteaza daca sunt doua v3-coduri - nu inteleg
#ch v.3.0.5 - awardspace.com banned list check: "porn","proxy","vand" to be implemented

use strict;
use warnings;

my $filename;
my $programa;

my $in_line;
my $counter; #counts the overall questions
my $q_counter; #counts the number of lines of a question
my $overall_err;
my $overall_warnings;

$overall_err=0;
$overall_warnings=0;

$filename= $ARGV[0];
$programa= $ARGV[1];

if(!defined( $filename)) {print "please enter db_xxx filename"; exit();}
if(!defined( $programa)) {print "please enter prog_xxx filename"; exit();}

####open hamquest file
open(INFILE,"<", "$filename") || print "can't open $filename!\n"; #open the question file
open(OUTFILE,">", "$filename.out") || print "can't open $filename.out\n";
open(HTFILE, ">", "$filename.html") || print "can't open $filename.html";

printf HTFILE qq!Content-type: text/html\n\n!;
printf HTFILE qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
printf HTFILE qq!<html>\n!;
printf HTFILE qq!<head>\n<title>$filename.html</title>\n</head>\n!;
printf HTFILE qq!<body bgcolor="forestgreen" text="aquamarine" link="white" alink="white" vlink="white">\n!;

#init the counter
$counter = 0;
$q_counter = 24;#init 
#rewind prompter in infile
seek(INFILE,0,0); #go to the beginning
$in_line=<INFILE>;

if(defined($in_line)){
do
{
if($in_line =~ /##/)
      {
			if($q_counter != 11) {
								printf HTFILE qq!<font color="red"><b>Line counting error for $filename, question ##$counter-1#</b></font><br>\n!;
								$overall_err++;
								}
            printf OUTFILE "##%i#\n",$counter;
             printf HTFILE "##%i#<br>\n",$counter;
			$counter++;
			$q_counter=0; #qcounter reset
			}
else {
if($q_counter == 25) {print "Nr. intrebari DECLARATE $in_line"; $q_counter=10;}
if($q_counter == 0) #if it's the answer line
{
 if(($in_line ne "a\n") and ($in_line ne "b\n") and ($in_line ne "c\n") and ($in_line ne "d\n"))
 {printf HTFILE qq!<font color="red"><b>Line $q_counter, question ##$counter-1#  should be an _answer_ a/b/c/d</b></font><br>\n!;
  $overall_err++;
 }
}
if($q_counter == 1) #if it's question
{
	unless($in_line =~ /^([0-9]{2,3}[A-Z]{1}[0-9]{2,}[a-z]{0,}~&)/) { printf HTFILE qq!<font color="blue"><b>Warning: W3code missing/extra</b></font><br>\n!;
	  $overall_warnings++;
	 }
}
if($q_counter == 2) #if it's image of question
{
unless($in_line =~ /^null$/)  #if no picture present, there is a ^null$ (regexp)
  {
unless((($in_line =~ /.gif/) && ($in_line =~ / /)) or (($in_line =~ /.jpg/) && ($in_line =~ / /)) ) #or ($in_line =~ /.jpg/)))
                                           {
                                          printf HTFILE qq!<font color="red"><b>image line syntax error</b></font><br>\n!; 
                                          $overall_err++;
                                           }
                                           }
  } #.end unless($in_line =~ /^null$/)

if($q_counter == 8) #if it's image of solution
{
unless($in_line =~ /^null$/)  #if no picture present, there is a ^null$ (regexp)
  {
unless((($in_line =~ /.gif/) && ($in_line =~ / /)) or (($in_line =~ /.jpg/) && ($in_line =~ / /)) ) #or ($in_line =~ /.jpg/)))
                                           {
                                          printf HTFILE qq!<font color="red"><b>image line syntax error</b></font><br>\n!; 
                                          $overall_err++;
                                           }
                                           }
  } #.end unless($in_line =~ /^null$/)

printf OUTFILE "%s",$in_line;
printf HTFILE "%s<br>\n",$in_line;

$q_counter++;
}

$in_line=<INFILE>;
}
while(defined($in_line));

#semnalizare pentru ultima problema
			if($q_counter != 11) {
								printf HTFILE qq!<font color="red"><b>Line counting error question ##$counter-1#</b></font><br>\n!;
								$overall_err++;
								}
}#if defined(in_line) - daca nu cumva fisierul e gol

print "Numar intrebari NUMARATE in db: $counter\n";

printf HTFILE qq!Overall errors: $overall_err<br>\n!;
print "db_numbering: Errors: $overall_err\n";
printf HTFILE qq!Warning/fara V3 code: $overall_warnings<br>\n!;
print "db_numberig: lipsa v3 code: $overall_warnings\n";
printf HTFILE qq!</body>\n</html>\n!;

close(HTFILE);
close(INFILE);
close(OUTFILE);

system("perl strip.pl $filename $programa"); #call strip
system("mv $filename.out hx_release/$filename"); #result
system("mv strip_$filename hx_release/"); #move strip

