#!/bin/bash

cocoapp="/home/marco/Projects/MetaPreProcessor/tools/cocorpy/CocoRPy27-1.4.1/Coco.py"
scriptname=Syntax
logname=log.txt
cd `dirname $0`
python $cocoapp -c -a $scriptname.atg >logname

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

while ! diff ${targetname} ${targetname}- > /dev/null ; do
	cat ${targetname}- > ${targetname}
	cat ${targetname} | sed -r "s/^(\t*)   /\1\t/g" > ${targetname}-
done

cat ${targetname}- | sed -r "s/\t/    /g" > ${targetname}

cp ${targetname} ../

cp $scriptname.atg ../

for filename in ./*; do
	if [ "$filename" != "./$scriptname.atg" -a "$filename" != "./compile.sh"  -a "$filename" != "./$logname" ]; then
		rm $filename;
	fi
done
