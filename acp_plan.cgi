#!/usr/bin/perl 

# Script to create a skeleton plan for Astronomer's Control Program
# (ACP) for observing a transit.  Input parameters are passed in the
# URL.  Typically this would be called from a URL that is created
# on the fly in the output of the list of transits for a given night,
# from plot_transits.cgi. 

# Copyright 2013-2019 Eric Jensen, ejensen1@swarthmore.edu.
# 
# This file is part of the Tapir package, a set of (primarily)
# web-based tools for planning astronomical observations.  For more
# information, see  the README.txt file or 
# http://astro.swarthmore.edu/~jensen/tapir.html .
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program, in the file COPYING.txt.  If not, see
# <http://www.gnu.org/licenses/>.

# 2018-03-15: Replace spaces in target name with underscores. 

use CGI;
use DateTime::Format::Epoch::JD;


use strict;
use warnings;

my $q = CGI->new();

# Contact info provided in the fatal_error subroutine:
my $script_contact_person = 'Eric Jensen, ejensen1@swarthmore.edu';

# Get some input settings from the URL:

my $jd_start = $q->param("jd_start");
my $jd_end = $q->param("jd_end");
# Above are for start and end of transit, this is quit time
# for script based on other constraints: 
my $jd_quit = $q->param("jd_quit");
my $V = $q->param("V");

# Sometimes abbreviated versions of the transit start/end times might
# be passed in; fix them.
if ($jd_start ne "") {
    if ($jd_start < 50000) {
	$jd_start += 2450000;
    } elsif ($jd_start < 2000000) {
	$jd_start += 2400000;
    }
}

if ($jd_end ne "") {
    if ($jd_end < 50000) {
	$jd_end += 2450000;
    } elsif ($jd_end < 2000000) {
	$jd_end += 2400000;
    }
}

if ($jd_quit ne "") {
    if ($jd_quit < 50000) {
	$jd_quit += 2450000;
    } elsif ($jd_quit < 2000000) {
	$jd_quit += 2400000;
    }
}


my $end_datetime = DateTime::Format::Epoch::JD->parse_datetime( $jd_end );
$end_datetime->set_time_zone('UTC');
# And get it in human-readable form:
my $end_datetime_string = sprintf("%s %02d:%02d", $end_datetime->mdy("/"), 
				  $end_datetime->hour(),
				  $end_datetime->minute() );

my $quit_time_string;
my $quit_message; 
# See if a quitting time was passed in: 
if ($jd_quit > 0) {
    my $quit_datetime = DateTime::Format::Epoch::JD->parse_datetime(
	$jd_quit );
    $quit_datetime->set_time_zone('UTC');

    $quit_time_string = sprintf("%s %02d:%02d", $quit_datetime->mdy("/"), 
				   $quit_datetime->hour(),
				   $quit_datetime->minute() );
    $quit_message = "and was based on alt/HA/daylight/baseline constraints."

} else {
   # Specify a time that is one hour after egress:
    $end_datetime->add( minutes => 60 );
    $quit_time_string = sprintf("%s %02d:%02d", $end_datetime->mdy("/"), 
				   $end_datetime->hour(),
				   $end_datetime->minute() );
    $quit_message = "and is one hour after egress."
}

my $start_datetime = DateTime::Format::Epoch::JD->parse_datetime( $jd_start );
$start_datetime->set_time_zone('UTC');
my $start_datetime_string = sprintf("%s %02d:%02d", $start_datetime->mdy("/"), 
				  $start_datetime->hour(),
				  $start_datetime->minute() );


my $ra = $q->param("ra");
my $dec = $q->param("dec");
my $target = $q->param("target");

# Replace whitespace in target name with underscores: 
$target =~ s/\s+/_/g;

# If there was a leading plus sign for the dec, it gets interpreted as
# a space when passed in the query component of the URL.  So here, we
# change it back to a plus - easier to do this than to try to URL
# encode it on the input end:
if ($dec =~ /^ \d/) {
    $dec =~ s/^ /\+/;
}


# Make a very rough cut at exposure time based on V magnitude.
# Estimate about 80 seconds for 11th mag, scale with a slightly 
# softer power law than the real magnitude equation: 
my $exp_time = sprintf("%d", 80 * 2**($V - 11));


print $q->header(
		 -type => "text/plain; charset=utf-8",
		 );
print <<END1;
; ACP plan for target $target\r
; Auto-generated by Tapir; editing will be necessary!\r
; Transit is from $start_datetime_string to $end_datetime_string UTC.\r
#FILTER r'\r
#BINNING 2\r
#REPEAT 999\r
#AUTOGUIDE\r
; Exposure time roughly estimated based on target V = $V\r
#INTERVAL $exp_time\r
; Uncomment 'waitairmass' if needed, but beware a bug that can\r
; make it skip a target if used in afternoon / early evening.\r
; #WAITAIRMASS 2.0, 300\r
$target\t$ra\t$dec\r
; Quit time is in UTC, $quit_message Edit as needed.\r
#QUITAT $quit_time_string\r
END1


# End of main routine.



sub fatal_error {

# Simple wrapper to allow us to die gracefully if a problem occurs, by
# printing out an HTML header and then a (hopefully) useful error
# message. 

    my ($title, $message) = @_;

    print $q->header(-type => "text/html; charset=utf-8");
    print $q->start_html(-title => $title);
    print $q->h2("Fatal error in input");
    print $q->p($message);
    print $q->end_html;
    die;
}
