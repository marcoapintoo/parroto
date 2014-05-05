#!/bin/bash

function patch_scanner(){
	patch=$1
	mv Scanner.py Scanner-unpatched.py
	cat Scanner-unpatched.py | sed "$patch" > Scanner.py
	rm Scanner-unpatched.py
}

function patches_in_scanner(){
	patch_scanner "s/self.ignore.add( ord(' ') )/#self.ignore.add( ord(' ') )/"
	patch_scanner "s/self.t.val = buf            self.CheckLiteral()/self.t.val = buf\n            self.CheckLiteral()/"
	patch_scanner "s/Scanner.ch/self.ch/"
	patch_scanner "s/Scanner.buffer.EOF/self.buffer.EOF/"
}

function join_files(){
	targetname=$1
	cat Parser.py | sed -r "s/from Scanner import (Token|Scanner)//g" | csplit -f temp - "/from Scanner import Position/" > /dev/null
	cat temp00 > ${targetname}
	cat Scanner.py >> ${targetname}
	cat temp01 | sed "s/from Scanner import Position//g" >> ${targetname}
	rm temp00
	rm temp01
	rm Parser.py*
	rm Scanner.py*
	rm trace.txt
}

function fix_indent(){
	targetname=$1
	fixedname=$1_
	cat ${targetname} | sed "s/lit == \"\"\"/lit == \"\\\\\"\"/g" | sed -r "s/^   /\t/g" > ${fixedname}
	while ! diff ${targetname} ${fixedname} > /dev/null ; do
		cat ${fixedname} > ${targetname}
		cat ${targetname} | sed -r "s/^(\t*)   /\1\t/g" > ${fixedname}
	done
	cat ${fixedname} | sed -r "s/\t/    /g" > ${targetname}
	rm $fixedname
}

function copy_scripts(){
	scriptname=$1
	targetname=$2
	targetpath=$3
	cp ${targetname} $targetpath
	cp ${scriptname} $targetpath
	rm ${targetname}*
	rm *.py*
}

function replace_symbols(){
	filebase=$1
	scriptname=$2
	tempscriptname=$2_
	filesymbols=$3
	cat $filebase > $scriptname
	while IFS=, read name value
	do
		mv $scriptname $tempscriptname
		value=$( echo $value | sed 's/\\/\\\\/g' )
		#echo "Changing: $name | $value"
		value=$( echo $value | sed 's/\\/\\\\/g' )
		value=$( echo $value | sed 's/"/\\"/g' )
		sed -r ':a;N;$!ba;s/(\s+'"${name}"'\s*\n\s*=\s*)([^.]*)./\1'"${value}"'./g' $tempscriptname > $scriptname
                cp $scriptname $tempscriptname
		sed -r 's/\$\$'"${name}"'/'"${value}"'/g' $tempscriptname > $scriptname
	done < $filesymbols
	rm $tempscriptname
}

function convert_syntax(){
	#
	# PARAMETERS
	#
	cocoapp="/home/marco/Projects/MetaPreProcessor/tools/cocorpy/CocoRPy27-1.4.1/Coco.py"
	filebase=$1
	scriptname=$2
	logname=log-$( basename $scriptname .atg ).txt
	targetname=$3
	filesymbols=$4
	targetpath=$5

	#
	# COMMANDS
	#
	cd `dirname $0`
	#echo replace_symbols $filebase $scriptname $filesymbols
	replace_symbols $filebase $scriptname $filesymbols
	#echo 1; read a
	python $cocoapp -a -c $scriptname > $logname
	#echo 21; read a
	patches_in_scanner
	#echo 31; read a
	join_files $targetname
	#echo 41; read a
	fix_indent $targetname
	#echo 51; read a
	copy_scripts $scriptname $targetname $targetpath
	#echo 61; read a
	echo "Compiled!"
}

convert_syntax $*
#convert_syntax base-syntax.atg syntax.atg compiler.py symbols.csv ..\

#function foo(){
#	echo $1 | sed "s/$2/--/g"
#}
#ar=\"1\"
#foo '"aa"'$ar'"aa"' "a"
#foo '"aa"'$ar'"aa"' \"1\"
