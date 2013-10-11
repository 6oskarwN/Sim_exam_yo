#!/usr/bin/perl

# db stripping tool. only v3 codes remain, one per line
# (c) 2010 Francisc TOTH YO6OWN
# ver. 3.0.3
# input at commandline:strip.pl db_xxxx prog_XXXX
# output strip_xxxxx 

#ch 3.0.3 - implementat verificarea daca un v3-code are capitolul existent in curricula

use strict;
use warnings;

my $filename;
my $programa;

my $v3code;
my @splitter;
my $in_line;
my $l_count=99;
my %progcodes=(); #codes from curricula, value is dummy
my %unique=();     #inainte sa introducem un cod, verificam unicitatea. value is dummy

$filename= $ARGV[0];
$programa= $ARGV[1];

####open hamquest file
open(INFILE,"<", "$filename") || print "can't open $filename!\n"; #open the question file
open(PRFILE,"<", "$programa") || print "can't open $programa!\n"; #open the curricula file

open(OUTFILE,">", "strip_$filename") || print "can't open stri_$filename\n";

#init the progcodes hash
#rewind prompter in infile
seek(PRFILE,0,0); #go to the beginning
while($in_line=<PRFILE>)
{
	if($in_line =~ /^[0-9]{2,}[a-z]?&/)
	{
		@splitter= split(/&/,$in_line);
		#print "$splitter[0] is curricula code\n";
		%progcodes = (%progcodes,$splitter[0],"dummy");
	}
	
}


#rewind prompter in infile
seek(INFILE,0,0); #go to the beginning
while($in_line=<INFILE>)
 {
if($in_line =~ /\#\#/){ $l_count=0;}
  else {$l_count ++;}

if($in_line =~ /^[0-9]{2,3}[A-Z]{1}[0-9]{2,}[a-z]?~&/)
  {
@splitter= split(/~&/,$in_line);
$v3code=$splitter[0];
printf OUTFILE  "$v3code\n";
#verificam unicitatea
 if (defined($unique{$v3code})) #daca exista deja
     {print "strip.pl error report: v3 code not unique: $v3code \n";}
   else {%unique = (%unique,$v3code,"dummy");}
#sfarsit verificare unicitate

#verificam daca se gaseste in programa
@splitter= split(/[A-Z]{1}/,$v3code);
if (defined($progcodes{$splitter[1]})) #daca exista in curricula capitol
     {}
     else {print "$v3code not from curricula\n"}
  }
elsif($l_count==2){printf OUTFILE  "\n";}


 } #..end while

close(INFILE);
close(PRFILE);
close(OUTFILE);



