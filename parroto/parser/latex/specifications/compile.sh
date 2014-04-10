#!/bin/bash
cocoapp="/home/marco/Projects/MetaPreProcessor/tools/cocorpy/CocoRPy27-1.4.1/Coco.py"
scriptname=Syntax
cd `dirname $0`
python $cocoapp -c -a $scriptname.atg
#PATCH: Comment this instruction => self.ignore.add( ord(' ') )
mv Scanner.py Scanner-unpatched.py
cat Scanner-unpatched.py | sed  "s/self.ignore.add( ord(' ') )/#self.ignore.add( ord(' ') )/" > Scanner.py

targetname=compiler.py
#cat Parser.py > ${targetname}
cat Parser.py | sed -r "s/from Scanner import (Token|Scanner)//g" | csplit -f temp - "/from Scanner import Position/"
cat temp00 > ${targetname}
cat Scanner.py >> ${targetname}
cat temp01 | sed "s/from Scanner import Position//g" >> ${targetname}

cat ${targetname} | sed "s/lit == \"\"\"/lit == \"\\\\\"\"/g" | sed -r "s/^   /\t/g" > ${targetname}-
#cat ${targetname}- > ${targetname}
#echo cat ${targetname}- \> ${targetname}
while ! diff ${targetname} ${targetname}- > /dev/null ; do
	cat ${targetname}- > ${targetname}
	cat ${targetname} | sed -r "s/^(\t*)   /\1\t/g" > ${targetname}-
#	echo 122, ${targetname}
done

#	if ! diff ${targetname} ${targetname}- > /dev/null
#	then
#	   echo "The files match"
#	else
#	   echo "The files are different"
#	fi
cat ${targetname}- | sed -r "s/\t/    /g" > ${targetname}

cp ${targetname} ../
#cat temp.py |
#cp Parser.py ../
#cp Scanner.py ../

cp $scriptname.atg ../
#cp $scriptname.py ../
#if [[ $# == 0  ]]; then 
if [[ 1 == 0  ]]; then 
function test_parser(){
	echo 
	echo "## Content to evaluate:"
	cat $1
	echo "## Parsing:"
	python $scriptname $1
	result=Unknown
	if [[ $1 == *ok* ]]; then
	  result=OK
	elif [[ $1 == *bad* ]]; then
	  result=BAD
	fi
	echo "## Must be: $result"
	echo 
}
for file in *.test; do test_parser $file; done
fi
