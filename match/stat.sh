# ref:
# http://c.biancheng.net/view/1120.html
# https://blog.csdn.net/edwzhang/article/details/53332900
# 

threshold=13
if [ $2 ]
then threshold=$2
fi

round=400
if [ $1 ]
then round=$1
fi

for f in /Users/zliu/go/match/4b32f/4b32f-p300_v_*-p300-${round}.dat; do
    rt=`python /Users/zliu/github/py-ex/dat2htm/dat2stat.py $f`
    name=${rt#* vs }
    name=${name% games *}
    n=${rt%                      W *}
    percent=${n: 0-5: 5}
    p=${n: 0-5: 2}
    #if [ $p -lt $threshold ]
    if [ $p -lt $threshold ]
    then echo $name $percent $f $rt
    #./stat_dat.sh $f 150
    fi
done


