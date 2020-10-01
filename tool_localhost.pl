#!/usr/bin/perl

#  tool_customize v.0.0.c (c)2008 - 2019 Francisc TOTH
#  status: devel
#  customizing tool
#  makes the automatic relocation of links
#  inserts release number
#  removes all remarks which start at begin of line or have a whitespace character before '#'
#  All rights reserved by YO6OWN Francisc TOTH
#  Made in Romania


#using the tool:
# 1. datafill this script with all correct file names
# 2. datafill this script with all patterns+replacements
# 3. datafill the correct release number
# 4. run the script in the parent directory of directory "hx_release/"
# the result files will be deposited in "hx_release/" directory

use strict;
use warnings;

my @filelist;

if(defined($ARGV[0])) {@filelist= ($ARGV[0]);}
else {@filelist=(
				'sim_authent.cgi',
				'sim_gen0.cgi',
				'sim_gen1.cgi',
				'sim_gen2.cgi',
				'sim_gen3.cgi',
				'sim_gen4.cgi',
				'sim_ver0.cgi',
				'sim_ver1.cgi',
				'sim_ver2.cgi',
				'sim_ver3.cgi',
				'sim_ver4.cgi',
				'sim_register.cgi',
				'tugetxr2.cgi',
 				'tool_checker2.cgi',
				'troubleticket.cgi',
				'tool_admintt.cgi',
				'My/ExamLib.pm'
				); #numele fisierelor

}
my $pattern1="80b3581f9e43242f96a6309e5432ce8b"; #development secret
my $replacement1="80b3581f9e43242f96a6309e5432ce8b";  #production
my $pattern1b="80b3581f9e43242f96a6309e5432aaaa"; #development secret
my $replacement1b="80b3581f9e43242f96a6309e5432aaaa";  #production

my $pattern2="localhost/";
my $replacement2="localhost/";

my $pattern3="^print qq!SimEx Radio Release";
my $replacement3="print qq!SimEx Radio Release 3.4; Author: Francisc TOTH YO6OWN\\n!;\n";




foreach my $FileName(@filelist)
{
#deschizi fisier sursa
open(INFILE,"<", "$FileName") || print "can't open $FileName: $!\n";
my @CopyBuffer; #bufferul target
my $fetch_line; #line-buffer

while($fetch_line=<INFILE>)
{
#line alterations
$fetch_line=~s/$pattern1/$replacement1/; #local replacement
$fetch_line=~s/$pattern1b/$replacement1b/; #local replacement

if($fetch_line=~/$pattern3/){$fetch_line=$replacement3;}#line replacement

$fetch_line=~s/$pattern2/$replacement2/; #local replacement

#$fetch_line=~s/$pattern21/$replacement21/; #local replacement
#if($fetch_line=~/$pattern21/){$fetch_line=$replacement21;}#line replacement


#removes all remarks
$fetch_line =~ s%(^|\s)(#)([^!])(.*)$%%;

#copy (possibly) altered line to buffer
@CopyBuffer=(@CopyBuffer,$fetch_line);
}

close (INFILE); #inchizi fisierul sursa

open(OUTFILE,">", "hx_release/$FileName") || print "can't write to $FileName.hx\n"; #deschizi fisier copie .hx
foreach $fetch_line(@CopyBuffer)
{print OUTFILE "$fetch_line";} 
close(OUTFILE); #inchizi fisierul.hx

}
