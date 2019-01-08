#!/usr/bin/perl

# db stripping tool. only v3 codes remain, one per line
# (c)2014 - 2019 Francisc TOTH YO6OWN
# ver. 3.0.6
# input at commandline:strip.pl db_xxxx prog_XXXX
# output strip_xxxxx 

#ch 3.0.6 - resolved bug, ch 3.0.5 was appending after </html>
#ch 3.0.5 - numaratoarea e cu bold-galben
#ch 3.0.4 - face numaratoarea acoperirii cu subiecte a curriculei
#ch 3.0.3 - implementat verificarea daca un v3-code are capitolul existent in curricula

use strict;
use warnings;

my $filename;
my $programa;

my $v3code;
my @splitter;
my $in_line;
my $l_count=99;
my $key; #iterator when we read the hash
my %progcodes=(); #hash of codes from curricula(keys), list of V3-codes as values
my %unique=();    #inainte sa introducem un cod, verificam unicitatea. value is dummy
my $array_size; #used to check coverage of curricula

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
	if($in_line =~ /^[0-9]{2,}[a-z]{0,}&/) #v3 code
	{
		@splitter= split(/&/,$in_line);
		#print "$splitter[0] is curricula code\n"; #debug
		%progcodes = (%progcodes,$splitter[0],[]); #each key gets as value reference to an array
	}
	
}


#rewind prompter in infile
seek(INFILE,0,0); #go to the beginning
while($in_line=<INFILE>)
 {
if($in_line =~ /\#\#/){ $l_count=0;}
  else {$l_count ++;}

if($in_line =~ /^[0-9]{2,3}[A-Z]{1}[0-9]{2,}[a-z]?~&/) #v3 code
  {
@splitter= split(/~&/,$in_line);
$v3code=$splitter[0];

printf OUTFILE  "$v3code\n"; #introducem codul in strip file

#verificam unicitatea
 if (defined($unique{$v3code})) #daca exista deja
     {print "strip.pl error report: v3 code not unique: $v3code \n";}
   else {%unique = (%unique,$v3code,"dummy");}
#sfarsit verificare unicitate


#verificam daca se gaseste in programa
@splitter= split(/[A-Z]{1}/,$v3code);
if (defined($progcodes{$splitter[1]})) #daca exista in curricula capitol

# atunci facem ceva: inseram intrebarea in arrayul liniei de programa
  {
 #print "gasit intrebare $v3code in $splitter[1]\n";#debug
 push(@{$progcodes{$splitter[1]}},$v3code); #add v3 to array
 #print "array $splitter[1]: @{$progcodes{$splitter[1]}}\n"; #debug

  }

     else {
             print "$v3code not from curricula\n";
          }
  }
elsif($l_count==2){printf OUTFILE  "\n";}


 } #..end while

close(INFILE);
close(OUTFILE);

#now we must display the curricula coverage

#open HTML output file, append style
#error, it appends after </body>
open(HTFILE, "+<", "$filename.html") || print "can't open $filename.html\n";
seek(HTFILE,0,0); #start with the beginning
#$in_line=<HTFILE>;#read first line for variable init
do{
   if($in_line=<HTFILE>) {} #we must check for EOF also
     else {$in_line = "Warnings: 99<br>";} #if EOF we give this value                  
  # print $in_line;   #debug
  }
until ($in_line =~ /^Warnings\:.*<br>$/);


#rewind prompter in infile
seek(PRFILE,0,0); #go to the beginning
while($in_line=<PRFILE>)
{
	if($in_line =~ /^[0-9]{2,}[a-z]{0,}&/) #v3 code
	{
		@splitter= split(/&/,$in_line);
         $array_size= @{$progcodes{$splitter[0]}};

#printf HTFILE qq!<b>$array_size</b> $in_line \{@{$progcodes{$splitter[0]}}\} <br>!; #print coverage, line by line
    printf HTFILE qq!<b><font color="yellow">$array_size</font></b> $in_line<br>!; #only counting
#    print "$array_size $in_line"; #print to stdout

	}
        else 
          {
              printf HTFILE qq!$in_line<br>!;
#              print "$in_line"; #print to stdout
           }
	
}

close(PRFILE); #finally we close programa

print HTFILE qq!\n</body>\n!;
print HTFILE qq!</html>\n!;
close(HTFILE);
