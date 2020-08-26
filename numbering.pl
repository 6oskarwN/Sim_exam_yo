#!/usr/bin/perl

# ver. 3.0.6
# general syntax-checking and auto-numbering script for eXAM databases(except db_human)
# (c) 2008-2019 Francisc TOTH YO6OWN
# input at commandline:db_syntax.pl db_xxxxx [prog_Programa]
# output in ./hx_release db_xxx and strip_db_xxx and in . db_xxx.html
# open with a text editor the db_xxxxx.out, and on line 2 put the number of questions(last+1, because first question is ##0#)
# DONE sa faca toata treaba, outputul sa fie corect, in UNIX format!!!!! sau sa fie error.
# DONE in HTML da warning daca linia intrebarii nu contine v3code(nu e obligatoriu, dar doar cele cu v3 fac history)

#ch v.3.0.6 - prog_Programa is already known and contained in first line of db_xxxxx
#ch v.3.0.5 - warning daca raspunsurile lina 4-7 sa fie doar de formatul /^[a-d]$/
#ch v.3.0.4 - awardspace.com banned list check: "porn","proxy","vand" implemented

use strict;
use warnings;

my $filename;	#name like db_xxx, input parameter ARGV[]
my $programa;   #name like prog_CEPT_radiotehnica, input parameter ARGV[]

my $in_line;
my $counter; #counts the overall questions
my $q_counter; #counts the number of lines of a question
my $overall_err; #overall errors, counter
my $overall_warnings; #overall warnings, counter
my $iter;    #for cycle iteration variable
my @dictionary =(
                 'regexp',
                 'sex',
                 'porn',
                 'proxy',
                 'ativan'  #new name for Lorazepam
                );

$overall_err=0;       #init
$overall_warnings=0;  #init

$filename= $ARGV[0];
$programa= $ARGV[1]; #ramane, doar pentru alegere

if(!defined( $filename)) {print "please enter db_xxx filename"; exit();}
 else {
open(INFILE,"<", "$filename") || print "can't open $filename!\n"; #open the question file
#rewind prompter in infile
seek(INFILE,0,0); #go to the beginning
$in_line=<INFILE>; #read first line  
my @splitter= split(/<curricula>|<\/curricula>/,$in_line);
$programa=$splitter[1];
print "detected curricula: $programa \n";
close (INFILE);
      }
if(!defined( $programa)) {print "please enter prog_xxx filename"; exit();}

####open db_xxx hamquest file
open(INFILE,"<", "$filename") || print "can't open $filename!\n"; #open the question file
open(OUTFILE,">", "$filename.out") || print "can't open $filename.out\n";
#HTFILE opens a html result file where warnings and errors are highlighted
open(HTFILE, ">", "$filename.html") || print "can't open $filename.html";

printf HTFILE qq!Content-type: text/html\n\n!;
printf HTFILE qq?<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n?; 
printf HTFILE qq!<html>\n!;
printf HTFILE qq!<head>\n<title>$filename.html</title>\n</head>\n!;
printf HTFILE qq!<body bgcolor="forestgreen" text="aquamarine" link="white" alink="white" vlink="white">\n!;

#init the counter
$counter = 0;
$q_counter = 24;   #init with big dummy value 
#rewind prompter in infile
seek(INFILE,0,0); #go to the beginning

$in_line=<INFILE>; #citim nr de intrebari  

if(defined($in_line)){

do
{

#pentru fiecare linie non-vida, verificam cuvintele banned din awardspace.com list
foreach $iter (@dictionary)
       {
        if(lc($in_line) =~ /$iter/) #forces lower-case
          {
           print qq!dictionary badword \"$iter\" in $filename, question $counter-1\n!;
           $overall_err++;
          }
       }


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

        if($in_line =~ /^[a-d]$/) 
              {printf HTFILE qq!<font color="red">ERROR: [a-d] not for this line</font>!;
	       $overall_err++;
              }
}

if(($q_counter > 3) && ($q_counter < 8)) #if it's one of answers
{
        if($in_line =~ /^[a-d]$/) 
              {printf HTFILE qq!<font color="blue">Warning: [a-d] seems unfinished business</font><br>\n!;
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

$in_line=<INFILE>; #fetch a new line from db_xx at the end of do {} while()
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
printf HTFILE qq!Warnings: $overall_warnings<br>\n!;
print "db_numbering: Warnings: $overall_warnings\n";
printf HTFILE qq!</body>\n</html>\n!;
print "See generated $filename\.html file for details\n";
close(HTFILE);
close(INFILE);
close(OUTFILE);

system("perl strip.pl $filename $programa"); #call strip
system("mv $filename.out hx_release/$filename"); #result
system("mv strip_$filename hx_release/"); #move strip

