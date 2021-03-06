#!/usr/cti/apps/CSPbase/Perl/bin/perl

# Usage of packages
use strict;
use warnings;
use XML::XPath;
use XML::XPath::XMLParser;

# File Name
my $FILE_NAME="insert_group";

#Database Connection
my $DB_USER="srgkpi";
my $DB_PASS="Kpi~1Mhsp";
my $DB_NAME="RDB1";
my $CONNECT_STRING="$DB_USER\/$DB_PASS\@$DB_NAME";

# Folders
my $BASE_DIR=data/mms/utils/kpi_seed_values";
my $SEED_XML_FILES_FOLDER="$BASE_DIR/SEED_XML_FILES";
my $SCRIPTS_FOLDER="$BASE_DIR/SCRIPTS";
my $LOG_FOLDER="$BASE_DIR/LOG";

# Shell Script Name
my $EXECUTION_SCRIPT="$SCRIPTS_FOLDER/execute.sh";

# SQL File Name
my $SQL_FILE="$BASE_DIR/$FILE_NAME.sql";

# Log File Name
my $LOG_FILE="$LOG_FOLDER/$FILE_NAME.log";

# XML File Name
my $XML_FILE="$SEED_XML_FILES_FOLDER/$FILE_NAME.xml";

# XSD File Name
my $XSD_FILE="$SEED_XML_FILES_FOLDER/XSD_FILES/$FILE_NAME.xsd";

# XML File Validation
`xmllint --noout --nowarning --schema "$XSD_FILE" "$XML_FILE" 2>&1`;

#`xmlwf $SEED_XML_FILES_FOLDER/$FILE_NAME.xml >>$LOG_FILE`;

my $validate=`cat $XML_FILE | grep "><" | wc -l`;
#Trimming value received from database.
$validate=~ s/^\s+//;
$validate=~ s/\s+$//;

if($validate>0) {
        print "\nPlease enter space for null values in the XML file $XML_FILE\n"; 
	exit;
        }

# Parser object creation
my $xp = XML::XPath->new(filename => $XML_FILE);

# Declaring all arrays
my (@relay_groups,@group_names);

# Reading XML File

foreach my $node ($xp->find('//insert_group_details/insert_group/relay_group/text()')->get_nodelist) {
        if(sprintf(XML::XPath::XMLParser::as_string($node)) eq " ") {
                push @relay_groups, sprintf("NULL");
                }
        else {
                push @relay_groups, sprintf(XML::XPath::XMLParser::as_string($node));
                }
        #print "1: ".XML::XPath::XMLParser::as_string($node)."\n";
        }

#print "relay_groups:: @relay_groups \n\n";

foreach my $node ($xp->find('//insert_group_details/insert_group/group_name/text()')->get_nodelist) {
        if(sprintf(XML::XPath::XMLParser::as_string($node)) eq " ") {
                push @group_names, sprintf("NULL");
                }
        else {
                push @group_names, sprintf(XML::XPath::XMLParser::as_string($node));
                }
        #print "2: ".XML::XPath::XMLParser::as_string($node)."\n";
        }

#print "group_names:: @group_names \n\n";


# Preparing SQL Statement

my $sql="";
my $i=0;
my $group_key=`sqlplus -s $CONNECT_STRING <<-EOF
                set head off
                select nvl(max(group_key),0) from dim_group\;
                exit\;
                EOF`;

#Trimming value received from database.
$group_key=~ s/^\s+//;
$group_key=~ s/\s+$//;

#print "group_key=$group_key";

foreach my $var (@group_names)        {
        $group_key++;
        $sql="($group_key,";
        if($relay_groups[$i] eq "NULL") {
                $sql.="$relay_groups[$i],";
                }
        else {
                $sql.="'$relay_groups[$i]',";
                }
        if($group_names[$i] eq "NULL") {
                $sql.="$group_names[$i])";
                }
        else {
                $sql.="'$group_names[$i]')";
                }

        #print "SQL Statement [$i] = $sql \n\n";

        # Writing SQL Statement to file
        `echo "insert into dim_group values$sql\;" >>$SQL_FILE`;
	 `echo "alter table AGG_GROUP_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_GRP_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
	`echo "alter table AGG_RELAY_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_RELAY_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
	`echo "alter table AGG_HOUR_GRP_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_HOUR_GRP_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
	`echo "alter table AGG_HOUR_RLY_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_HOUR_RLY_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
	`echo "alter table AGG_DAY_GRP_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_DAY_GRP_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
	 `echo "alter table AGG_DAY_RLY_KPI_COUNTER add partition GRP_$group_key values ($group_key)
  		(SUBPARTITION P_AGG_DAY_RLY_"$group_key"_199901010000
	       VALUES LESS THAN (to_date('199901010000','yyyymmddhh24mi')));" >>$SQL_FILE`;
        $i++;
        }

# Writing SQL Statement to file
`echo "commit\;" >>$SQL_FILE`;

# Executing SQL Statement
print "\n Group Partition and Sub partition creation shall take few hours\n";

`$EXECUTION_SCRIPT $FILE_NAME`;
`rm -rf $SQL_FILE`;
`./KpiSetupSubPartitionsRelay.sh &`;
`./KpiSetupSubPartitionsGroup.sh &`;

print "Complete \n\n";

/*
<insert_group_details>
                <insert_group>
			<relay_group>Test1</relay_group>
                        <group_name>Display:Test1</group_name>
                </insert_group>
<insert_group>
                        <relay_group>Test2</relay_group>
                        <group_name>Display:Test2</group_name>
                </insert_group>
</insert_group_details>


*/
